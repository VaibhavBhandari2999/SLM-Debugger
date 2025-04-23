from dataclasses import dataclass
from dataclasses import field


def test_dataclasses():
    """
    This function demonstrates the usage of the `dataclasses` module in Python to create a simple data class named `SimpleDataObject`. The class has two fields, `field_a` and `field_b`, both of which are integers. The `field` decorator is used to initialize these fields. The function creates two instances of `SimpleDataObject` with the same value for `field_a` but different values for `field_b`. It then checks if these two instances are equal, which they are
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
