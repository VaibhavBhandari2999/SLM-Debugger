from django.test import SimpleTestCase

from ..utils import setup


class JsonScriptTests(SimpleTestCase):
    @setup({"json-tag01": '{{ value|json_script:"test_id" }}'})
    def test_basic(self):
        """
        Tests the basic functionality of the `render_to_string` method.
        
        This test checks if the `render_to_string` method correctly renders a JSON string with special characters and tags. The method takes a template name and a dictionary of context variables as input. The context variable 'value' contains a JSON object with a string that includes newlines, single and double quotes, and HTML tags. The expected output is a script tag with the JSON string properly escaped and formatted.
        
        Parameters:
        self: The test
        """

        output = self.engine.render_to_string(
            "json-tag01", {"value": {"a": "testing\r\njson 'string\" <b>escaping</b>"}}
        )
        self.assertEqual(
            output,
            '<script id="test_id" type="application/json">'
            '{"a": "testing\\r\\njson \'string\\" '
            '\\u003Cb\\u003Eescaping\\u003C/b\\u003E"}'
            "</script>",
        )

    @setup({"json-tag02": "{{ value|json_script }}"})
    def test_without_id(self):
        output = self.engine.render_to_string("json-tag02", {"value": {}})
        self.assertEqual(output, '<script type="application/json">{}</script>')
