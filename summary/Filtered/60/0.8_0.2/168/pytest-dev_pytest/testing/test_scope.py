import re

import pytest
from _pytest.scope import Scope


def test_ordering() -> None:
    """
    Tests the ordering of different scope levels in a software development context.
    
    This function asserts the correct ordering of scope levels, which are used to determine the visibility and accessibility of code elements in a programming environment. The scopes are compared in the following order: Session > Package > Module > Class > Function.
    
    The function does not take any parameters and does not return any value.
    """

    assert Scope.Session > Scope.Package
    assert Scope.Package > Scope.Module
    assert Scope.Module > Scope.Class
    assert Scope.Class > Scope.Function


def test_next_lower() -> None:
    assert Scope.Session.next_lower() is Scope.Package
    assert Scope.Package.next_lower() is Scope.Module
    assert Scope.Module.next_lower() is Scope.Class
    assert Scope.Class.next_lower() is Scope.Function

    with pytest.raises(ValueError, match="Function is the lower-most scope"):
        Scope.Function.next_lower()


def test_next_higher() -> None:
    assert Scope.Function.next_higher() is Scope.Class
    assert Scope.Class.next_higher() is Scope.Module
    assert Scope.Module.next_higher() is Scope.Package
    assert Scope.Package.next_higher() is Scope.Session

    with pytest.raises(ValueError, match="Session is the upper-most scope"):
        Scope.Session.next_higher()


def test_from_user() -> None:
    """
    Function to validate the scope of a given module, parametrize, and id.
    
    This function takes three parameters: `scope`, `parametrize`, and `id`. It checks if the `scope` is valid based on the values of `parametrize` and `id`. If the `scope` is not as expected, it raises an exception with a specific error message.
    
    Parameters:
    scope (str): The scope to validate.
    parametrize (str): The context in which the scope is
    """

    assert Scope.from_user("module", "for parametrize", "some::id") is Scope.Module

    expected_msg = "for parametrize from some::id got an unexpected scope value 'foo'"
    with pytest.raises(pytest.fail.Exception, match=re.escape(expected_msg)):
        Scope.from_user("foo", "for parametrize", "some::id")  # type:ignore[arg-type]
