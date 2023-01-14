import dataclasses

import pytest

from mutwo import diary_interfaces


@dataclasses.dataclass(frozen=True)
class TContext(diary_interfaces.Context, name="test", version=0):
    data: int


def get_entry_tree_values():
    with diary_interfaces.open():
        return diary_interfaces.fetch_entry_tree().values()


@pytest.fixture
def entry_tree_fixture(tmpdir):
    storage_path = f"{tmpdir}/test.fs"
    default_storage_path = diary_interfaces.configurations.DEFAULT_STORAGE_PATH
    diary_interfaces.configurations.DEFAULT_STORAGE_PATH = storage_path
    get_entry_tree_values()
    yield None
    diary_interfaces.configurations.DEFAULT_STORAGE_PATH = default_storage_path


def test_persistent_entry(entry_tree_fixture):
    """Ensure new entry is commited to db
    + reinitialsing object doesn't create new entry in db
    """

    def initialise_entry(code: str = "def main(context): 100"):
        with diary_interfaces.open():
            diary_interfaces.DynamicEntry(
                "test", TContext.identifier, int, code=code, skip_check=False
            )

    assert len(get_entry_tree_values()) == 0
    initialise_entry()
    assert len(get_entry_tree_values()) == 1
    initialise_entry()
    assert len(get_entry_tree_values()) == 1


def test_apply_change_to_entry(entry_tree_fixture):
    ...
