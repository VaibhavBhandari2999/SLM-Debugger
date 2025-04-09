import logging
from typing import Any

from _pytest._io import TerminalWriter
from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter() -> None:
    """
    Tests the functionality of the ColoredLevelFormatter class with different TerminalWriter settings.
    
    Args:
    None
    
    Returns:
    None
    
    Summary:
    This function tests the ColoredLevelFormatter class by creating a LogRecord object and formatting it using the specified log format string. The function checks the output based on whether the TerminalWriter has markup enabled or not.
    
    Important Functions:
    - `ColoredLevelFormatter`: The class responsible for formatting log records with color based on the TerminalWriter
    """

    logfmt = "%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"

    record = logging.LogRecord(
        name="dummy",
        level=logging.INFO,
        pathname="dummypath",
        lineno=10,
        msg="Test Message",
        args=(),
        exc_info=None,
    )

    tw = TerminalWriter()
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


def test_coloredlogformatter_with_width_precision() -> None:
    """
    Tests the functionality of the ColoredLevelFormatter with specified width and precision settings.
    
    Args:
    None
    
    Returns:
    None
    
    Important Functions:
    - `ColoredLevelFormatter`: The formatter used to format log records with color and width/precision settings.
    - `TerminalWriter`: The writer responsible for handling terminal-specific formatting.
    - `logging.LogRecord`: The log record object containing the log message details.
    
    Summary:
    This function tests the ColoredLevelFormatter by
    """

    logfmt = "%(filename)-25s %(lineno)4d %(levelname)-8.8s %(message)s"

    record = logging.LogRecord(
        name="dummy",
        level=logging.INFO,
        pathname="dummypath",
        lineno=10,
        msg="Test Message",
        args=(),
        exc_info=None,
    )

    tw = TerminalWriter()
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


def test_multiline_message() -> None:
    """
    This function tests the formatting of multiline messages using the PercentStyleMultiline class from _pytest.logging.
    
    Args:
    None
    
    Returns:
    None
    
    Important Functions:
    - PercentStyleMultiline: A class from _pytest.logging that formats log records with multiline messages.
    - logging.LogRecord: A class representing a log record with attributes like name, level, pathname, lineno, msg, etc.
    - logging.Formatter.format: A method that formats the log record message based on
    """

    from _pytest.logging import PercentStyleMultiline

    logfmt = "%(filename)-25s %(lineno)4d %(levelname)-8s %(message)s"

    record: Any = logging.LogRecord(
        name="dummy",
        level=logging.INFO,
        pathname="dummypath",
        lineno=10,
        msg="Test Message line1\nline2",
        args=(),
        exc_info=None,
    )
    # this is called by logging.Formatter.format
    record.message = record.getMessage()

    ai_on_style = PercentStyleMultiline(logfmt, True)
    output = ai_on_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\n"
        "                                        line2"
    )

    ai_off_style = PercentStyleMultiline(logfmt, False)
    output = ai_off_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\nline2"
    )

    ai_none_style = PercentStyleMultiline(logfmt, None)
    output = ai_none_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\nline2"
    )

    record.auto_indent = False
    output = ai_on_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\nline2"
    )

    record.auto_indent = True
    output = ai_off_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\n"
        "                                        line2"
    )

    record.auto_indent = "False"
    output = ai_on_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\nline2"
    )

    record.auto_indent = "True"
    output = ai_off_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\n"
        "                                        line2"
    )

    # bad string values default to False
    record.auto_indent = "junk"
    output = ai_off_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\nline2"
    )

    # anything other than string or int will default to False
    record.auto_indent = dict()
    output = ai_off_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\nline2"
    )

    record.auto_indent = "5"
    output = ai_off_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\n     line2"
    )

    record.auto_indent = 5
    output = ai_off_style.format(record)
    assert output == (
        "dummypath                   10 INFO     Test Message line1\n     line2"
    )


def test_colored_short_level() -> None:
    """
    Formats a log record with colored levels using the specified format.
    
    Args:
    None
    
    Returns:
    None
    
    Attributes:
    logfmt (str): The format string for the log record.
    record (logging.LogRecord): The log record to be formatted.
    ColorConfig (class): A configuration class for color options.
    TerminalWriter (class): A class for terminal writing.
    ColoredLevelFormatter (class): A formatter for colored log levels.
    
    Summary:
    This
    """

    logfmt = "%(levelname).1s %(message)s"

    record = logging.LogRecord(
        name="dummy",
        level=logging.INFO,
        pathname="dummypath",
        lineno=10,
        msg="Test Message",
        args=(),
        exc_info=None,
    )

    class ColorConfig:
        class option:
            pass

    tw = TerminalWriter()
    tw.hasmarkup = True
    formatter = ColoredLevelFormatter(tw, logfmt)
    output = formatter.format(record)
    # the I (of INFO) is colored
    assert output == ("\x1b[32mI\x1b[0m Test Message")
