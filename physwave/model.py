from pathlib import Path
import torch

def strip_prefix(state: dict[str, torch.Tensor], prefix: str) -> dict[str, torch.Tensor]:
    return {key[len(prefix):]: value for key, value in state.items() if key.startswith(prefix)}

def load_model(ckpt_path: Path, vae_ckpt_path: Path, device: torch.device):
    if not ckpt_path.is_file():
        raise FileNotFoundError(f"PhysWave checkpoint not found: {ckpt_path}")
    if not vae_ckpt_path.is_file():
        raise FileNotFoundError(f"VAE checkpoint not found: {vae_ckpt_path}")

    from stable_audio_tools.models.factory import create_model_from_config

    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=True, mmap=True)
    config = ckpt["model_config"]
    model = create_model_from_config(config)
    state = ckpt["state_dict"]

    raw = strip_prefix(state, "diffusion.")
    ema = {
        "model." + key: value
        for key, value in strip_prefix(state, "diffusion_ema.ema_model.").items()
        if not key.startswith(("initted", "step"))
    }
    load_state = {**raw, **ema}
    missing, unexpected = model.load_state_dict(load_state, strict=False)
    print(
        f"Loaded diffusion: raw={len(raw)} ema_overlay={len(ema)} "
        f"missing={len(missing)} unexpected={len(unexpected)}",
        flush=True,
    )
    if missing or unexpected:
        raise RuntimeError(f"Checkpoint mismatch: missing={missing}, unexpected={unexpected}")
    del ckpt, state, raw, ema, load_state

    vae_ckpt = torch.load(vae_ckpt_path, map_location="cpu", weights_only=True, mmap=True)
    vae_state = strip_prefix(vae_ckpt["state_dict"], "autoencoder_ema.ema_model.")
    if not vae_state:
        vae_state = strip_prefix(vae_ckpt["state_dict"], "autoencoder.")
    if not vae_state:
        raise RuntimeError(f"No VAE weights found in {vae_ckpt_path}")
    model.pretransform.load_state_dict(vae_state, strict=True)
    print(f"Loaded VAE pretransform weights: {len(vae_state)} tensors", flush=True)
    del vae_ckpt, vae_state

    model.to(device).eval().requires_grad_(False)
    return model, config
