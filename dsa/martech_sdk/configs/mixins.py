class ConfigMixins:
    @classmethod
    def describe(cls):
        descriptions = []
        for k, v in cls.__dict__.items():
            if k.startswith('__'):
                continue
            if callable(v):
                continue
            if isinstance(v, type) and hasattr(v, 'describe') and callable(v.describe):
                descriptions.append(f'{k}={{ {v.describe()} }}')
            else:
                descriptions.append(f'{k}={v}')
        return ', '.join(descriptions)