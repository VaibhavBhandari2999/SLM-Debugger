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
    
    The function creates a Flask application with a suppressed exception logging mechanism. It defines a route that raises an exception and then makes a GET request to this route using the test client. The function checks that the response status code is 500 (Internal Server Error) and that the response data contains the expected
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
