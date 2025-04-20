import inspect

import pytest
from _pytest import warning_types
from _pytest.pytester import Pytester


@pytest.mark.parametrize(
    "warning_class",
    [
        w
        for n, w in vars(warning_types).items()
        if inspect.isclass(w) and issubclass(w, Warning)
    ],
)
def test_warning_types(warning_class: UserWarning) -> None:
    """Make sure all warnings declared in _pytest.warning_types are displayed as coming
    from 'pytest' instead of the internal module (#5452).
    """
    assert warning_class.__module__ == "pytest"


@pytest.mark.filterwarnings("error::pytest.PytestWarning")
def test_pytest_warnings_repr_integration_test(pytester: Pytester) -> None:
    """Small integration test to ensure our small hack of setting the __module__ attribute
    of our warnings actually works (#5452).
    """
    pytester.makepyfile(
        """
        import pytest
        import warnings

        def test():
            warnings.warn(pytest.PytestWarning("some warning"))
    """
    )
    result = pytester.runpytest()
    result.stdout.fnmatch_lines(["E       pytest.PytestWarning: some warning"])


@pytest.mark.filterwarnings("error")
def test_warn_explicit_for_annotates_errors_with_location():
    """
    Function to test warning explicit for annotations with location.
    
    This function raises a warning using `pytest.raises` and `warning_types.warn_explicit_for` to check if the location of the warning message is correctly annotated.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    Warning: A pytest warning with the message "test" is raised. The warning message should include the file name and line number where the warning was raised.
    
    Note:
    The function uses a regular expression to match the warning message
    """

    with pytest.raises(Warning, match="(?m)test\n at .*python_api.py:\\d+"):
        warning_types.warn_explicit_for(
            pytest.raises, warning_types.PytestWarning("test")  # type: ignore
        )
