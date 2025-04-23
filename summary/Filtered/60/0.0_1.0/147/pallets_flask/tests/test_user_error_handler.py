import pytest
from werkzeug.exceptions import Forbidden
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import InternalServerError
from werkzeug.exceptions import NotFound

import flask


def test_error_handler_no_match(app, client):
    """
    This function tests the error handling mechanism in a Flask application. It includes specific error handlers for custom exceptions and generic HTTP errors. The function checks that custom exceptions are properly handled and that generic errors are wrapped and handled correctly. It also ensures that unacceptable custom exceptions are caught and an assertion error is raised.
    
    Parameters:
    app (Flask): The Flask application to test.
    client (TestClient): The test client for the Flask application.
    
    Returns:
    None: This function does not return anything.
    """

    class CustomException(Exception):
        pass

    class UnacceptableCustomException(BaseException):
        pass

    @app.errorhandler(CustomException)
    def custom_exception_handler(e):
        assert isinstance(e, CustomException)
        return "custom"

    with pytest.raises(
        AssertionError, match="Custom exceptions must be subclasses of Exception."
    ):
        app.register_error_handler(UnacceptableCustomException, None)

    @app.errorhandler(500)
    def handle_500(e):
        """
        Handle a 500 Internal Server Error.
        
        This function is designed to handle exceptions of type `InternalServerError`. It checks if the exception has an `original_exception` attribute and returns a string indicating whether the error was wrapped or not. If no original exception is found, it returns a default message.
        
        Parameters:
        e (InternalServerError): The exception object to be handled.
        
        Returns:
        str: A string indicating whether the error was wrapped or not.
        """

        assert isinstance(e, InternalServerError)
        original = getattr(e, "original_exception", None)

        if original is not None:
            return f"wrapped {type(original).__name__}"

        return "direct"

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
    """
    Tests error handling for exceptions, ensuring that parent exceptions are handled correctly and child exceptions are routed to specific handlers. The function sets up an application with error handlers for a parent exception and a child exception. It then defines routes that raise these exceptions and checks that the correct responses are returned for each route.
    
    Parameters:
    app (Flask): The Flask application to configure and test.
    
    Returns:
    None: The function asserts the expected behavior through HTTP requests and does not return any value.
    """

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
    """
    This function sets up a Flask application with a blueprint and custom error handlers.
    
    Parameters:
    app (Flask): The Flask application to which the blueprint and error handlers will be added.
    
    Returns:
    None: The function modifies the provided Flask application in place.
    
    Key Steps:
    1. Creates a Flask blueprint named 'bp'.
    2. Defines a custom error handler for 500 errors within the blueprint, returning 'bp-error'.
    3. Registers a route '/error' within the blueprint that raises
    """

    bp = flask.Blueprint("bp", __name__)

    @bp.errorhandler(500)
    def bp_exception_handler(e):
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
        """
        This function configures a Flask application with custom routes for handling different types of errors and exceptions.
        
        Parameters:
        app (Flask): The Flask application to configure.
        
        Returns:
        Flask: The configured Flask application with custom routes.
        
        Key Routes:
        - /custom: Raises a custom exception.
        - /error: Raises a KeyError.
        - /abort: Aborts the request with a 500 Internal Server Error.
        - /raise: Raises an InternalServerError.
        
        Note:
        - The application's `
        """

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
