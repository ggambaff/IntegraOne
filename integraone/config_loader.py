import json

class Config:
    _config = {}

    @classmethod
    def load(cls, path):
        with open(path, 'r') as f:
            cls._config = json.load(f)

    @classmethod
    def get(cls, key, default=None):
        return cls._config.get(key, default)

    @classmethod
    def all(cls):
        return cls._config