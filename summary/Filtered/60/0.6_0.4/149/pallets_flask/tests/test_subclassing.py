from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    This function tests the logging behavior of exceptions in a Flask application when exceptions are suppressed.
    
    Key Parameters:
    - None
    
    Key Keywords:
    - None
    
    Inputs:
    - None
    
    Outputs:
    - None
    
    The function creates a custom Flask application that suppresses logging of exceptions. It then raises an exception in a route and checks if the exception is logged and if the response status and content are as expected.
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
