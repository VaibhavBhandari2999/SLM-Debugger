import pprint
from typing import List
from typing import Tuple

import pytest


def pytest_generate_tests(metafunc):
    """
    Generates test cases for a test function.
    
    This function is used to dynamically generate test cases for a test function. It takes a test function as input and automatically generates test cases based on the parameters specified in the function's signature.
    
    Parameters:
    metafunc (pytest.Metafunc): The pytest metafunction object that provides access to the test function and its parameters.
    
    Returns:
    None: This function does not return any value. It directly modifies the test function's parameters to include the generated test cases.
    """

    if "arg1" in metafunc.fixturenames:
        metafunc.parametrize("arg1", ["arg1v1", "arg1v2"], scope="module")

    if "arg2" in metafunc.fixturenames:
        metafunc.parametrize("arg2", ["arg2v1", "arg2v2"], scope="function")


@pytest.fixture(scope="session")
def checked_order():
    """
    Generates a list of tuples representing an ordered sequence of test cases and their corresponding fixes and arguments.
    
    Yields:
    List[Tuple[str, str, str]]: A list of tuples where each tuple contains the name of the test case, the fix applied, and the argument value.
    
    Example:
    >>> checked_order()
    [
    ('issue_519.py', 'fix1', 'arg1v1'),
    ('test_one[arg1v1-arg2v1]',
    """

    order: List[Tuple[str, str, str]] = []

    yield order
    pprint.pprint(order)
    assert order == [
        ("issue_519.py", "fix1", "arg1v1"),
        ("test_one[arg1v1-arg2v1]", "fix2", "arg2v1"),
        ("test_two[arg1v1-arg2v1]", "fix2", "arg2v1"),
        ("test_one[arg1v1-arg2v2]", "fix2", "arg2v2"),
        ("test_two[arg1v1-arg2v2]", "fix2", "arg2v2"),
        ("issue_519.py", "fix1", "arg1v2"),
        ("test_one[arg1v2-arg2v1]", "fix2", "arg2v1"),
        ("test_two[arg1v2-arg2v1]", "fix2", "arg2v1"),
        ("test_one[arg1v2-arg2v2]", "fix2", "arg2v2"),
        ("test_two[arg1v2-arg2v2]", "fix2", "arg2v2"),
    ]


@pytest.fixture(scope="module")
def fix1(request, arg1, checked_order):
    checked_order.append((request.node.name, "fix1", arg1))
    yield "fix1-" + arg1


@pytest.fixture(scope="function")
def fix2(request, fix1, arg2, checked_order):
    checked_order.append((request.node.name, "fix2", arg2))
    yield "fix2-" + arg2 + fix1


def test_one(fix2):
    pass


def test_two(fix2):
    pass
