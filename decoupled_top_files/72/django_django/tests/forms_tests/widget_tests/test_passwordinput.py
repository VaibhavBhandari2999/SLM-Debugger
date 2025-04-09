"""
```markdown
This file contains tests for the Django `PasswordInput` widget. It defines a single test class `PasswordInputTest` which inherits from `WidgetTest`. The class includes three test methods:

1. `test_render`: Verifies that the widget renders an input field with the correct type and name attributes.
2. `test_render_ignore_value`: Ensures that the widget does not render the value by default, even if provided.
3. `test_render_value_true`: Tests the behavior when `render_value` is set to `True`, allowing the value to be rendered.

The `PasswordInput` widget itself is instantiated within these tests to verify its rendering behavior under different conditions.
```

### Explanation:
- **Purpose**: The file
"""
from django.forms import PasswordInput

from .base import WidgetTest


class PasswordInputTest(WidgetTest):
    widget = PasswordInput()

    def test_render(self):
        self.check_html(self.widget, 'password', '', html='<input type="password" name="password">')

    def test_render_ignore_value(self):
        self.check_html(self.widget, 'password', 'secret', html='<input type="password" name="password">')

    def test_render_value_true(self):
        """
        The render_value argument lets you specify whether the widget should
        render its value. For security reasons, this is off by default.
        """
        widget = PasswordInput(render_value=True)
        self.check_html(widget, 'password', '', html='<input type="password" name="password">')
        self.check_html(widget, 'password', None, html='<input type="password" name="password">')
        self.check_html(
            widget, 'password', 'test@example.com',
            html='<input type="password" name="password" value="test@example.com">',
        )
