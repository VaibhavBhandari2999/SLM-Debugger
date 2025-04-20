import json
import os
import textwrap
from datetime import timedelta

import pytest

import flask


# config keys used for the TestConfig
TEST_KEY = "foo"
SECRET_KEY = "config"


def common_object_test(app):
    assert app.secret_key == "config"
    assert app.config["TEST_KEY"] == "foo"
    assert "TestConfig" not in app.config


def test_config_from_pyfile():
    """
    Tests configuration loading from a Python file.
    
    This function loads configuration settings from a specified Python file and applies them to a Flask application. The configuration is loaded using the `from_pyfile` method of the Flask application object.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The configuration file is expected to be located in the same directory as this function and should have the same name as this function with a `.py` extension.
    - The `common_object_test` function is called
    """

    app = flask.Flask(__name__)
    app.config.from_pyfile(f"{__file__.rsplit('.', 1)[0]}.py")
    common_object_test(app)


def test_config_from_object():
    app = flask.Flask(__name__)
    app.config.from_object(__name__)
    common_object_test(app)


def test_config_from_file():
    """
    Load configuration settings from a JSON file and apply them to a Flask application.
    
    This function initializes a Flask application, sets the current directory, and loads configuration settings from a JSON file named 'config.json' located in the 'static' directory. The loaded configuration is then applied to the Flask application.
    
    Parameters:
    None
    
    Returns:
    None
    """

    app = flask.Flask(__name__)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app.config.from_file(os.path.join(current_dir, "static", "config.json"), json.load)
    common_object_test(app)


def test_config_from_mapping():
    """
    This function tests the configuration of a Flask application using different methods of setting configuration values. It creates a Flask app and sets configuration values using `from_mapping` method in three different ways: passing a dictionary, a list of tuples, and keyword arguments. After setting the configurations, a common test function `common_object_test` is called to perform further checks. The function also includes a test case to ensure that passing two dictionaries to `from_mapping` raises a TypeError.
    
    Parameters:
    - app (Flask
    """

    app = flask.Flask(__name__)
    app.config.from_mapping({"SECRET_KEY": "config", "TEST_KEY": "foo"})
    common_object_test(app)

    app = flask.Flask(__name__)
    app.config.from_mapping([("SECRET_KEY", "config"), ("TEST_KEY", "foo")])
    common_object_test(app)

    app = flask.Flask(__name__)
    app.config.from_mapping(SECRET_KEY="config", TEST_KEY="foo")
    common_object_test(app)

    app = flask.Flask(__name__)
    with pytest.raises(TypeError):
        app.config.from_mapping({}, {})


def test_config_from_class():
    class Base:
        TEST_KEY = "foo"

    class Test(Base):
        SECRET_KEY = "config"

    app = flask.Flask(__name__)
    app.config.from_object(Test)
    common_object_test(app)


def test_config_from_envvar(monkeypatch):
    """
    Test configuration loading from environment variables.
    
    This function tests the behavior of loading configuration from environment variables in a Flask application. It uses `monkeypatch` to simulate different environment settings and checks the outcome.
    
    Parameters:
    monkeypatch (pytest.MonkeyPatch): A fixture used to modify the environment during the test.
    
    Returns:
    None: The function asserts the expected behavior through `pytest.raises` and `assert` statements.
    
    Key Steps:
    1. Set the environment to an empty dictionary and attempt to load configuration
    """

    monkeypatch.setattr("os.environ", {})
    app = flask.Flask(__name__)
    with pytest.raises(RuntimeError) as e:
        app.config.from_envvar("FOO_SETTINGS")
        assert "'FOO_SETTINGS' is not set" in str(e.value)
    assert not app.config.from_envvar("FOO_SETTINGS", silent=True)

    monkeypatch.setattr(
        "os.environ", {"FOO_SETTINGS": f"{__file__.rsplit('.', 1)[0]}.py"}
    )
    assert app.config.from_envvar("FOO_SETTINGS")
    common_object_test(app)


def test_config_from_envvar_missing(monkeypatch):
    monkeypatch.setattr("os.environ", {"FOO_SETTINGS": "missing.cfg"})
    with pytest.raises(IOError) as e:
        app = flask.Flask(__name__)
        app.config.from_envvar("FOO_SETTINGS")
    msg = str(e.value)
    assert msg.startswith(
        "[Errno 2] Unable to load configuration file (No such file or directory):"
    )
    assert msg.endswith("missing.cfg'")
    assert not app.config.from_envvar("FOO_SETTINGS", silent=True)


def test_config_missing():
    app = flask.Flask(__name__)
    with pytest.raises(IOError) as e:
        app.config.from_pyfile("missing.cfg")
    msg = str(e.value)
    assert msg.startswith(
        "[Errno 2] Unable to load configuration file (No such file or directory):"
    )
    assert msg.endswith("missing.cfg'")
    assert not app.config.from_pyfile("missing.cfg", silent=True)


def test_config_missing_file():
    app = flask.Flask(__name__)
    with pytest.raises(IOError) as e:
        app.config.from_file("missing.json", load=json.load)
    msg = str(e.value)
    assert msg.startswith(
        "[Errno 2] Unable to load configuration file (No such file or directory):"
    )
    assert msg.endswith("missing.json'")
    assert not app.config.from_file("missing.json", load=json.load, silent=True)


def test_custom_config_class():
    class Config(flask.Config):
        pass

    class Flask(flask.Flask):
        config_class = Config

    app = Flask(__name__)
    assert isinstance(app.config, Config)
    app.config.from_object(__name__)
    common_object_test(app)


def test_session_lifetime():
    """
    Function to test the session lifetime configuration in a Flask application.
    
    This function sets up a Flask application with a specified permanent session lifetime and checks if the configured lifetime matches the expected value.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - app: A Flask application object.
    
    Keywords:
    - app.config["PERMANENT_SESSION_LIFETIME"]: The configuration key for setting the session lifetime in seconds.
    
    Details:
    The function configures the `PERMANENT_SESSION_LIFETIME
    """

    app = flask.Flask(__name__)
    app.config["PERMANENT_SESSION_LIFETIME"] = 42
    assert app.permanent_session_lifetime.seconds == 42


def test_send_file_max_age():
    """
    Tests the configuration of the `SEND_FILE_MAX_AGE_DEFAULT` in a Flask application.
    
    This function sets the `SEND_FILE_MAX_AGE_DEFAULT` configuration in a Flask application and checks if the value is correctly set. It first sets the configuration to an integer representing seconds and then to a `timedelta` object representing hours.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - Sets the `SEND_FILE_MAX_AGE_DEFAULT` configuration to 3600 seconds and
    """

    app = flask.Flask(__name__)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600
    assert app.send_file_max_age_default.seconds == 3600
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = timedelta(hours=2)
    assert app.send_file_max_age_default.seconds == 7200


def test_get_namespace():
    app = flask.Flask(__name__)
    app.config["FOO_OPTION_1"] = "foo option 1"
    app.config["FOO_OPTION_2"] = "foo option 2"
    app.config["BAR_STUFF_1"] = "bar stuff 1"
    app.config["BAR_STUFF_2"] = "bar stuff 2"
    foo_options = app.config.get_namespace("FOO_")
    assert 2 == len(foo_options)
    assert "foo option 1" == foo_options["option_1"]
    assert "foo option 2" == foo_options["option_2"]
    bar_options = app.config.get_namespace("BAR_", lowercase=False)
    assert 2 == len(bar_options)
    assert "bar stuff 1" == bar_options["STUFF_1"]
    assert "bar stuff 2" == bar_options["STUFF_2"]
    foo_options = app.config.get_namespace("FOO_", trim_namespace=False)
    assert 2 == len(foo_options)
    assert "foo option 1" == foo_options["foo_option_1"]
    assert "foo option 2" == foo_options["foo_option_2"]
    bar_options = app.config.get_namespace(
        "BAR_", lowercase=False, trim_namespace=False
    )
    assert 2 == len(bar_options)
    assert "bar stuff 1" == bar_options["BAR_STUFF_1"]
    assert "bar stuff 2" == bar_options["BAR_STUFF_2"]


@pytest.mark.parametrize("encoding", ["utf-8", "iso-8859-15", "latin-1"])
def test_from_pyfile_weird_encoding(tmpdir, encoding):
    f = tmpdir.join("my_config.py")
    f.write_binary(
        textwrap.dedent(
            f"""
            # -*- coding: {encoding} -*-
            TEST_VALUE = "föö"
            """
        ).encode(encoding)
    )
    app = flask.Flask(__name__)
    app.config.from_pyfile(str(f))
    value = app.config["TEST_VALUE"]
    assert value == "föö"

