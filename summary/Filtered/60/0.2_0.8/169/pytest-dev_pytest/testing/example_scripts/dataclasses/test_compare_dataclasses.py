from dataclasses import dataclass
from dataclasses import field


def test_dataclasses():
    """
    This function demonstrates the usage of the `dataclasses` module in Python to create a simple data class. The `SimpleDataObject` class is defined with two fields, `field_a` and `field_b`, both of which are integers. The `field` decorator is used to initialize these fields.
    
    Key Parameters:
    - field_a: An integer value for the first field.
    - field_b: An integer value for the second field.
    
    The function creates two instances of `SimpleDataObject` with
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
