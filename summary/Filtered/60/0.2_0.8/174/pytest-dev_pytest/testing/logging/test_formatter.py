import logging

import py.io

from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter():
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

    class ColorConfig:
        class option:
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


def test_multiline_message():
    """
    Tests a multiline message formatting using a custom logging formatter.
    
    This function verifies the formatting of a log message that spans multiple lines using the `PercentStyleMultiline` formatter from `_pytest.logging`. The formatter is configured with a specific log format string.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> test_multiline_message()
    # The function will assert that the formatted log message matches the expected output.
    """

    from _pytest.logging import PercentStyleMultiline

    logfmt = "%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"

    record = logging.LogRecord(
        name="dummy",
        level=logging.INFO,
        pathname="dummypath",
        lineno=10,
        msg="Test Message line1\nline2",
        args=(),
        exc_info=False,
    )
    # this is called by logging.Formatter.format
    record.message = record.getMessage()

    style = PercentStyleMultiline(logfmt)
    output = style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\n"
        "                                        line2"
    )


def test_colored_short_level():
    logfmt = "%(levelname).1s %(message)s"

    record = logging.LogRecord(
        name="dummy",
        level=logging.INFO,
        pathname="dummypath",
        lineno=10,
        msg="Test Message",
        args=(),
        exc_info=False,
    )

    class ColorConfig:
        class option:
            pass

    tw = py.io.TerminalWriter()
    tw.hasmarkup = True
    formatter = ColoredLevelFormatter(tw, logfmt)
    output = formatter.format(record)
    # the I (of INFO) is colored
    assert output == ("\x1b[32mI\x1b[0m Test Message")
