import pytest
from flask import g
from flask import session

from flaskr.db import get_db


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "a"})
    assert response.headers["Location"] == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'a'").fetchone()
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
    Function to test the validation of input during user registration.
    
    This function sends a POST request to the '/auth/register' endpoint with the provided username and password. It then checks if the response contains the specified message, indicating that the input validation was successful.
    
    Parameters:
    client (TestClient): The test client used to send the request.
    username (str): The username to be used for registration.
    password (str): The password to be used for registration.
    message (str): The expected
    """

    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client, auth):
    """
    Function to test the login functionality in the application.
    
    This function tests the login page and the login process. It verifies that:
    1. Viewing the login page does not result in template errors.
    2. A successful login redirects to the index page.
    3. After a successful login, the user ID is stored in the session.
    4. The user's username is correctly retrieved from the session.
    
    Parameters:
    client (TestClient): The test client for the application.
    auth (Auth): An object
    """

    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "/"

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
    
    This function logs out a user who is currently logged in. It takes a Flask test client and an authentication helper as arguments. The user must be logged in before calling this function. After the logout, the function asserts that the 'user_id' is no longer present in the session, indicating a successful logout.
    
    Parameters:
    client (Flask test client): The Flask test client used for making requests.
    auth (Auth helper): An authentication helper object used for
    """

    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
