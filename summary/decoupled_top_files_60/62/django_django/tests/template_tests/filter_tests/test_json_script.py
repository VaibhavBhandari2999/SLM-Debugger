from django.test import SimpleTestCase

from ..utils import setup


class JsonScriptTests(SimpleTestCase):

    @setup({'json-tag01': '{{ value|json_script:"test_id" }}'})
    def test_basic(self):
        """
        Tests the rendering of a JSON string with special characters.
        
        This function tests the rendering of a JSON string that contains special characters, including newlines, single quotes, double quotes, and HTML tags. The test checks if the rendered output correctly escapes these characters and formats them as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Input:
        - A dictionary with a single key-value pair. The key is 'value' and the value is a dictionary containing a single key 'a' with a
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
