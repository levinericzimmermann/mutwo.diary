import dataclasses
import functools
import hashlib
import typing

import persistent

__all__ = (
    "ContextIdentifier",
    "Context",
    "EmptyContext",
)


@functools.total_ordering
class ContextIdentifier(persistent.Persistent):
    def __init__(self, name: str, version: int):
        self._identifier = f"{name}_{version}"
        self._name = name
        self._version = version

    @functools.cached_property
    def hash(self) -> str:
        return hashlib.md5(self._identifier.encode()).hexdigest()

    def __hash__(self) -> int:
        return hash((self.hash,))

    def __lt__(self, other: typing.Any) -> bool:
        return str(self) < str(other)

    def __eq__(self, other: typing.Any) -> bool:
        try:
            return str(self) == str(other) and self.hash == other.hash
        except AttributeError:
            return False

    def __str__(self) -> str:
        return self._identifier

    def __repr__(self) -> str:
        return self._identifier

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return str(self._version)


@dataclasses.dataclass(frozen=True)
class Context(object):
    def __init_subclass__(
        cls,
        *args,
        name: str = "",
        version: int = 0,
        **kwargs,
    ):
        super().__init_subclass__(*args, **kwargs)
        cls.name = name
        cls.version = version
        cls.identifier = ContextIdentifier(cls.name, cls.version)


class EmptyContext(Context):
    ...
