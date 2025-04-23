from _pytest.pytester import Pytester


def test_519(pytester: Pytester) -> None:
    """
    Test the function to run pytest on a specific example file and verify the outcomes.
    
    This function copies an example file 'issue_519.py' and runs pytest on it. It then checks the outcomes to ensure that 8 tests have passed.
    
    Parameters:
    pytester (Pytester): An instance of the Pytester fixture, which provides methods to copy example files and run pytest.
    
    Returns:
    None: The function asserts the expected outcomes and does not return any value.
    """

    pytester.copy_example("issue_519.py")
    res = pytester.runpytest("issue_519.py")
    res.assert_outcomes(passed=8)
