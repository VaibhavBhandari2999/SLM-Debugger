from datetime import datetime
from datetime import timezone
from uuid import uuid4

import pytest

from flask import Markup
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
    Tests the functionality of a custom JSON tag for a class `Foo`. The function registers a custom tag `TagFoo` with a JSON serializer. This tag is designed to handle instances of `Foo` by serializing their `data` attribute and deserializing back to a `Foo` instance. The test ensures that the custom tag works correctly by serializing and deserializing an instance of `Foo` and verifying that the `data` attribute is preserved.
    
    Key Parameters:
    - None
    
    Key
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
    
    This function checks the order of tags in a JSON serializer when they are registered with different indices. Specifically, it:
    - Registers `Tag1` with an index of -1, which should place it second to last in the order.
    - Registers `Tag2` with an index of None, which should place it last in the order.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - `Tag1` and
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
