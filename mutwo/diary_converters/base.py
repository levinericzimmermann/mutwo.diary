import logging
import typing

import numpy as np

from mutwo import core_converters
from mutwo import core_utilities
from mutwo import diary_interfaces
from mutwo import timeline_interfaces

__all__ = (
    "ContextTupleToEventPlacementTuple",
)


class ContextTupleToEventPlacementTuple(core_converters.abc.Converter):
    def __init__(
        self,
        random_seed: int = 10,
        **rquery_kwargs,
    ):
        rquery_kwargs.setdefault(
            "entry_identifier",
            "|".join(
                tuple(
                    map(
                        lambda entry_class: entry_class.identifier,
                        (
                            diary_interfaces.Entry,
                            diary_interfaces.DynamicEntry,
                        ),
                    )
                )
            ),
        )
        rquery_kwargs.setdefault(
            "return_type", timeline_interfaces.EventPlacement.__name__
        )

        self._rquery_kwargs = rquery_kwargs
        self._random = np.random.default_rng(random_seed)
        self._logger = logging.getLogger(f"{__name__}.{type(self).__name__}")

    def convert(
        self, context_tuple: tuple[diary_interfaces.Context, ...]
    ) -> tuple[timeline_interfaces.EventPlacement, ...]:

        event_placement_list = []
        context_identifier_to_entry_tuple = {}

        self._logger.debug("<<<<< find entries")

        for context in context_tuple:
            try:
                entry_tuple = context_identifier_to_entry_tuple[context.identifier]
            except KeyError:
                context_identifier_to_entry_tuple[
                    context.identifier
                ] = entry_tuple = self._context_to_entry_tuple(context)
            entry_tuple = tuple(
                filter(lambda entry: entry.is_supported(context), entry_tuple)
            )
            entry_relevance_tuple = tuple(e.relevance for e in entry_tuple)
            if picked_entry := self._pick_entry(entry_tuple, entry_relevance_tuple):
                self._logger.debug(f"Picked '{picked_entry.name}'.")
                if (event_placement := picked_entry(context)) is not None:
                    event_placement_list.append(event_placement)
            else:
                self._logger.debug("No entry picked.")

        self._logger.debug"finished >>>>>>>")

        return tuple(event_placement_list)

    def _context_to_entry_tuple(
        self, context: diary_interfaces.Context
    ) -> tuple[diary_interfaces.Entry, ...]:
        return tuple(
            diary_interfaces.fetch_wrapped_entry_tree().rquery(
                context_identifier=str(context.identifier), **self._rquery_kwargs
            )
        )

    def _pick_entry(
        self,
        entry_tuple: tuple[diary_interfaces.Entry, ...],
        entry_relevance_tuple: tuple[float, ...],
    ) -> typing.Optional[diary_interfaces.Entry]:
        if entry_tuple:
            return self._random.choice(
                entry_tuple,
                p=core_utilities.scale_sequence_to_sum(entry_relevance_tuple, 1),
            )
