import sqlite3

import pytest

from flaskr.db import get_db


def test_get_close_db(app):
    """
    Summary:
    This function tests the behavior of the `get_close_db` function, which is expected to return the database connection in the context of the application and close it outside of the context.
    
    Parameters:
    - app: The Flask application object used to set the application context.
    
    Returns:
    - None
    
    Key Points:
    - The function sets the application context using `app.app_context()`.
    - It calls `get_db()` to obtain the database connection.
    - It asserts that the same database connection is returned by
    """

    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder:
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("flaskr.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
