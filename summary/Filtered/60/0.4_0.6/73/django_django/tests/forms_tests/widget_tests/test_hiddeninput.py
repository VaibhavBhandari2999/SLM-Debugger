from django.forms import HiddenInput

from .base import WidgetTest


class HiddenInputTest(WidgetTest):
    widget = HiddenInput()

    def test_render(self):
        self.check_html(self.widget, 'email', '', html='<input type="hidden" name="email">')

    def test_use_required_attribute(self):
        """
        Tests the `use_required_attribute` method of the widget.
        
        This method is used to determine whether a required attribute should be used
        for a widget. The method returns `False` for all inputs, including `None`, an
        empty string, and a non-empty string.
        
        Parameters:
        value (str or None): The value to check for the required attribute.
        
        Returns:
        bool: `False` for all inputs.
        """

        # Always False to avoid browser validation on inputs hidden from the
        # user.
        self.assertIs(self.widget.use_required_attribute(None), False)
        self.assertIs(self.widget.use_required_attribute(''), False)
        self.assertIs(self.widget.use_required_attribute('foo'), False)
