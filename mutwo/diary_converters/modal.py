import typing

from mutwo import clock_converters
from mutwo import clock_events
from mutwo import core_converters
from mutwo import core_events
from mutwo import diary_converters
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
                # BBB: In old mutwo.clocks version ModalEvent
                # has not 'energy' attribute.
                energy=getattr(modal_event, 'energy', 0),
            )
            context_list.append(context)
        return tuple(context_list)


class Modal0SequentialEventToEventPlacementTuple(
    diary_converters.ContextTupleToEventPlacementTuple,
    clock_converters.Modal0SequentialEventToEventPlacementTuple,
):
    def __init__(
        self,
        *args,
        orchestration: music_parameters.Orchestration,
        add_mod1: bool = True,  # Turn off modal1 mode if not needed for better performance
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._orchestration = orchestration

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

    def convert(
        self, modal_0_sequential_event_to_convert
    ) -> tuple[timeline_interfaces.EventPlacement, ...]:
        mod0seq = modal_0_sequential_event_to_convert

        context_tuple = self._modal0context(mod0seq)

        if self._add_mod1:
            mod1seq = self._mod0seq2mod1seq(mod0seq)
            context_tuple += self._modal1context(mod1seq)

        return super().convert(context_tuple)
