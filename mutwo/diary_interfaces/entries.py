"""Entries represent small musical fragments to be reused.

"""

from __future__ import annotations

import abc
import datetime
import functools
import hashlib
import typing

import numpy as np
import persistent
import transaction

from mutwo import common_generators
from mutwo import diary_interfaces


__all__ = ("Entry", "DynamicEntry")

T = typing.TypeVar("T")


class Entry(persistent.Persistent):
    def __init__(
        self,
        # Stable path
        name: str,
        context_identifier: diary_interfaces.ContextIdentifier,
        return_type: typing.Type,
        # Instable path
        comment: str = "",
        relevance: int = 0,
        abbreviation_to_path_dict: AbbreviationToPathDict = {},  # Specify requirements
        # Tweak behaviour of auto-commit.
        force_commit: bool = False,
        skip_check: bool = True,  # Set to True for faster load from database.
        # Auto created by Entry.
        _creation_date: typing.Optional[datetime.datetime] = None,
        _modification_date: typing.Optional[datetime.datetime] = None,
    ):
        self._name = name
        self._context_identifier = context_identifier
        self._return_type = return_type
        self._comment = comment
        self._relevance = relevance
        self._abbreviation_to_path_dict = abbreviation_to_path_dict
        self._creation_date = _creation_date
        self._modification_date = _modification_date
        if (not skip_check) and (not force_commit):
            try:
                old_self = self._fetch_self_from_db()
            except KeyError:
                force_commit = True
                self._creation_date = datetime.datetime.utcnow()
            else:
                self._creation_date = old_self.creation_date
                self._modification_date = old_self.modification_date
        if force_commit or self.hash != old_self.hash:
            self._modification_date = datetime.datetime.utcnow()
            self.commit()

        # Sanity check
        assert (
            self.path not in self.abbreviation_to_path_dict.items()
        ), "Can't call itself"

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.identifier}({self.path})"

    @property
    def name(self) -> str:
        return self._name

    @property
    def context_identifier(self) -> diary_interfaces.ContextIdentifier:
        return self._context_identifier

    @classmethod
    @property
    def identifier(cls) -> str:
        return cls.__name__

    @property
    def return_type(self) -> typing.Type:
        return self._return_type

    @property
    def abbreviation_to_path_dict(self) -> AbbreviationToPathDict:
        return self._abbreviation_to_path_dict

    @property
    def relevance(self) -> int:
        return self._relevance

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def creation_date(self) -> datetime.datetime:
        if self._creation_date is None:
            self._creation_date = self._fetch_self_from_db()._creation_date
        return self._creation_date

    @property
    def modification_date(self) -> datetime.datetime:
        if self._modification_date is None:
            self._modification_date = self._fetch_self_from_db()._modification_date
        return self._modification_date

    @functools.cached_property
    def path_arg_tuple(self) -> tuple[str, ...]:
        return (
            str(self.context_identifier),
            self.identifier,
            self.return_type.__name__,
            self.name,
        )

    @functools.cached_property
    def instable_path_arg_tuple(self) -> tuple[str, ...]:
        return self.path_arg_tuple + (
            hashlib.md5(self.comment.encode()).hexdigest(),
            str(self.relevance),
            ";".join(
                f"{abbreviation}={path}"
                for abbreviation, path in self.abbreviation_to_path_dict.items()
            ),
        )

    @functools.cached_property
    def path(self) -> diary_interfaces.EntryPath:
        return diary_interfaces.EntryPath(*self.path_arg_tuple)

    @functools.cached_property
    def instable_path(self) -> diary_interfaces.InstableEntryPath:
        return diary_interfaces.InstableEntryPath(*self.instable_path_arg_tuple)

    @functools.cached_property
    def hash(self) -> str:
        return hashlib.md5(self.instable_path.encode()).hexdigest()

    @functools.cached_property
    def abbreviation_to_entry_dict(self) -> AbbreviationToEntryDict:
        root = diary_interfaces.fetch_entry_tree()
        return {
            abbreviation: root[path]
            for abbreviation, path in self.abbreviation_to_path_dict.items()
        }

    def _fetch_self_from_db(self):
        return diary_interfaces.fetch_entry_tree()[self.path]

    def commit(self):
        entry_tree = diary_interfaces.fetch_entry_tree()
        entry_tree[self.path] = self
        transaction.commit()

    def _is_supported(
        self,
        context: diary_interfaces.Context,
        **kwargs,
    ) -> bool:
        return True

    def is_supported(self, context: diary_interfaces.Context, **kwargs):
        return self._is_supported(
            context, **dict(self.abbreviation_to_entry_dict, **kwargs)
        )

    def __call__(self, context: diary_interfaces.Context, **kwargs):
        id_self, id_passed = self._context_identifier, context.identifier
        assert id_self == id_passed, f"Expected {id_self}, got {id_passed}"
        assert self.is_supported(context, **kwargs), "Not supported!"
        keyword_argument_dict = dict(self.abbreviation_to_entry_dict)
        keyword_argument_dict.update(kwargs)
        object_ = self._context_to_data(context, **keyword_argument_dict)
        return object_

    @abc.abstractmethod
    def _context_to_data(
        self, context: diary_interfaces.Context, **kwargs
    ) -> typing.Any:
        ...

    def __hash__(self) -> int:
        return hash((self.hash,))


EntryAbbreviation: typing.TypeAlias = str
"""User defined abbreviation for a specific entry.

The abbreviation will be passed to the context_to_data and
is_supported functions.
"""

AbbreviationToEntryDict: typing.TypeAlias = dict[EntryAbbreviation, Entry]
AbbreviationToPathDict: typing.TypeAlias = dict[
    EntryAbbreviation, diary_interfaces.Path
]


class DynamicEntry(Entry):
    def __init__(
        self,
        *args,
        # Added to instable path.
        code: str,
        function_name: typing.Optional[str] = None,
        random_seed: int = 100,
        **kwargs,
    ):
        self._code = code
        self._function_name = (
            function_name or diary_interfaces.configurations.DEFAULT_FUNCTION_NAME
        )
        self._random_seed = random_seed
        super().__init__(*args, **kwargs)

    @classmethod
    def from_file(cls, *args, file_path: str, **kwargs) -> DynamicEntry:
        with open(file_path, "r") as file:
            code = file.read()
        return cls(*args, code=code, **kwargs)

    @property
    def code(self):
        return self._code

    @property
    def function_name(self):
        return self._function_name

    @property
    def random_seed(self):
        return self._random_seed

    @functools.cached_property
    def random(self) -> np.random.default_rng:
        return np.random.default_rng(self._random_seed)

    @functools.cached_property
    def activity_level(self) -> common_generators.ActivityLevel:
        return common_generators.ActivityLevel()

    @functools.cached_property
    def instable_path_arg_tuple(self) -> tuple[str, ...]:
        return super().instable_path_arg_tuple + (
            self.function_name,
            hashlib.md5(self.code.encode()).hexdigest(),
            str(self.random_seed),
        )

    @functools.cached_property
    def instable_path(self) -> diary_interfaces.InstableDynamicEntryPath:
        return diary_interfaces.InstableDynamicEntryPath(*self.instable_path_arg_tuple)

    def _is_supported(
        self,
        context: diary_interfaces.Context,
        **kwargs,
    ) -> bool:
        try:
            return diary_interfaces.execute(
                self.name, self._code, "is_supported", context, **kwargs
            )
        except NameError:
            return super()._is_supported(context, **kwargs)

    def _context_to_data(
        self, context: diary_interfaces.Context, **kwargs
    ) -> typing.Any:
        # Don't specify them hard coded, due to the following
        # reason: If we call an entry from a different entry,
        # we may want to send the 'random' and 'activity_level'
        # of the entry which calls the other entry. This is
        # impossible if we hard code them (because then 'random'
        # would be provided twice).
        kwargs.setdefault("random", self.random)
        kwargs.setdefault("activity_level", self.activity_level)
        try:
            return diary_interfaces.execute(
                self.name,
                self._code,
                self._function_name,
                context,
                **kwargs,
            )
        except Exception:
            print(f"Raised in '{self.name}'!")
            raise
