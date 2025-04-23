from io import StringIO

import flask


def test_suppressed_exception_logging():
    """
    This function tests the logging behavior of exceptions in a Flask application when exceptions are suppressed.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - A custom Flask class `SuppressedFlask` is defined, which overrides the `log_exception` method to suppress logging of exceptions.
    - An instance of `SuppressedFlask` is created.
    - A route `/` is defined with a view function `index` that raises an exception.
    - The test client of the Flask application is used
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
