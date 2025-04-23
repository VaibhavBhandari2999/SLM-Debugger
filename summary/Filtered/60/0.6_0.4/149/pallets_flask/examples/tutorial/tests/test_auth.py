import pytest
from flask import g
from flask import session

from flaskr.db import get_db


def test_register(client, app):
    """
    Tests the registration functionality of the application.
    
    This function checks the behavior of the user registration process. It verifies that the registration page can be accessed without errors and that a successful registration redirects to the login page. Additionally, it ensures that the newly registered user is correctly stored in the database.
    
    Parameters:
    client (TestClient): The test client used to make HTTP requests.
    app (Flask): The Flask application context.
    
    Returns:
    None: This function does not return any value. It asserts
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
    """
    Tests the login functionality of the application.
    
    This function checks the behavior of the login page and the login process. It ensures that:
    - Viewing the login page does not result in template errors.
    - A successful login redirects the user to the index page.
    - The user's ID is stored in the session after a successful login.
    - The user's username is correctly retrieved from the session.
    
    Parameters:
    - client: The test client for the application.
    - auth: An object that provides methods for authenticating
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
    Logout the current user from the session.
    
    This function logs out the currently logged-in user by removing the 'user_id' from the session. It is typically used after a user has completed their session or when they choose to log out.
    
    Parameters:
    client (Flask test client): The Flask test client used for testing.
    auth (Auth object): An object that provides methods for user authentication.
    
    Returns:
    None: This function does not return anything. It modifies the session directly.
    
    Usage:
    """

    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
