import json

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class TestTemplates(SimpleTestCase):
    def test_javascript_escaping(self):
        """
        Tests the escaping of JavaScript strings in the inline admin formset data.
        
        This function checks that the JavaScript escaping is correctly applied to the inline formset data, ensuring that special characters are properly escaped. It renders the formset data in both stacked and tabular HTML formats and verifies that the escaping is consistent across both formats.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The rendered output contains the expected escaped strings for 'prefix' and 'verbose_name'.
        - The escaping is
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
