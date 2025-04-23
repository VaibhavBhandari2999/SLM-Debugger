from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_with_attribute_comparison_off():
    """
    This function demonstrates the use of dataclasses in Python, specifically focusing on the `compare=False` parameter for a field. The `@dataclass` decorator is used to create a simple data class `SimpleDataObject` with two fields: `field_a` and `field_b`. The `field_b` is marked with `compare=False`, which means that when comparing two instances of `SimpleDataObject`, the value of `field_b` will not be considered.
    
    Parameters:
    - No explicit parameters
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field(compare=False)

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
