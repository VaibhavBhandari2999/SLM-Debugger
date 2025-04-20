import pytest
from flask import g
from flask import session

from flaskr.db import get_db


def test_register(client, app):
    """
    Tests the registration functionality of the application.
    
    This function performs several checks to ensure that the registration process works as expected:
    - Verifies that the registration page is accessible (status code 200).
    - Checks that a successful registration redirects to the login page.
    - Ensures that the newly registered user is stored in the database.
    
    Parameters:
    - client: The test client used to make HTTP requests.
    - app: The application context for the test.
    
    Returns:
    - None: This function does not return
    """

    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "a"})
    assert "http://localhost/auth/login" == response.headers["Location"]

    # test that the user was inserted into the database
    with app.app_context():
        assert (
            get_db().execute("select * from user where username = 'a'").fetchone()
            is not None
        )


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required."),
        ("a", "", b"Password is required."),
        ("test", "test", b"already registered"),
    ),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "http://localhost/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", b"Incorrect username."), ("test", "a", b"Incorrect password.")),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    """
    Logout the current user from the application.
    
    This function logs out the currently authenticated user. It requires a Flask test client and an authentication object to be passed in. The test client is used to simulate a web request, and the authentication object is used to handle the login and logout process.
    
    Parameters:
    client (Flask test client): A test client for the Flask application.
    auth (Auth object): An authentication object that handles login and logout.
    
    Returns:
    None: This function does not return
    """

    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
t in session
