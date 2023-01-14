from mutwo import diary_interfaces


def test_entry_path():
    assert diary_interfaces.EntryPath.component_tuple == (
        "context_identifier",
        "entry_identifier",
        "return_type",
        "name",
    )
    arg_tuple = ("test-context-identifier", "test-entry-identifier", "str", "test")
    entry_path = diary_interfaces.EntryPath(*arg_tuple)
    assert entry_path.name == "test"
    assert entry_path == diary_interfaces.constants.PATH_SEPARATOR.join(arg_tuple)
    assert not hasattr(entry_path, "code")


def test_instable_entry_path():
    assert diary_interfaces.InstableEntryPath.component_tuple == (
        "context_identifier",
        "entry_identifier",
        "return_type",
        "name",
        "comment",
        "relevance",
        "requirement_tuple",
    )
