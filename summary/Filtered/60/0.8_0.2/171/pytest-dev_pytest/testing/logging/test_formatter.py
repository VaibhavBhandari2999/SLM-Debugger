import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
    """
    Test the ColoredLevelFormatter with a custom log format.
    
    This function tests the ColoredLevelFormatter class by creating a LogRecord
    with specific attributes and formatting it using the provided log format.
    The test checks the output for both cases where the TerminalWriter supports
    markup and where it does not.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Attributes:
    - `logfmt`: The custom log format string.
    - `record`: A LogRecord instance with predefined attributes.
    
    Output:
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
