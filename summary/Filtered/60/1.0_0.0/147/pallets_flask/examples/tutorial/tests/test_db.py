import sqlite3

import pytest

from flaskr.db import get_db


def test_get_close_db(app):
    """
    Summary:
    This function tests the behavior of the `get_close_db` function within the context of an application's request.
    
    Parameters:
    - app: The Flask application object used to create an application context.
    
    Returns:
    - None
    
    Description:
    The function enters the application context provided by the Flask application and calls the `get_db` function to retrieve a database connection. It then checks if the same database connection is returned when `get_db` is called again within the same application context. After exiting the application
    """

    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e.value)


def test_init_db_command(runner, monkeypatch):
    """
    Function to test the 'init-db' command.
    
    This function uses the `runner` and `monkeypatch` fixtures to simulate the execution of the 'init-db' command. It replaces the `init_db` function with a mock function that sets a flag to True when called. The function then invokes the 'init-db' command and checks if the output contains the string "Initialized" and if the mock function was called.
    
    Parameters:
    - runner: The test runner object used to invoke commands.
    -
    """

    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
