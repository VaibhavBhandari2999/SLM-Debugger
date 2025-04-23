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
    Register a TagDict with a specific key and ensure it is added to the serializer's tags and order.
    
    This function tests the registration of a TagDict with a specific key in a JSON serializer. It ensures that a KeyError is raised if the key already exists, and that the TagDict can be registered with the force=True option.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    KeyError: If the key already exists in the serializer's tags and force is not set to True.
    
    Example
    """

    class TagDict(JSONTag):
        key = " d"

    s = TaggedJSONSerializer()
    pytest.raises(KeyError, s.register, TagDict)
    s.register(TagDict, force=True, index=0)
    assert isinstance(s.tags[" d"], TagDict)
    assert isinstance(s.order[0], TagDict)


def test_custom_tag():
    """
    Test custom JSON tag for serialization and deserialization of custom objects.
    
    This function registers a custom JSON tag for a custom class `Foo` and tests its functionality. The custom tag is used to serialize and deserialize instances of `Foo` to and from JSON.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Concepts:
    - `Foo`: A custom class with a `data` attribute.
    - `TagFoo`: A custom JSON tag class for `Foo`.
    - `check`: A
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
    class Tag1(JSONTag):
        key = " 1"

    class Tag2(JSONTag):
        key = " 2"

    s = TaggedJSONSerializer()

    s.register(Tag1, index=-1)
    assert isinstance(s.order[-2], Tag1)

    s.register(Tag2, index=None)
    assert isinstance(s.order[-1], Tag2)
