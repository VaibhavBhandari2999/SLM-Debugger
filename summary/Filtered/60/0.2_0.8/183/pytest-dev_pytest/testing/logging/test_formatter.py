import logging
from typing import Any

from _pytest._io import TerminalWriter
from _pytest.logging import ColoredLevelFormatter


def test_coloredlogformatter() -> None:
    """
    Test the ColoredLevelFormatter with different TerminalWriter settings.
    
    This function tests the ColoredLevelFormatter by creating a LogRecord and formatting it with a specific log format string. The test checks the output based on whether the TerminalWriter has markup enabled or not.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The output matches the expected string when TerminalWriter has markup enabled.
    - The output matches the expected string when TerminalWriter does not have markup enabled.
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
    Tests the formatting of log records with colored short levels.
    
    This function creates a log record with specified attributes and uses a `ColoredLevelFormatter` to format the record. The formatted output is checked to ensure that the level indicator is colored.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Attributes:
    - `logfmt`: The format string for the log record, which includes the level as a single character.
    - `record`: A `LogRecord` instance with predefined attributes such as
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
x1b[0m Test Message")
