import typing

from ZODB.FileStorage import FileStorage
from ZODB.interfaces import IStorage, IConnection, IDatabase

STORAGE: typing.Optional[IStorage] = None
DATABASE: typing.Optional[IDatabase] = None
CONNECTION: typing.Optional[IConnection] = None

DEFAULT_STORAGE_PATH: str = "diary.fs"

DEFAULT_FUNCTION_NAME: str = "main"


def GET_STORAGE(storage_path: typing.Optional[str] = None) -> FileStorage:
    return FileStorage(storage_path or DEFAULT_STORAGE_PATH)
