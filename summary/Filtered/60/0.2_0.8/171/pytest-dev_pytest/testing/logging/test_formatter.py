import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
    """
    Test the ColoredLevelFormatter with a custom log format.
    
    This function tests the ColoredLevelFormatter with a specific log format string and a sample LogRecord. It verifies that the formatter correctly formats the log record, applying color to the log level when the terminal supports markup.
    
    Parameters:
    - logfmt (str): The log format string to be used by the formatter.
    
    Returns:
    - None: The function asserts the expected output against the actual output.
    
    Key Points:
    - The function creates a LogRecord
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
