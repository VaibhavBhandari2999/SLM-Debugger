import pytest
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import InternalServerError
from werkzeug.exceptions import NotFound

import flask


def test_error_handler_no_match(app, client):
    """
    This function tests error handling in a Flask application. It checks for proper handling of custom exceptions, invalid error handler registrations, and HTTP errors. The function uses pytest to assert conditions and validate error responses.
    
    Parameters:
    - app (Flask): The Flask application to test.
    - client (TestClient): The test client for the Flask application.
    
    Returns:
    - None: The function asserts conditions and checks for correct error handling, no return value is expected.
    
    Key Points:
    - Registers a custom exception handler for
    """

    class CustomException(Exception):
        pass

    @app.errorhandler(CustomException)
    def custom_exception_handler(e):
        assert isinstance(e, CustomException)
        return "custom"

    with pytest.raises(TypeError) as exc_info:
        app.register_error_handler(CustomException(), None)

    assert "CustomException() is an instance, not a class." in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        app.register_error_handler(list, None)

    assert "'list' is not a subclass of Exception." in str(exc_info.value)

    @app.errorhandler(500)
    def handle_500(e):
        """
        Handle a 500 Internal Server Error.
        
        This function is designed to handle exceptions of type `InternalServerError`. It checks if the exception has an original exception wrapped within it. If so, it returns a message indicating the type of the original exception. If not, it returns a direct message.
        
        Parameters:
        e (InternalServerError): The exception object to be handled.
        
        Returns:
        str: A string indicating whether the exception was wrapped or not.
        """

        assert isinstance(e, InternalServerError)

        if e.original_exception is not None:
            return f"wrapped {type(e.original_exception).__name__}"

        return "direct"

    with pytest.raises(ValueError) as exc_info:
        app.register_error_handler(999, None)

    assert "Use a subclass of HTTPException" in str(exc_info.value)

    @app.route("/custom")
    def custom_test():
        raise CustomException()

    @app.route("/keyerror")
    def key_error():
        raise KeyError()

    @app.route("/abort")
    def do_abort():
        flask.abort(500)

    app.testing = False
    assert client.get("/custom").data == b"custom"
    assert client.get("/keyerror").data == b"wrapped KeyError"
    assert client.get("/abort").data == b"direct"


def test_error_handler_subclass(app):
    class ParentException(Exception):
        pass

    class ChildExceptionUnregistered(ParentException):
        pass

    class ChildExceptionRegistered(ParentException):
        pass

    @app.errorhandler(ParentException)
    def parent_exception_handler(e):
        assert isinstance(e, ParentException)
        return "parent"

    @app.errorhandler(ChildExceptionRegistered)
    def child_exception_handler(e):
        assert isinstance(e, ChildExceptionRegistered)
        return "child-registered"

    @app.route("/parent")
    def parent_test():
        raise ParentException()

    @app.route("/child-unregistered")
    def unregistered_test():
        raise ChildExceptionUnregistered()

    @app.route("/child-registered")
    def registered_test():
        raise ChildExceptionRegistered()

    c = app.test_client()

    assert c.get("/parent").data == b"parent"
    assert c.get("/child-unregistered").data == b"parent"
    assert c.get("/child-registered").data == b"child-registered"


def test_error_handler_http_subclass(app):
    """
    Test error handler for HTTP subclass.
    
    This function tests the error handling for HTTP subclass exceptions in a Flask application. It registers a custom subclass of the Forbidden HTTP exception and defines error handlers for both the base Forbidden exception and the custom subclass. The function then tests these handlers by raising exceptions in different routes and checking the responses.
    
    Parameters:
    app (Flask): The Flask application to test.
    
    Returns:
    None: The function asserts the expected behavior and does not return any value.
    """

    class ForbiddenSubclassRegistered(Forbidden):
        pass

    class ForbiddenSubclassUnregistered(Forbidden):
        pass

    @app.errorhandler(403)
    def code_exception_handler(e):
        assert isinstance(e, Forbidden)
        return "forbidden"

    @app.errorhandler(ForbiddenSubclassRegistered)
    def subclass_exception_handler(e):
        assert isinstance(e, ForbiddenSubclassRegistered)
        return "forbidden-registered"

    @app.route("/forbidden")
    def forbidden_test():
        raise Forbidden()

    @app.route("/forbidden-registered")
    def registered_test():
        raise ForbiddenSubclassRegistered()

    @app.route("/forbidden-unregistered")
    def unregistered_test():
        raise ForbiddenSubclassUnregistered()

    c = app.test_client()

    assert c.get("/forbidden").data == b"forbidden"
    assert c.get("/forbidden-unregistered").data == b"forbidden"
    assert c.get("/forbidden-registered").data == b"forbidden-registered"


def test_error_handler_blueprint(app):
    bp = flask.Blueprint("bp", __name__)

    @bp.errorhandler(500)
    def bp_exception_handler(e):
        """
        Handles exceptions raised by the blueprint.
        
        Args:
        e (HTTPException): The HTTPException that was raised.
        
        Returns:
        str: A default message indicating a generic error.
        
        Raises:
        AssertionError: If the provided exception is not an instance of HTTPException or NotFound.
        """

        return "bp-error"

    @bp.route("/error")
    def bp_test():
        raise InternalServerError()

    @app.errorhandler(500)
    def app_exception_handler(e):
        return "app-error"

    @app.route("/error")
    def app_test():
        raise InternalServerError()

    app.register_blueprint(bp, url_prefix="/bp")

    c = app.test_client()

    assert c.get("/error").data == b"app-error"
    assert c.get("/bp/error").data == b"bp-error"


def test_default_error_handler():
    bp = flask.Blueprint("bp", __name__)

    @bp.errorhandler(HTTPException)
    def bp_exception_handler(e):
        assert isinstance(e, HTTPException)
        assert isinstance(e, NotFound)
        return "bp-default"

    @bp.errorhandler(Forbidden)
    def bp_forbidden_handler(e):
        assert isinstance(e, Forbidden)
        return "bp-forbidden"

    @bp.route("/undefined")
    def bp_registered_test():
        raise NotFound()

    @bp.route("/forbidden")
    def bp_forbidden_test():
        raise Forbidden()

    app = flask.Flask(__name__)

    @app.errorhandler(HTTPException)
    def catchall_exception_handler(e):
        """
        Catch-all Exception Handler
        
        This function is designed to handle exceptions in a specific way, particularly HTTP exceptions and 404 Not Found errors.
        
        Parameters:
        e (HTTPException): The exception object that needs to be handled.
        
        Returns:
        str: A default string response.
        
        Raises:
        AssertionError: If the input is not an instance of HTTPException or NotFound.
        """

        assert isinstance(e, HTTPException)
        assert isinstance(e, NotFound)
        return "default"

    @app.errorhandler(Forbidden)
    def catchall_forbidden_handler(e):
        assert isinstance(e, Forbidden)
        return "forbidden"

    @app.route("/forbidden")
    def forbidden():
        raise Forbidden()

    @app.route("/slash/")
    def slash():
        return "slash"

    app.register_blueprint(bp, url_prefix="/bp")

    c = app.test_client()
    assert c.get("/bp/undefined").data == b"bp-default"
    assert c.get("/bp/forbidden").data == b"bp-forbidden"
    assert c.get("/undefined").data == b"default"
    assert c.get("/forbidden").data == b"forbidden"
    # Don't handle RequestRedirect raised when adding slash.
    assert c.get("/slash", follow_redirects=True).data == b"slash"


class TestGenericHandlers:
    """Test how very generic handlers are dispatched to."""

    class Custom(Exception):
        pass

    @pytest.fixture()
    def app(self, app):
        @app.route("/custom")
        def do_custom():
            raise self.Custom()

        @app.route("/error")
        def do_error():
            raise KeyError()

        @app.route("/abort")
        def do_abort():
            flask.abort(500)

        @app.route("/raise")
        def do_raise():
            raise InternalServerError()

        app.config["PROPAGATE_EXCEPTIONS"] = False
        return app

    def report_error(self, e):
        """
        Generate a report of an error.
        
        This function takes an exception `e` and returns a string describing the type of the error. If the exception has an `original_exception` attribute, it returns a message indicating that the error was wrapped and the type of the original exception. Otherwise, it returns a message indicating that the error was direct and the type of the exception.
        
        Parameters:
        e (Exception): The exception object to report.
        
        Returns:
        str: A string describing the type of the error
        """

        original = getattr(e, "original_exception", None)

        if original is not None:
            return f"wrapped {type(original).__name__}"

        return f"direct {type(e).__name__}"

    @pytest.mark.parametrize("to_handle", (InternalServerError, 500))
    def test_handle_class_or_code(self, app, client, to_handle):
        """``InternalServerError`` and ``500`` are aliases, they should
        have the same behavior. Both should only receive
        ``InternalServerError``, which might wrap another error.
        """

        @app.errorhandler(to_handle)
        def handle_500(e):
            assert isinstance(e, InternalServerError)
            return self.report_error(e)

        assert client.get("/custom").data == b"wrapped Custom"
        assert client.get("/error").data == b"wrapped KeyError"
        assert client.get("/abort").data == b"direct InternalServerError"
        assert client.get("/raise").data == b"direct InternalServerError"

    def test_handle_generic_http(self, app, client):
        """``HTTPException`` should only receive ``HTTPException``
        subclasses. It will receive ``404`` routing exceptions.
        """

        @app.errorhandler(HTTPException)
        def handle_http(e):
            assert isinstance(e, HTTPException)
            return str(e.code)

        assert client.get("/error").data == b"500"
        assert client.get("/abort").data == b"500"
        assert client.get("/not-found").data == b"404"

    def test_handle_generic(self, app, client):
        """Generic ``Exception`` will handle all exceptions directly,
        including ``HTTPExceptions``.
        """

        @app.errorhandler(Exception)
        def handle_exception(e):
            return self.report_error(e)

        assert client.get("/custom").data == b"direct Custom"
        assert client.get("/error").data == b"direct KeyError"
        assert client.get("/abort").data == b"direct InternalServerError"
        assert client.get("/not-found").data == b"direct NotFound"
