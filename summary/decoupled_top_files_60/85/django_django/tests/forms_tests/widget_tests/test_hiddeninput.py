from django.forms import HiddenInput

from .base import WidgetTest


class HiddenInputTest(WidgetTest):
    widget = HiddenInput()

    def test_render(self):
        self.check_html(self.widget, 'email', '', html='<input type="hidden" name="email">')

    def test_use_required_attribute(self):
        """
        Test the use_required_attribute method of the widget.
        
        This method checks whether the widget requires an attribute to be used
        based on the given value. The method always returns False, as it is
        designed to avoid browser validation on inputs that are hidden from the
        user.
        
        Parameters:
        value (str): The value to check if the widget requires an attribute.
        
        Returns:
        bool: Always returns False.
        """

        # Always False to avoid browser validation on inputs hidden from the
        # user.
        self.assertIs(self.widget.use_required_attribute(None), False)
        self.assertIs(self.widget.use_required_attribute(''), False)
        self.assertIs(self.widget.use_required_attribute('foo'), False)
