from django.test import SimpleTestCase

from ..utils import setup


class JsonScriptTests(SimpleTestCase):

    @setup({'json-tag01': '{{ value|json_script:"test_id" }}'})
    def test_basic(self):
        """
        Tests the rendering of a JSON template with a complex string value.
        
        This function tests the `render_to_string` method of the `engine` object by passing a template named 'json-tag01' and a dictionary containing a complex JSON string. The dictionary has a single key 'value' with a nested dictionary as its value. The nested dictionary contains a key 'a' with a string that includes special characters such as newline, single quotes, double quotes, and HTML tags.
        
        Parameters:
        None
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
