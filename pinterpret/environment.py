from typing import Dict, Tuple

from pinterpret.common import Object


class Environment:
    _store: Dict[str, Object]
    outer: "Environment"

    def __init__(self, outer=None):
        self._store = {}
        self.outer = outer

    def get(self, key: str) -> Tuple[Object, bool]:
        ret = self._store.get(key)
        if ret is None and self.outer is not None:
            ret = self.outer.get(key)
        return ret, ret is not None

    def set(self, key: str, val: Object) -> Object:
        self._store[key] = val
        return val
