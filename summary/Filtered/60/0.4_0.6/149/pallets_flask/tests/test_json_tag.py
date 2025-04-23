from datetime import datetime
from datetime import timezone
from uuid import uuid4

import pytest
from markupsafe import Markup

from flask.json.tag import JSONTag
from flask.json.tag import TaggedJSONSerializer


@pytest.mark.parametrize(
    "data",
    (
        {" t": (1, 2, 3)},
        {" t__": b"a"},
        {" di": " di"},
        {"x": (1, 2, 3), "y": 4},
        (1, 2, 3),
        [(1, 2, 3)],
        b"\xff",
        Markup("<html>"),
        uuid4(),
        datetime.now(tz=timezone.utc).replace(microsecond=0),
    ),
)
def test_dump_load_unchanged(data):
    s = TaggedJSONSerializer()
    assert s.loads(s.dumps(data)) == data


def test_duplicate_tag():
    class TagDict(JSONTag):
        key = " d"

    s = TaggedJSONSerializer()
    pytest.raises(KeyError, s.register, TagDict)
    s.register(TagDict, force=True, index=0)
    assert isinstance(s.tags[" d"], TagDict)
    assert isinstance(s.order[0], TagDict)


def test_custom_tag():
    """
    Tests the functionality of a custom JSON tag for a `Foo` class. The `Foo` class is initialized with a `data` parameter. A custom JSON tag, `TagFoo`, is defined to handle serialization and deserialization of `Foo` objects. The `TagFoo` class includes methods to check if a value is an instance of `Foo`, to convert a `Foo` object to a JSON-compatible format, and to convert a JSON-compatible format back to a `Foo` object.
    """

    class Foo:  # noqa: B903, for Python2 compatibility
        def __init__(self, data):
            self.data = data

    class TagFoo(JSONTag):
        __slots__ = ()
        key = " f"

        def check(self, value):
            return isinstance(value, Foo)

        def to_json(self, value):
            return self.serializer.tag(value.data)

        def to_python(self, value):
            return Foo(value)

    s = TaggedJSONSerializer()
    s.register(TagFoo)
    assert s.loads(s.dumps(Foo("bar"))).data == "bar"


def test_tag_interface():
    t = JSONTag(None)
    pytest.raises(NotImplementedError, t.check, None)
    pytest.raises(NotImplementedError, t.to_json, None)
    pytest.raises(NotImplementedError, t.to_python, None)


def test_tag_order():
    """
    Tests the order in which tags are registered in a JSON serializer.
    
    This function checks the order of tags in a JSON serializer when they are registered with different indices. It registers two custom JSON tags, Tag1 and Tag2, with specific indices and verifies that the tags are added to the serializer's order list in the correct sequence.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - Registers Tag1 and Tag2 with the JSON serializer.
    - Tag1 is registered with index
    """

    class Tag1(JSONTag):
        key = " 1"

    class Tag2(JSONTag):
        key = " 2"

    s = TaggedJSONSerializer()

    s.register(Tag1, index=-1)
    assert isinstance(s.order[-2], Tag1)

    s.register(Tag2, index=None)
    assert isinstance(s.order[-1], Tag2)
