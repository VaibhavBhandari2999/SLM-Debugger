from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    This function demonstrates the use of dataclasses in Python to create a simple data object. The dataclass `SimpleDataObject` is defined with two fields: `field_a` and `field_b`. Both fields are initialized with default values and are expected to be integers.
    
    Key Parameters:
    - field_a (int): The first field of the data object.
    - field_b (int): The second field of the data object.
    
    Keywords:
    - dataclass: A Python decorator used to automatically generate special methods
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
