from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function: test_suppressed_exception_logging
    
    This function tests the logging behavior of a Flask application when exceptions are suppressed.
    
    Key Parameters:
    - None
    
    Key Keywords:
    - None
    
    Inputs:
    - None
    
    Outputs:
    - None
    
    Description:
    The function creates a suppressed Flask application and defines a route that raises an exception. It then makes a GET request to this route and checks if the response status code is 500 (Internal Server Error) and if the response data contains the expected error message
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
