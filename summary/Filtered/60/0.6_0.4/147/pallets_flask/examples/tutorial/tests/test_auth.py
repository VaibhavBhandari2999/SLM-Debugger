import pytest
from flask import g
from flask import session

from flaskr.db import get_db


def test_register(client, app):
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
    """
    Validate user registration input.
    
    This function sends a POST request to the '/auth/register' endpoint with the provided username and password. It checks if the response contains the specified message, indicating whether the input validation was successful or not.
    
    Parameters:
    client (TestClient): The test client used to send the request.
    username (str): The username to be registered.
    password (str): The password to be used for registration.
    message (str): The expected message to be found in the response
    """

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
    Logout a user from the application.
    
    This function logs out a user who is currently logged in. It requires a Flask test client and an authentication object. The function logs in the user first and then logs them out. After logging out, it checks if the 'user_id' is not present in the session, indicating a successful logout.
    
    Parameters:
    client (Flask test client): The Flask test client used for making requests.
    auth (Auth object): An authentication object that provides methods for logging
    """

    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
