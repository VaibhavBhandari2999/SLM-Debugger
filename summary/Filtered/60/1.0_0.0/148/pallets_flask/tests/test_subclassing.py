from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    Function: test_suppressed_exception_logging
    
    This function tests the logging behavior of exceptions in a Flask application when exception logging is suppressed.
    
    Key Parameters:
    - None
    
    Key Keywords:
    - None
    
    Input:
    - None
    
    Output:
    - The function does not return a value. It uses a test client to send a GET request to the root route of the Flask application and checks the response status code and content. It also checks the output of the logging stream to ensure that no exception details are logged.
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
