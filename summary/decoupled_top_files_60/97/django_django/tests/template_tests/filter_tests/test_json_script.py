from django.test import SimpleTestCase

from ..utils import setup


class JsonScriptTests(SimpleTestCase):
    @setup({"json-tag01": '{{ value|json_script:"test_id" }}'})
    def test_basic(self):
        """
        Tests the basic functionality of the `render_to_string` method with a JSON template.
        
        Args:
        self: The test case instance.
        
        This method tests the `render_to_string` method of the `engine` object by passing a JSON template and a context dictionary containing a string with special characters. The method expects the rendered output to be a script tag with the specified JSON content, properly escaped.
        
        Returns:
        None: The method asserts the expected output against the actual output.
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
