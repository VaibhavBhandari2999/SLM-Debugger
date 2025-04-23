from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_with_attribute_comparison_off():
    """
    This function demonstrates the use of dataclasses in Python, specifically focusing on the `compare=False` parameter for a field. The `SimpleDataObject` class is defined with two fields: `field_a` and `field_b`. The `field_b` is marked with `compare=False`, which means it will not be used in the comparison of instances of this class.
    
    Parameters:
    - No explicit parameters are required for this function as it is a demonstration of the concept.
    
    Key Attributes:
    - `
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field(compare=False)

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
