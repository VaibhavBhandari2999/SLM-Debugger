from sphinx.util.jsdump import dumps, loads


def test_jsdump():
    """
    Test the JavaScript object serialization and deserialization functions.
    
    Args:
    data (dict): The dictionary to be serialized and deserialized.
    
    Returns:
    None: The function asserts the correctness of the serialization and deserialization process.
    
    This function checks the behavior of the `dumps` and `loads` functions for different types of input dictionaries, including those with special characters and reserved names, ensuring that the serialization and deserialization processes maintain the integrity of the original data.
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
