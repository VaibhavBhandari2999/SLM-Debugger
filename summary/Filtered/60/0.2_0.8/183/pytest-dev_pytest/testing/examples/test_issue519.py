from _pytest.pytester import Pytester


def test_519(pytester: Pytester) -> None:
    """
    Test the function to ensure it correctly runs a pytest on the specified file and returns the expected outcomes.
    
    Args:
    pytester (Pytester): A fixture that provides functionality to copy and run pytest on example files.
    
    Returns:
    None: The function asserts the expected outcomes through the test runner's output.
    """

    pytester.copy_example("issue_519.py")
    res = pytester.runpytest("issue_519.py")
    res.assert_outcomes(passed=8)
