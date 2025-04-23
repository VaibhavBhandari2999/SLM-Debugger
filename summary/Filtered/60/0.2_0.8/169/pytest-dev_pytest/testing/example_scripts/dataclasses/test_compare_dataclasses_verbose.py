from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    Tests the behavior of a dataclass with verbose field initialization.
    
    This function creates a dataclass named `SimpleDataObject` with two fields, `field_a` and `field_b`. Both fields are initialized with default values. The function then creates two instances of this dataclass, `left` and `right`, with `field_a` set to 1 and `field_b` set to different values, 'b' and 'c' respectively. The function asserts that these two instances are considered
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
