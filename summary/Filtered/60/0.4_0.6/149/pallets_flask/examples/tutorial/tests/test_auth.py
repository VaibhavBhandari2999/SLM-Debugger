import pytest
from flask import g
from flask import session

from flaskr.db import get_db


def test_register(client, app):
    """
    Tests the registration functionality of the application.
    
    This function checks the registration process of the application. It first ensures that the registration page can be accessed without errors. Then, it tests that a successful registration redirects the user to the login page. Finally, it verifies that the newly registered user is stored in the database.
    
    Parameters:
    - client: The test client used to simulate HTTP requests.
    - app: The application context for the test.
    
    Returns:
    - None: This function does not return anything. It performs
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
    """
    Function to test the validation of input during user registration.
    
    Args:
    client (TestClient): The test client for making HTTP requests.
    username (str): The username to be tested.
    password (str): The password to be tested.
    message (str): The expected error message if the input is invalid.
    
    Returns:
    None: This function asserts that the expected error message is present in the response data.
    
    Example:
    >>> test_register_validate_input(client, "test_user", "weak
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
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
