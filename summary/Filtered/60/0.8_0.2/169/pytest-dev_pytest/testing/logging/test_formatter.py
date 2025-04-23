import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
    """
    Tests the ColoredLevelFormatter class for formatting log records with color.
    
    This function initializes a log formatter with a specific format string and tests its behavior with and without terminal markup support. It creates a `LogRecord` instance and uses the `ColoredLevelFormatter` to format the log record. The function asserts that the formatted output matches the expected results based on the presence or absence of terminal markup.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - `logfmt`: The format
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
