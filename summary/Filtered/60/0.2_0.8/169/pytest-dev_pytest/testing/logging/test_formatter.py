import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
    """
    Test the ColoredLevelFormatter with different configurations.
    
    This function tests the ColoredLevelFormatter by setting up a LogRecord with specific attributes and using a custom log format string. It then creates an instance of ColoredLevelFormatter with a TerminalWriter that has markup enabled and disabled, and formats the LogRecord to check the output.
    
    Parameters:
    - logfmt (str): The log format string to be used for formatting the log record.
    
    Returns:
    - None: The function asserts the expected output against the
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
