# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/PyCQA/pylint/blob/main/CONTRIBUTORS.txt

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from pylint.testutils.checker_test_case import CheckerTestCase


def set_config(**kwargs: Any) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Decorator for setting an option on the linter.

    Passing the args and kwargs back to the test function itself
    allows this decorator to be used on parameterized test cases.
    """

    def _wrapper(fun: Callable[..., None]) -> Callable[..., None]:
        """
        Wrapper function for test cases in a CheckerTestCase class.
        
        This function is designed to be used as a decorator for test methods in a CheckerTestCase class. It sets the specified options via argparse and reopens the checker to reflect any configuration changes. The test method is then called with the provided arguments.
        
        Parameters:
        fun (Callable[..., None]): The test method to be wrapped.
        
        Returns:
        Callable[..., None]: The wrapped test method.
        
        Usage:
        @wrapper
        def test_example(self, arg
        """

        @functools.wraps(fun)
        def _forward(
            self: CheckerTestCase, *args: Any, **test_function_kwargs: Any
        ) -> None:
            """Set option via argparse."""
            for key, value in kwargs.items():
                self.linter.set_option(key, value)

            # Reopen checker in case, it may be interested in configuration change
            self.checker.open()

            fun(self, *args, **test_function_kwargs)

        return _forward

    return _wrapper
