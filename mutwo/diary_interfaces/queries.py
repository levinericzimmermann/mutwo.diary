import functools
import re
import typing

from mutwo import diary_interfaces


__all__ = ("qwrap",)


class qwrap(object):
    """Create wrapper of database to query database"""

    def __init__(
        self, mapping: typing.Mapping[diary_interfaces.Path, diary_interfaces.Entry]
    ):
        self._mapping = mapping

    def __str__(self) -> str:
        return f"wrapped({str(self._mapping)})"

    def __repr__(self) -> str:
        return f"wrapped({repr(self._mapping)})"

    def __getitem__(self, key: diary_interfaces.Path) -> diary_interfaces.Entry:
        return self._mapping[key]

    @functools.cached_property
    def path_tuple(self) -> tuple[diary_interfaces.Path, ...]:
        return tuple(self._mapping.keys())

    def rquery(
        self,
        full: typing.Optional[str] = None,
        raise_exception: bool = False,
        **kwargs: str,
    ) -> typing.Generator:
        """Regex based query

        Fast but limited.

        You can pass any

            <path_component> = <regex>

        assignment to rquery method.
        """

        pattern_dict = {name: re.compile(pattern) for name, pattern in kwargs.items()}

        def query_base(path: diary_interfaces.Path) -> bool:
            for key, pattern in pattern_dict.items():
                try:
                    value = getattr(path, key)
                except AttributeError:
                    if raise_exception:
                        raise
                else:
                    if not bool(pattern.match(value)):
                        return False
            return True

        if full is not None:
            full = re.compile(full)

            def query_full(path: diary_interfaces.Path) -> bool:
                return bool(full.match(path))

            def query(path: diary_interfaces.Path) -> bool:
                return query_full(path) and query_base(path)

        else:
            query = query_base

        for path in self.path_tuple:
            if query(path):
                yield self[path]

    def fquery(
        self, function: typing.Callable[[diary_interfaces.Entry], bool]
    ) -> typing.Generator:
        """Function based query

        Slow but rich.
        """
        for entry in self._mapping.values():
            if function(entry):
                yield entry
