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
    Tests the response of the given path using the provided client. It checks if the rendered template matches the expected template name.
    
    :param app: The Flask application to test.
    :param client: The Flask test client to use for making requests.
    :param path: The URL path to test.
    :param template_name: The expected name of the template to be rendered.
    :type app: Flask
    :type client: FlaskClient
    :type path: str
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
