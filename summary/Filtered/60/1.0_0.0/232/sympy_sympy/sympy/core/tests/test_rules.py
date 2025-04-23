from sympy.core.rules import Transform

from sympy.utilities.pytest import raises


def test_Transform():
    """
    Transform a dictionary by applying a function to keys that meet a condition.
    
    This function creates a Transform object that applies a given function to keys in a dictionary if they meet a specified condition.
    
    Parameters:
    func (callable): A function to be applied to the keys that meet the condition.
    condition (callable): A condition that the keys must meet to be transformed.
    
    Returns:
    Transform: A Transform object that can be used to access transformed keys.
    
    Example usage:
    add1 = Transform(lambda x
    """

    add1 = Transform(lambda x: x + 1, lambda x: x % 2 == 1)
    assert add1[1] == 2
    assert (1 in add1) is True
    assert add1.get(1) == 2

    raises(KeyError, lambda: add1[2])
    assert (2 in add1) is False
    assert add1.get(2) is None
