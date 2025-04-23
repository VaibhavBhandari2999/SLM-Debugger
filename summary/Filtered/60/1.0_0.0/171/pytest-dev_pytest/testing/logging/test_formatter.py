import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
    """
    Tests the ColoredLevelFormatter class for formatting log records with color.
    
    This function checks the functionality of the ColoredLevelFormatter class by formatting a log record with a specified log format string. The formatter is expected to add color to the log level if the TerminalWriter has markup capabilities.
    
    Parameters:
    - logfmt (str): The log format string to be used for formatting the log record.
    
    Returns:
    - str: The formatted log record as a string.
    
    Key Points:
    - The function creates a dummy
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
