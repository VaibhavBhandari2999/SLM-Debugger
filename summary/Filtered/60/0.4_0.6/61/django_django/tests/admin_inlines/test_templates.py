import json

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class TestTemplates(SimpleTestCase):
    def test_javascript_escaping(self):
        """
        Tests the escaping of JavaScript strings in the inline admin formset data.
        
        This function renders the 'admin/edit_inline/stacked.html' and 'admin/edit_inline/tabular.html' templates with a context containing an inline admin formset. The formset data includes a JSON string with a prefix and a verbose name that contains an escape sequence. The function checks that the rendered output correctly escapes the JavaScript strings.
        
        Parameters:
        - None (the function uses a predefined context)
        
        Returns:
        - None (the function
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
