from mutwo import diary_interfaces


def test_context():
    class NewContext(diary_interfaces.Context, name="new", version=0):
        ...

    assert NewContext
    assert NewContext.name == "new"
    assert NewContext.version == 0
    assert NewContext.identifier == diary_interfaces.ContextIdentifier("new", 0)
