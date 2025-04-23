from django.forms import HiddenInput

from .base import WidgetTest


class HiddenInputTest(WidgetTest):
    widget = HiddenInput()

    def test_render(self):
        self.check_html(self.widget, 'email', '', html='<input type="hidden" name="email">')

    def test_use_required_attribute(self):
        """
        Tests the `use_required_attribute` method of the widget.
        
        This method is used to determine whether a required attribute should be
        applied to a widget. The method always returns `False` for the following
        inputs: `None`, `''` (empty string), and any non-empty string.
        
        Parameters:
        value (str or None): The value to check for the required attribute.
        
        Returns:
        bool: `False` for all inputs, indicating that the required attribute
        should not be
        """

        # Always False to avoid browser validation on inputs hidden from the
        # user.
        self.assertIs(self.widget.use_required_attribute(None), False)
        self.assertIs(self.widget.use_required_attribute(''), False)
        self.assertIs(self.widget.use_required_attribute('foo'), False)
