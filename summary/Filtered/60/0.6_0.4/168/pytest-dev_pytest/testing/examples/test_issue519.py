from _pytest.pytester import Pytester


def test_519(pytester: Pytester) -> None:
    """
    Test function to run pytest on a specific example file and verify the outcomes.
    
    This function copies an example file 'issue_519.py' and runs pytest on it. It then checks the outcomes to ensure that all tests pass.
    
    Parameters:
    pytester (Pytester): A fixture provided by pytest that allows for testing of pytest itself.
    
    Returns:
    None: The function asserts the expected outcomes and does not return any value.
    """

    pytester.copy_example("issue_519.py")
    res = pytester.runpytest("issue_519.py")
    res.assert_outcomes(passed=8)
