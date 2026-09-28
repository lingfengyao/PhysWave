from pathlib import Path

import numpy as np
import torch

from .model import load_model
from .waypoints import build_features


ROOT = Path(__file__).resolve().parents[1]


def prepare_condition(caption, waypoints):
    if not isinstance(caption, str) or not caption.strip():
        raise ValueError('caption must be a non-empty string')
    wp = np.asarray(waypoints, dtype=np.float32)
    if wp.ndim != 2 or wp.shape[1] != 4 or len(wp) < 2:
        raise ValueError('waypoints must contain at least two [time, azimuth, elevation, distance] rows')
    if not np.isfinite(wp).all():
        raise ValueError('waypoints must be finite')
    if np.any(np.diff(wp[:, 0]) <= 0) or wp[0, 0] != 0 or wp[-1, 0] != 10:
        raise ValueError('waypoint times must strictly increase from 0 to 10 seconds')
    if np.any(np.abs(wp[:, 2]) > 90) or np.any(wp[:, 3] < 0.5):
        raise ValueError('elevation must be in [-90, 90] and distance must be at least 0.5 metres')
    return {
        'prompt': caption.strip(), 'prompt_text': caption.strip(),
        'seconds_start': 0.0, 'seconds_total': 10.0,
        'waypoint_features': build_features(wp, wp[0, 1], wp[0, 2], wp[-1, 1], wp[-1, 2], 10.0).tolist(),
    }


class PhysWave:
    def __init__(self, checkpoint=None, vae_checkpoint=None, device=None):
        self.device = torch.device(device or ('cuda' if torch.cuda.is_available() else 'cpu'))
        self.model, self.config = load_model(
            Path(checkpoint or ROOT / 'checkpoints/physwave.ckpt'),
            Path(vae_checkpoint or ROOT / 'checkpoints/vae.ckpt'),
            self.device,
        )
        self.sample_rate = int(self.config['sample_rate'])

    @torch.no_grad()
    def generate(self, caption, waypoints, *, seed=0, steps=100, cfg_scale=6.0):
        from stable_audio_tools.inference.sampling import sample

        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
            raise ValueError('steps must be a positive integer')
        if not np.isfinite(cfg_scale) or cfg_scale < 0:
            raise ValueError('cfg_scale must be finite and non-negative')
        condition = prepare_condition(caption, waypoints)
        model = self.model
        size = int(self.config['sample_size']) // model.pretransform.downsampling_ratio
        dtype = next(model.model.parameters()).dtype
        torch.manual_seed(seed)
        noise = torch.randn([1, model.io_channels, size], device=self.device).to(dtype)
        with torch.amp.autocast(device_type=self.device.type, enabled=False):
            inputs = model.get_conditioning_inputs(model.conditioner([condition], self.device))
            inputs = {k: v.to(dtype) if torch.is_tensor(v) else v for k, v in inputs.items()}
            latents = sample(model.model, noise, steps, 0, **inputs,
                             cfg_scale=cfg_scale, dist_shift=model.dist_shift, batch_cfg=True)
            audio = model.pretransform.decode(latents)[0].float().cpu().numpy().T
        if not np.isfinite(audio).all():
            raise RuntimeError('Generated audio contains non-finite samples')
        peak = float(np.abs(audio).max())
        if peak > 1.0:
            audio *= 0.98 / peak
        return audio

    def generate_instruction(self, instruction, *, gemini_model, provider='openrouter', **kwargs):
        from .parser import parse_instruction

        condition = parse_instruction(instruction, model=gemini_model, provider=provider)
        audio = self.generate(condition['caption'], condition['waypoints'], **kwargs)
        return audio, condition
