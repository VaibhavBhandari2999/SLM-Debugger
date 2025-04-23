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
    """
    Register a TagDict with a JSON serializer, ensuring that duplicate keys are handled correctly.
    
    This function tests the registration of a custom TagDict with a JSON serializer. It ensures that a KeyError is raised when attempting to register a duplicate key without the force parameter. If the force parameter is set to True, the function should successfully register the TagDict and ensure it is included in the serializer's tags and order.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    KeyError: If the function is
    """

    class TagDict(JSONTag):
        key = " d"

    s = TaggedJSONSerializer()
    pytest.raises(KeyError, s.register, TagDict)
    s.register(TagDict, force=True, index=0)
    assert isinstance(s.tags[" d"], TagDict)
    assert isinstance(s.order[0], TagDict)


def test_custom_tag():
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
    """
    Tests the behavior of a JSONTag object by asserting that it raises a NotImplementedError for the check, to_json, and to_python methods when called with no arguments.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    NotImplementedError: If any of the check, to_json, or to_python methods are called without arguments.
    """

    t = JSONTag(None)
    pytest.raises(NotImplementedError, t.check, None)
    pytest.raises(NotImplementedError, t.to_json, None)
    pytest.raises(NotImplementedError, t.to_python, None)


def test_tag_order():
    class Tag1(JSONTag):
        key = " 1"

    class Tag2(JSONTag):
        key = " 2"

    s = TaggedJSONSerializer()

    s.register(Tag1, index=-1)
    assert isinstance(s.order[-2], Tag1)

    s.register(Tag2, index=None)
    assert isinstance(s.order[-1], Tag2)
