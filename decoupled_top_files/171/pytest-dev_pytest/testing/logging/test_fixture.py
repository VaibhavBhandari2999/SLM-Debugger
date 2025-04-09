# -*- coding: utf-8 -*-
import logging

import pytest

logger = logging.getLogger(__name__)
sublogger = logging.getLogger(__name__ + ".baz")


def test_fixture_help(testdir):
    result = testdir.runpytest("--fixtures")
    result.stdout.fnmatch_lines(["*caplog*"])


def test_change_level(caplog):
    """
    Set up logging levels and test filtering of log messages.
    
    This function sets the logging level to `INFO` and tests that debug messages are filtered out while info messages are captured. It then sets the logging level to `CRITICAL` for a specific logger and tests that warning and critical messages are captured while other levels are filtered out.
    
    Args:
    caplog (pytest.LogCaptureFixture): A fixture provided by pytest for capturing log messages.
    
    Returns:
    None: The function asserts that the
    """

    caplog.set_level(logging.INFO)
    logger.debug("handler DEBUG level")
    logger.info("handler INFO level")

    caplog.set_level(logging.CRITICAL, logger=sublogger.name)
    sublogger.warning("logger WARNING level")
    sublogger.critical("logger CRITICAL level")

    assert "DEBUG" not in caplog.text
    assert "INFO" in caplog.text
    assert "WARNING" not in caplog.text
    assert "CRITICAL" in caplog.text


def test_change_level_undo(testdir):
    """Ensure that 'set_level' is undone after the end of the test"""
    testdir.makepyfile(
        """
        import logging

        def test1(caplog):
            caplog.set_level(logging.INFO)
            # using + operator here so fnmatch_lines doesn't match the code in the traceback
            logging.info('log from ' + 'test1')
            assert 0

        def test2(caplog):
            # using + operator here so fnmatch_lines doesn't match the code in the traceback
            logging.info('log from ' + 'test2')
            assert 0
    """
    )
    result = testdir.runpytest()
    result.stdout.fnmatch_lines(["*log from test1*", "*2 failed in *"])
    assert "log from test2" not in result.stdout.str()


def test_with_statement(caplog):
    """
    Test logging levels using the `with` statement.
    
    This function tests the logging levels by capturing log messages within a specified context. It uses the `caplog.at_level` method to set the logging level for different parts of the code. The function logs messages at various levels (DEBUG, INFO, WARNING, CRITICAL) and checks if the messages are captured based on their severity.
    
    Args:
    caplog (pytest.LogCaptureFixture): A fixture that captures log messages.
    
    Returns:
    """

    with caplog.at_level(logging.INFO):
        logger.debug("handler DEBUG level")
        logger.info("handler INFO level")

        with caplog.at_level(logging.CRITICAL, logger=sublogger.name):
            sublogger.warning("logger WARNING level")
            sublogger.critical("logger CRITICAL level")

    assert "DEBUG" not in caplog.text
    assert "INFO" in caplog.text
    assert "WARNING" not in caplog.text
    assert "CRITICAL" in caplog.text


def test_log_access(caplog):
    """
    Test logging access.
    
    Args:
    caplog (pytest.LogCaptureFixture): A fixture that captures log messages.
    
    Summary:
    This function tests logging access by setting the log level to INFO,
    logging a message with placeholders, and asserting the log record's
    level name, message, and presence in the captured logs.
    
    Returns:
    None
    """

    caplog.set_level(logging.INFO)
    logger.info("boo %s", "arg")
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].msg == "boo %s"
    assert "boo arg" in caplog.text


def test_messages(caplog):
    """
    Test logging messages using caplog.
    
    Args:
    caplog (pytest.LogCaptureFixture): A fixture that captures log messages.
    
    Summary:
    This function tests logging messages with different formats and asserts the captured log messages. It also tests exception handling and logs the traceback. The important keywords and functions used include `caplog`, `logging.INFO`, `logger.info`, `assert`, and `logger.exception`.
    """

    caplog.set_level(logging.INFO)
    logger.info("boo %s", "arg")
    logger.info("bar %s\nbaz %s", "arg1", "arg2")
    assert "boo arg" == caplog.messages[0]
    assert "bar arg1\nbaz arg2" == caplog.messages[1]
    assert caplog.text.count("\n") > len(caplog.messages)
    assert len(caplog.text.splitlines()) > len(caplog.messages)

    try:
        raise Exception("test")
    except Exception:
        logger.exception("oops")

    assert "oops" in caplog.text
    assert "oops" in caplog.messages[-1]
    # Tracebacks are stored in the record and not added until the formatter or handler.
    assert "Exception" in caplog.text
    assert "Exception" not in caplog.messages[-1]


def test_record_tuples(caplog):
    """
    Test the logging of record tuples.
    
    This function sets the log level to INFO and logs a message using the `logger` object. It then checks if the recorded log messages match the expected tuple.
    
    Args:
    caplog (pytest.LogCaptureFixture): A fixture that captures log messages.
    
    Returns:
    None
    """

    caplog.set_level(logging.INFO)
    logger.info("boo %s", "arg")

    assert caplog.record_tuples == [(__name__, logging.INFO, "boo arg")]


def test_unicode(caplog):
    """
    Test logging of Unicode characters.
    
    Args:
    caplog (pytest.LogCaptureFixture): A fixture for capturing log messages.
    
    Summary:
    This function tests the logging of Unicode characters using the `logger.info` method. It sets the log level to INFO, logs the Unicode character 'bū', and asserts that the logged message matches the expected value. The function uses the `caplog` fixture to capture and verify the log records.
    
    Returns:
    None
    """

    caplog.set_level(logging.INFO)
    logger.info(u"bū")
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].msg == u"bū"
    assert u"bū" in caplog.text


def test_clear(caplog):
    """
    Clears the captured log records and text.
    
    This function sets the logging level to INFO, logs a message using the `logger` object, asserts that there are log records and text, clears the captured log records and text, and asserts that there are no more log records or text.
    
    Args:
    caplog (pytest.LogCaptureFixture): A fixture that captures log records.
    
    Returns:
    None
    """

    caplog.set_level(logging.INFO)
    logger.info(u"bū")
    assert len(caplog.records)
    assert caplog.text
    caplog.clear()
    assert not len(caplog.records)
    assert not caplog.text


@pytest.fixture
def logging_during_setup_and_teardown(caplog):
    """
    Logs information during setup and teardown using the `caplog` fixture. Sets the log level to 'INFO', records a setup log message, yields control, records a teardown log message, and asserts that the teardown logs match the expected message.
    
    Args:
    caplog (pytest.LogCaptureFixture): A pytest fixture for capturing log messages.
    
    Yields:
    None: Control is yielded during the test execution.
    
    Raises:
    AssertionError: If the teardown logs do not match the expected message.
    """

    caplog.set_level("INFO")
    logger.info("a_setup_log")
    yield
    logger.info("a_teardown_log")
    assert [x.message for x in caplog.get_records("teardown")] == ["a_teardown_log"]


def test_caplog_captures_for_all_stages(caplog, logging_during_setup_and_teardown):
    """
    Summary: This function captures logs using pytest's caplog fixture for setup and call stages. It asserts that no records are present initially, then logs an info message and checks if the log is captured correctly. It also verifies that the setup stage logs are captured and ensures that the catch_log_handlers dictionary contains entries for both 'setup' and 'call' stages.
    
    Args:
    caplog (pytest fixture): A pytest fixture for capturing logs.
    logging_during_setup_and_teardown (function):
    """

    assert not caplog.records
    assert not caplog.get_records("call")
    logger.info("a_call_log")
    assert [x.message for x in caplog.get_records("call")] == ["a_call_log"]

    assert [x.message for x in caplog.get_records("setup")] == ["a_setup_log"]

    # This reaches into private API, don't use this type of thing in real tests!
    assert set(caplog._item.catch_log_handlers.keys()) == {"setup", "call"}
