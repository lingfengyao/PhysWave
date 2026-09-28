__all__ = ['PhysWave', 'parse_instruction']


def __getattr__(name):
    if name == 'PhysWave':
        from .inference import PhysWave
        return PhysWave
    if name == 'parse_instruction':
        from .parser import parse_instruction
        return parse_instruction
    raise AttributeError(name)
