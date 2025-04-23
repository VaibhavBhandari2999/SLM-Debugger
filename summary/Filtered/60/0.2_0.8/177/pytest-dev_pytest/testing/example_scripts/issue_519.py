import pprint

import pytest


def pytest_generate_tests(metafunc):
    if "arg1" in metafunc.fixturenames:
        metafunc.parametrize("arg1", ["arg1v1", "arg1v2"], scope="module")

    if "arg2" in metafunc.fixturenames:
        metafunc.parametrize("arg2", ["arg2v1", "arg2v2"], scope="function")


@pytest.fixture(scope="session")
def checked_order():
    """
    Generates a test order for a series of tests and fixes. The function yields a list of tuples, each containing the path to a test script, a fix name, and an argument value. The function asserts that the generated order matches a predefined sequence of test scripts, fixes, and argument values.
    
    Key Parameters:
    - None
    
    Output:
    - A generator that yields a list of tuples, each containing:
    - The path to a test script (str)
    - A fix name (str)
    """

    order = []

    yield order
    pprint.pprint(order)
    assert order == [
        ("testing/example_scripts/issue_519.py", "fix1", "arg1v1"),
        ("test_one[arg1v1-arg2v1]", "fix2", "arg2v1"),
        ("test_two[arg1v1-arg2v1]", "fix2", "arg2v1"),
        ("test_one[arg1v1-arg2v2]", "fix2", "arg2v2"),
        ("test_two[arg1v1-arg2v2]", "fix2", "arg2v2"),
        ("testing/example_scripts/issue_519.py", "fix1", "arg1v2"),
        ("test_one[arg1v2-arg2v1]", "fix2", "arg2v1"),
        ("test_two[arg1v2-arg2v1]", "fix2", "arg2v1"),
        ("test_one[arg1v2-arg2v2]", "fix2", "arg2v2"),
        ("test_two[arg1v2-arg2v2]", "fix2", "arg2v2"),
    ]


@pytest.yield_fixture(scope="module")
def fix1(request, arg1, checked_order):
    checked_order.append((request.node.name, "fix1", arg1))
    yield "fix1-" + arg1


@pytest.yield_fixture(scope="function")
def fix2(request, fix1, arg2, checked_order):
    checked_order.append((request.node.name, "fix2", arg2))
    yield "fix2-" + arg2 + fix1


def test_one(fix2):
    pass


def test_two(fix2):
    pass
