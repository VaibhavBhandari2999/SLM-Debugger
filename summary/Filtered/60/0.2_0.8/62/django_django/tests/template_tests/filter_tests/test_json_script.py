from django.test import SimpleTestCase

from ..utils import setup


class JsonScriptTests(SimpleTestCase):

    @setup({'json-tag01': '{{ value|json_script:"test_id" }}'})
    def test_basic(self):
        """
        Render a JSON string template with a dictionary containing a nested dictionary. The function takes a template name and a dictionary with a single key 'value' whose value is a nested dictionary. The nested dictionary contains a key 'a' with a string value that includes special characters such as newline, single quote, double quote, and HTML tags. The function renders the template, escaping these special characters appropriately. The output is a script tag with the type set to 'application/json' containing the escaped JSON string.
        """

        output = self.engine.render_to_string(
            'json-tag01',
            {'value': {'a': 'testing\r\njson \'string" <b>escaping</b>'}}
        )
        self.assertEqual(
            output,
            '<script id="test_id" type="application/json">'
            '{"a": "testing\\r\\njson \'string\\" \\u003Cb\\u003Eescaping\\u003C/b\\u003E"}'
            '</script>'
        )
