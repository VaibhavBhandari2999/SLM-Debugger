from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function to test exception logging suppression in a Flask application.
    
    This function sets up a Flask application with a suppressed exception logging mechanism. It then defines a route that raises an exception and makes a GET request to this route. The function checks the response status code and content, as well as the logging output.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - A `SuppressedFlask` class is defined to suppress exception logging.
    - An exception is raised in the route handler
    """

    class SuppressedFlask(flask.Flask):
        def log_exception(self, exc_info):
            pass

    out = StringIO()
    app = SuppressedFlask(__name__)

    @app.route("/")
    def index():
        raise Exception("test")

    rv = app.test_client().get("/", errors_stream=out)
    assert rv.status_code == 500
    assert b"Internal Server Error" in rv.data
    assert not out.getvalue()
