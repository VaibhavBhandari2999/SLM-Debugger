import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
    """
    Tests the functionality of the ColoredLevelFormatter with different configurations.
    
    Args:
    None
    
    Returns:
    None
    
    Summary:
    This function tests the ColoredLevelFormatter by creating a LogRecord object and formatting it using different TerminalWriter configurations. It checks if the formatted output matches the expected results based on whether the TerminalWriter has markup enabled or not.
    
    Important Functions:
    - `ColoredLevelFormatter`: The formatter used to format the log record.
    - `logging.Log
    """

    logfmt = "%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"

    record = logging.LogRecord(
        name="dummy",
        level=logging.INFO,
        pathname="dummypath",
        lineno=10,
        msg="Test Message",
        args=(),
        exc_info=False,
    )

    class ColorConfig(object):
        class option(object):
            pass

    tw = py.io.TerminalWriter()
    tw.hasmarkup = True
    formatter = ColoredLevelFormatter(tw, logfmt)
    output = formatter.format(record)
    assert output == (
        "dummypath                   10 \x1b[32mINFO    \x1b[0m Test Message"
    )

    tw.hasmarkup = False
    formatter = ColoredLevelFormatter(tw, logfmt)
    output = formatter.format(record)
    assert output == ("dummypath                   10 INFO     Test Message")
