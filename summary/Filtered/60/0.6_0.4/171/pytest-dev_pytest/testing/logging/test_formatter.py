import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
    """
    Test the ColoredLevelFormatter with different configurations.
    
    This function tests the ColoredLevelFormatter by creating a LogRecord and formatting it with different TerminalWriter settings. It checks that the output matches the expected colored or non-colored log message based on the TerminalWriter's `hasmarkup` attribute.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - The function uses a predefined log format string `logfmt` which includes placeholders for filename, line number, log level, and message.
    -
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
