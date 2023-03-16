from BTrees.OOBTree import OOBTree
import transaction

from mutwo import diary_interfaces
from mutwo import diary_utilities


__all__ = (
    "fetch_entry_tree",
    "fetch_wrapped_entry_tree",
    "execute",
)


def fetch_entry_tree() -> OOBTree:
    try:
        return diary_interfaces.configurations.ROOT.entry_tree
    except AttributeError as e:
        if diary_interfaces.configurations.ROOT is not None:
            diary_interfaces.configurations.ROOT.entry_tree = OOBTree()
            transaction.commit()
        else:
            raise e
        return fetch_entry_tree()


def fetch_wrapped_entry_tree() -> diary_interfaces.qwrap:
    return diary_interfaces.qwrap(fetch_entry_tree())


def execute(name: str, code: str, function_name: str, *args, **kwargs):
    exec(code, locals())
    try:
        function = locals()[function_name]
    # Imitate builtin error message
    except KeyError:
        raise NameError(f"name '{function_name}' is not defined")
    try:
        return function(*args, **kwargs)
    except Exception as e:
        raise diary_utilities.ExecutionError(
            f"Raised error when executing {name} with "
            f"arguments '{args}' and '{kwargs}':\n{e}"
        )
