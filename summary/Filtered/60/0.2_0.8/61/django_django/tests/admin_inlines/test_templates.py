import json

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class TestTemplates(SimpleTestCase):
    def test_javascript_escaping(self):
        """
        Tests the escaping of JavaScript strings in the inline admin formset data.
        
        This function checks that the inline admin formset data is properly escaped when rendered in both stacked and tabular inline admin templates. It ensures that the JSON data is correctly formatted with escaped double quotes and backslashes.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The output contains the expected JSON data with properly escaped double quotes and backslashes in both the stacked and tabular templates.
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
