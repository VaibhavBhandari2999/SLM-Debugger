import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
    """
    Test the ColoredLevelFormatter with a custom log format.
    
    This function tests the ColoredLevelFormatter class by formatting a log record
    with a specified log format. The formatter is expected to color the log level
    if the terminal supports markup. The function checks the output for both
    colored and non-colored terminal scenarios.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - `logfmt` (str): The log format string to be used for formatting the log record.
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
