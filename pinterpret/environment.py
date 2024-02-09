from typing import Dict, Tuple

from pinterpret.obj import Object


class Environment:
    _store: Dict[str, Object]

    def __init__(self):
        self._store = {}

    def get(self, key: str) -> Tuple[Object, bool]:
        ret = self._store.get(key)
        return ret, ret is not None

    def set(self, key: str, val: Object) -> Object:
        self._store[key] = val
        return val
