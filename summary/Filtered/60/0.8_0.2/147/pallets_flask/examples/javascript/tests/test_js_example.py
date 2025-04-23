import pytest
from flask import template_rendered


@pytest.mark.parametrize(
    ("path", "template_name"),
    (
        ("/", "plain.html"),
        ("/plain", "plain.html"),
        ("/fetch", "fetch.html"),
        ("/jquery", "jquery.html"),
    ),
)
def test_index(app, client, path, template_name):
    """
    Tests the index view of a Flask application.
    
    This function sends a GET request to the specified path and checks if the rendered template matches the expected template name.
    
    Parameters:
    app (Flask): The Flask application instance.
    client: The test client for the Flask application.
    path (str): The URL path to the view being tested.
    template_name (str): The expected name of the template to be rendered.
    
    Returns:
    None: This function does not return anything. It relies on
    """

    def check(sender, template, context):
        assert template.name == template_name

    with template_rendered.connected_to(check, app):
        client.get(path)


@pytest.mark.parametrize(
    ("a", "b", "result"), ((2, 3, 5), (2.5, 3, 5.5), (2, None, 2), (2, "b", 2))
)
def test_add(client, a, b, result):
    response = client.post("/add", data={"a": a, "b": b})
    assert response.get_json()["result"] == result
