import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='PhysWave text and trajectory to WXYZ audio')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--condition', type=Path, help='JSON with caption and waypoints')
    source.add_argument('--instruction')
    parser.add_argument('--provider', choices=['openrouter', 'google'], default='openrouter')
    parser.add_argument('--gemini-model', default='google/gemini-2.5-flash-lite')
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--vae-checkpoint', type=Path)
    parser.add_argument('--device', choices=['cpu', 'cuda'])
    parser.add_argument('--steps', type=int, default=100)
    parser.add_argument('--cfg-scale', type=float, default=6.0)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--output', type=Path, default=Path('output.wav'))
    parser.add_argument('--parse-only', action='store_true')
    args = parser.parse_args()
    if args.instruction:
        from .parser import parse_instruction
        condition = parse_instruction(args.instruction, model=args.gemini_model, provider=args.provider)
    else:
        condition = json.loads(args.condition.read_text())
    if args.parse_only:
        print(json.dumps(condition, ensure_ascii=False, indent=2))
        return
    from .inference import PhysWave
    import soundfile as sf
    generator = PhysWave(args.checkpoint, args.vae_checkpoint, args.device)
    audio = generator.generate(condition['caption'], condition['waypoints'],
                               seed=args.seed, steps=args.steps, cfg_scale=args.cfg_scale)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(args.output, audio, generator.sample_rate, subtype='FLOAT')
    args.output.with_suffix('.json').write_text(json.dumps({
        **condition, 'seed': args.seed, 'steps': args.steps, 'cfg_scale': args.cfg_scale,
        'sample_rate': generator.sample_rate, 'samples': len(audio),
        'channel_order': 'WXYZ', 'azimuth_positive': 'right',
    }, ensure_ascii=False, indent=2) + '\n')
    print(args.output)


if __name__ == '__main__':
    main()
