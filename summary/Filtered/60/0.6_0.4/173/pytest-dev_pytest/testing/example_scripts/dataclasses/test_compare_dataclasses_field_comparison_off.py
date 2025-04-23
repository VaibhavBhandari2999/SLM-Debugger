from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_with_attribute_comparison_off():
    """
    This function demonstrates the usage of dataclasses in Python, specifically focusing on how to handle attribute comparison. The function defines a dataclass `SimpleDataObject` with two fields: `field_a` and `field_b`. The `field_b` is marked with `compare=False` to prevent it from being considered in the comparison operations.
    
    Key Parameters:
    - No explicit parameters are passed to the function. The function demonstrates the behavior of the dataclass `SimpleDataObject`.
    
    Keywords:
    - `dataclass
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field(compare=False)

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
