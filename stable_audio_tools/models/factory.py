import json


def create_model_from_config(config):
    if config.get('model_type') == 'diffusion_cond':
        from .diffusion import create_diffusion_cond_from_config
        return create_diffusion_cond_from_config(config)
    if config.get('model_type') == 'autoencoder':
        from .autoencoders import create_autoencoder_from_config
        return create_autoencoder_from_config(config)
    raise ValueError('This runtime supports only the released PhysWave DiT and VAE')


def create_model_from_config_path(path):
    with open(path) as file:
        return create_model_from_config(json.load(file))


def create_pretransform_from_config(config, sample_rate):
    if config.get('type') != 'autoencoder':
        raise ValueError('PhysWave requires an autoencoder pretransform')
    from .autoencoders import create_autoencoder_from_config
    from .pretransforms import AutoencoderPretransform
    model = create_autoencoder_from_config({'sample_rate': sample_rate, 'model': config['config']})
    transform = AutoencoderPretransform(
        model, scale=config.get('scale', 1.0), model_half=config.get('model_half', False),
        iterate_batch=config.get('iterate_batch', False), chunked=config.get('chunked', False),
    )
    transform.enable_grad = config.get('enable_grad', False)
    transform.eval().requires_grad_(transform.enable_grad)
    return transform


def create_bottleneck_from_config(config):
    if config.get('type') != 'vae':
        raise ValueError('PhysWave requires a VAE bottleneck')
    from .bottleneck import VAEBottleneck
    bottleneck = VAEBottleneck()
    bottleneck.requires_grad_(config.get('requires_grad', True))
    return bottleneck
