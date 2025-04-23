from typing import Optional

import pytest
from _pytest.config import ExitCode
from _pytest.pytester import Testdir


@pytest.mark.parametrize(
    "ret_exc",
    (
        pytest.param((None, ValueError)),
        pytest.param((42, SystemExit)),
        pytest.param((False, SystemExit)),
    ),
)
def test_wrap_session_notify_exception(ret_exc, testdir):
    """
    Test wrapping session notify exception.
    
    This function tests how pytest handles internal errors and session start exceptions. It creates a custom conftest file to simulate an exception during the session start phase. Depending on the exception type and the return code, pytest will either exit with a specific return code or raise an internal error. The function verifies the expected behavior by checking the exit code and the output messages.
    
    Parameters:
    ret_exc (tuple): A tuple containing the return code and the exception type to be raised during
    """

    returncode, exc = ret_exc
    c1 = testdir.makeconftest(
        """
        import pytest

        def pytest_sessionstart():
            raise {exc}("boom")

        def pytest_internalerror(excrepr, excinfo):
            returncode = {returncode!r}
            if returncode is not False:
                pytest.exit("exiting after %s..." % excinfo.typename, returncode={returncode!r})
    """.format(
            returncode=returncode, exc=exc.__name__
        )
    )
    result = testdir.runpytest()
    if returncode:
        assert result.ret == returncode
    else:
        assert result.ret == ExitCode.INTERNAL_ERROR
    assert result.stdout.lines[0] == "INTERNALERROR> Traceback (most recent call last):"

    if exc == SystemExit:
        assert result.stdout.lines[-3:] == [
            'INTERNALERROR>   File "{}", line 4, in pytest_sessionstart'.format(c1),
            'INTERNALERROR>     raise SystemExit("boom")',
            "INTERNALERROR> SystemExit: boom",
        ]
    else:
        assert result.stdout.lines[-3:] == [
            'INTERNALERROR>   File "{}", line 4, in pytest_sessionstart'.format(c1),
            'INTERNALERROR>     raise ValueError("boom")',
            "INTERNALERROR> ValueError: boom",
        ]
    if returncode is False:
        assert result.stderr.lines == ["mainloop: caught unexpected SystemExit!"]
    else:
        assert result.stderr.lines == ["Exit: exiting after {}...".format(exc.__name__)]


@pytest.mark.parametrize("returncode", (None, 42))
def test_wrap_session_exit_sessionfinish(
    """
    Wrap the test session with a custom session finish hook.
    
    This function runs a pytest session with a custom session finish hook defined in the conftest file. The hook exits the pytest session with a specified return code or with a default return code of 0 if no return code is provided. The function asserts the exit code and the output of the pytest session.
    
    Parameters:
    returncode (Optional[int]): The return code to exit the pytest session with. If not provided, the session will exit with
    """

    returncode: Optional[int], testdir: Testdir
) -> None:
    testdir.makeconftest(
        """
        import pytest
        def pytest_sessionfinish():
            pytest.exit(msg="exit_pytest_sessionfinish", returncode={returncode})
    """.format(
            returncode=returncode
        )
    )
    result = testdir.runpytest()
    if returncode:
        assert result.ret == returncode
    else:
        assert result.ret == ExitCode.NO_TESTS_COLLECTED
    assert result.stdout.lines[-1] == "collected 0 items"
    assert result.stderr.lines == ["Exit: exit_pytest_sessionfinish"]
