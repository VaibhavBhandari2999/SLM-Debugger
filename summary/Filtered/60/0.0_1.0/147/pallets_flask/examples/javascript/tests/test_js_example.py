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
    Tests the response of the index view.
    
    This function sends a GET request to the specified path using the provided client and checks if the rendered template matches the expected template name.
    
    Parameters:
    app (Flask): The Flask application to test.
    client: The test client to send the request.
    path (str): The URL path to test.
    template_name (str): The expected name of the template to be rendered.
    
    Returns:
    None: This function does not return anything. It relies
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
