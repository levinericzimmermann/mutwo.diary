import typing

import numpy as np

from mutwo import clock_converters
from mutwo import clock_events
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities
from mutwo import diary_interfaces
from mutwo import music_parameters
from mutwo import timeline_interfaces

__all__ = (
    "ModalSequentialEventToModalContextTuple",
    "Modal0SequentialEventToEventPlacementTuple",
)


class ModalSequentialEventToModalContextTuple(core_converters.abc.Converter):
    def __init__(
        self,
        modal_context_class: typing.Type[
            diary_interfaces.CommonContext
        ] = diary_interfaces.ModalContext0,
    ):
        self._modal_context_class = modal_context_class

    def convert(
        self,
        modal_sequential_event_to_convert: core_events.SequentialEvent[
            core_events.SimpleEvent | clock_events.ModalEvent0
        ],
        orchestration: music_parameters.Orchestration,
    ) -> tuple[timeline_interfaces.EventPlacement, ...]:
        context_list = []
        (
            absolute_time_tuple,
            duration,
        ) = modal_sequential_event_to_convert._absolute_time_tuple_and_duration
        for start, end, modal_event in zip(
            absolute_time_tuple,
            absolute_time_tuple[1:] + (duration,),
            modal_sequential_event_to_convert,
        ):
            context = self._modal_context_class(
                start=start,
                end=end,
                modal_event=modal_event,
                orchestration=orchestration,
            )
            context_list.append(context)
        return tuple(context_list)


class Modal0SequentialEventToEventPlacementTuple(
    clock_converters.Modal0SequentialEventToEventPlacementTuple
):
    def __init__(
        self,
        orchestration: music_parameters.Orchestration,
        random_seed: int = 10,
        add_mod1: bool = True,  # Turn off modal1 mode if not needed for better performance
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

        self._orchestration = orchestration
        self._rquery_kwargs = rquery_kwargs
        self._random = np.random.default_rng(random_seed)

        self._modal0context = lambda seq: ModalSequentialEventToModalContextTuple(
            diary_interfaces.ModalContext0
        ).convert(seq, self._orchestration)
        self._modal1context = lambda seq: ModalSequentialEventToModalContextTuple(
            diary_interfaces.ModalContext1
        ).convert(seq, self._orchestration)

        self._mod0seq2mod1seq = (
            clock_converters.Modal0SequentialEventToModal1SequentialEvent().convert
        )
        self._add_mod1 = add_mod1

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

    def convert(
        self,
        modal_0_sequential_event_to_convert,
    ) -> tuple[timeline_interfaces.EventPlacement, ...]:
        mod0seq = modal_0_sequential_event_to_convert

        context_tuple = self._modal0context(mod0seq)

        if self._add_mod1:
            mod1seq = self._mod0seq2mod1seq(mod0seq)
            context_tuple += self._modal1context(mod1seq)

        event_placement_list = []
        context_identifier_to_entry_tuple = {}
        print("\n\n")
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
                print(f"Picked '{picked_entry.name}'.")
                if (event_placement := picked_entry(context)) is not None:
                    event_placement_list.append(event_placement)
            else:
                print("No entry picked.")
        return tuple(event_placement_list)
