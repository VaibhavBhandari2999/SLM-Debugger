"""
The provided Python file contains a Django test case class named `TestTemplates` that focuses on testing the escaping of JavaScript strings within inline admin formset data. Specifically, it ensures that the formset data, which includes a JSON string with a prefix and a verbose name, is correctly escaped to prevent potential JavaScript injection vulnerabilities. The test uses the `render_to_string` method from Django's template loader to render the formset data into HTML and then checks if the necessary escape sequences are present in the generated HTML for both the stacked and tabular inline admin templates.

#### Main Components:
- **Class**: `TestTemplates` - A subclass of `SimpleTestCase` designed to test the escaping of JavaScript strings in inline admin formset data.
- **Function
"""
import json

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class TestTemplates(SimpleTestCase):
    def test_javascript_escaping(self):
        """
        Tests the escaping of JavaScript strings in the inline admin formset data.
        
        This function checks that the inline admin formset data is properly escaped
        when rendered into HTML using `render_to_string`. The data includes a JSON
        string with a prefix and a verbose name, both of which are expected to be
        correctly escaped to prevent JavaScript injection attacks. The function
        verifies that the escape sequences are present in the generated HTML for
        both the stacked and tabular inline admin templates
        """

        context = {
            'inline_admin_formset': {
                'inline_formset_data': json.dumps({
                    'formset': {'prefix': 'my-prefix'},
                    'opts': {'verbose_name': 'verbose name\\'},
                }),
            },
        }
        output = render_to_string('admin/edit_inline/stacked.html', context)
        self.assertIn('&quot;prefix&quot;: &quot;my-prefix&quot;', output)
        self.assertIn('&quot;verbose_name&quot;: &quot;verbose name\\\\&quot;', output)

        output = render_to_string('admin/edit_inline/tabular.html', context)
        self.assertIn('&quot;prefix&quot;: &quot;my-prefix&quot;', output)
        self.assertIn('&quot;verbose_name&quot;: &quot;verbose name\\\\&quot;', output)
