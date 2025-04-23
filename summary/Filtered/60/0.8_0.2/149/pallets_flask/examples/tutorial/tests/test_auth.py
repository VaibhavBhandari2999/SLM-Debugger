import pytest
from flask import g
from flask import session

from flaskr.db import get_db


def test_register(client, app):
    """
    Tests the registration functionality of the application.
    
    This function checks the registration process by ensuring that the registration page can be accessed and that a new user can be successfully registered. It also verifies that the user is redirected to the login page after registration and that the user is correctly added to the database.
    
    Parameters:
    client (TestClient): The test client for the Flask application.
    app (Flask): The Flask application instance.
    
    Returns:
    None: This function does not return anything. It performs assertions
    """

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
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.data


def test_login(client, auth):
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
    Logs out the current user from the application.
    
    This function simulates a user logout process. It first logs in the user using the `auth.login()` method. Then, it logs out the user using `auth.logout()`. After logging out, it checks if the 'user_id' is not present in the session, indicating a successful logout.
    
    Parameters:
    client (Flask test client): The Flask test client used for making requests.
    auth (Authenticator): An instance of the Authenticator
    """

    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
