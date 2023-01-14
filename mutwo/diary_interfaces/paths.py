import dataclasses

from mutwo import diary_interfaces

__all__ = ("Path", "EntryPath", "InstableEntryPath", "InstableDynamicEntryPath")


@dataclasses.dataclass(frozen=True)
class Path(str):
    @classmethod
    @property
    def component_tuple(cls) -> tuple[str, ...]:
        return tuple(cls.__dataclass_fields__.keys())

    def __new__(cls, *args):
        path_string = diary_interfaces.constants.PATH_SEPARATOR.join(args)
        return str.__new__(cls, path_string)


@dataclasses.dataclass(frozen=True)
class EntryPath(Path):
    context_identifier: str
    entry_identifier: str
    return_type: str
    name: str


@dataclasses.dataclass(frozen=True)
class InstableEntryPath(EntryPath):
    comment: str
    relevance: str
    requirement_tuple: str


@dataclasses.dataclass(frozen=True)
class InstableDynamicEntryPath(InstableEntryPath):
    function_name: str
    code: str
    random_seed: str
