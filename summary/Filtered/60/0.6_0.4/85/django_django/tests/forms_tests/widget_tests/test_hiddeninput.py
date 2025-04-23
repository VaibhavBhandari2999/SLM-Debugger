from django.forms import HiddenInput

from .base import WidgetTest


class HiddenInputTest(WidgetTest):
    widget = HiddenInput()

    def test_render(self):
        self.check_html(self.widget, 'email', '', html='<input type="hidden" name="email">')

    def test_use_required_attribute(self):
        """
        Tests the use_required_attribute method of the widget.
        
        This method checks whether the widget requires an attribute to be used based on the input value. The method always returns False to bypass browser validation for inputs that are hidden from the user.
        
        Parameters:
        value (str, None): The value of the input field to check.
        
        Returns:
        bool: Always returns False.
        """

        # Always False to avoid browser validation on inputs hidden from the
        # user.
        self.assertIs(self.widget.use_required_attribute(None), False)
        self.assertIs(self.widget.use_required_attribute(''), False)
        self.assertIs(self.widget.use_required_attribute('foo'), False)
