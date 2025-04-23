# -*- coding: utf-8 -*-
import logging

import pytest

logger = logging.getLogger(__name__)
sublogger = logging.getLogger(__name__ + ".baz")


def test_fixture_help(testdir):
    result = testdir.runpytest("--fixtures")
    result.stdout.fnmatch_lines(["*caplog*"])


def test_change_level(caplog):
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
    
    This function captures and asserts the logging output using the caplog fixture. It sets the log level to INFO and logs a message with an argument. The function checks that the logged record has the correct level and message, and that the formatted message is present in the captured logs.
    
    Parameters:
    caplog (pytest.LogCaptureFixture): A fixture provided by pytest for capturing logging output.
    
    Returns:
    None: This function does not return any value. It asserts the correctness of the logging
    """

    caplog.set_level(logging.INFO)
    logger.info("boo %s", "arg")
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].msg == "boo %s"
    assert "boo arg" in caplog.text


def test_messages(caplog):
    """
    Test logging messages.
    
    This function tests the logging of messages with different formats and ensures that the captured log messages match the expected output. It also checks for the presence of tracebacks in the log when an exception is raised.
    
    Parameters:
    caplog (pytest.LogCaptureFixture): A fixture provided by pytest for capturing log messages.
    
    Returns:
    None: The function asserts conditions and does not return any value.
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
    caplog.set_level(logging.INFO)
    logger.info("boo %s", "arg")

    assert caplog.record_tuples == [(__name__, logging.INFO, "boo arg")]


def test_unicode(caplog):
    caplog.set_level(logging.INFO)
    logger.info(u"bū")
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].msg == u"bū"
    assert u"bū" in caplog.text


def test_clear(caplog):
    """
    Clears the captured log records and text.
    
    This function clears the captured log records and the log text in the `caplog` object, allowing for subsequent tests to start with a clean slate.
    
    Parameters:
    caplog (pytest.LogCaptureFixture): The pytest fixture used to capture log records.
    
    Returns:
    None: This function does not return any value. It modifies the `caplog` object in place.
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
    caplog.set_level("INFO")
    logger.info("a_setup_log")
    yield
    logger.info("a_teardown_log")
    assert [x.message for x in caplog.get_records("teardown")] == ["a_teardown_log"]


def test_caplog_captures_for_all_stages(caplog, logging_during_setup_and_teardown):
    """
    This function tests the logging capture mechanism for different stages of execution.
    
    Parameters:
    caplog (pytest.LogCaptureFixture): A fixture provided by pytest for capturing log messages.
    logging_during_setup_and_teardown (function): A function that logs messages during setup and teardown.
    
    Returns:
    None: This function asserts conditions based on the captured log records and does not return any value.
    
    Key Steps:
    1. Asserts that no log records are captured initially.
    2. Logs an info message and asserts
    """

    assert not caplog.records
    assert not caplog.get_records("call")
    logger.info("a_call_log")
    assert [x.message for x in caplog.get_records("call")] == ["a_call_log"]

    assert [x.message for x in caplog.get_records("setup")] == ["a_setup_log"]

    # This reaches into private API, don't use this type of thing in real tests!
    assert set(caplog._item.catch_log_handlers.keys()) == {"setup", "call"}
