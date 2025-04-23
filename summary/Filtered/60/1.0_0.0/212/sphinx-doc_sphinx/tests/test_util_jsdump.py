from sphinx.util.jsdump import dumps, loads


def test_jsdump():
    """
    Test the JavaScript object serialization and deserialization functions.
    
    This function tests the serialization and deserialization of Python dictionaries
    into and from JavaScript object notation (JSON). It ensures that the original
    data structure is preserved after serialization and deserialization.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The serialized form of a dictionary with a non-ASCII key should be a
    valid JSON string.
    - The original dictionary should be equal to the dictionary obtained after
    deserializing
    """

    data = {'1a': 1}
    assert dumps(data) == '{"1a":1}'
    assert data == loads(dumps(data))

    data = {'a1': 1}
    assert dumps(data) == '{a1:1}'
    assert data == loads(dumps(data))

    data = {'a\xe8': 1}
    assert dumps(data) == '{"a\\u00e8":1}'
    assert data == loads(dumps(data))

    data = {'_foo': 1}
    assert dumps(data) == '{_foo:1}'
    assert data == loads(dumps(data))
