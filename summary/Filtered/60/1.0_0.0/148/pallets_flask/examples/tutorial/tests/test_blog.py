import pytest

from flaskr.db import get_db


def test_index(client, auth):
    """
    Tests the index route of the application. It checks if the page is accessible and contains the expected elements. If the user is logged in, it also verifies that the page displays the correct title, author, and body of the test post, as well as the update link.
    
    Parameters:
    - client: The test client used to make HTTP requests to the application.
    - auth: An authentication helper object to log in the test user.
    
    Returns:
    - None: The function asserts the expected behavior and does not
    """

    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"test title" in response.data
    assert b"by test on 2018-01-01" in response.data
    assert b"test\nbody" in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"


@pytest.mark.parametrize("path", ("/create", "/1/update"))
def test_create_update_validate(client, auth, path):
    """
    Function to test the creation, updating, and validation of content.
    
    This function is designed to test the creation and updating of content via a POST request to a specified path. It also validates the content by checking for required fields.
    
    Parameters:
    client (TestClient): The test client used for making HTTP requests.
    auth (Auth): Authentication helper for logging in the user.
    path (str): The URL path to which the POST request is sent.
    
    Returns:
    None: This function does not
    """

    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None
