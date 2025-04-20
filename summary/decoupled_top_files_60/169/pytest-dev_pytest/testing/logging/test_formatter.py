import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
    """
    Tests the ColoredLevelFormatter class for formatting log records with color.
    
    This function checks the formatting of log records using the ColoredLevelFormatter class. It takes a log format string and a LogRecord object as input and returns a formatted string. The function also tests the behavior of the formatter when terminal markup is enabled or disabled.
    
    Parameters:
    logfmt (str): The log format string to be used for formatting.
    
    Returns:
    str: The formatted log message.
    
    Key Parameters:
    - log
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
