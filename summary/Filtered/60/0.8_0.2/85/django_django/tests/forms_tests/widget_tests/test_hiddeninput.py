from django.forms import HiddenInput

from .base import WidgetTest


class HiddenInputTest(WidgetTest):
    widget = HiddenInput()

    def test_render(self):
        self.check_html(self.widget, 'email', '', html='<input type="hidden" name="email">')

    def test_use_required_attribute(self):
        """
        Tests the use_required_attribute method of the widget.
        
        This method checks whether the widget uses a required attribute for different input values. The method always returns False, which is used to avoid browser validation on inputs that are hidden from the user.
        
        Parameters:
        value (str, None): The value to check for the required attribute. Possible values are None, '', and any non-empty string.
        
        Returns:
        bool: Always returns False.
        """

        # Always False to avoid browser validation on inputs hidden from the
        # user.
        self.assertIs(self.widget.use_required_attribute(None), False)
        self.assertIs(self.widget.use_required_attribute(''), False)
        self.assertIs(self.widget.use_required_attribute('foo'), False)
