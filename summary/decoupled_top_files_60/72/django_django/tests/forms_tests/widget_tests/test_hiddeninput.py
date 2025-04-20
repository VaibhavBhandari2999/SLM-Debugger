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
        applied to an HTML input element. The method always returns `False` for the
        following cases:
        - When the input value is `None`.
        - When the input value is an empty string.
        
        For any other input value, the method also returns `False`.
        
        Parameters:
        - value (Any): The value of the input element.
        
        Returns:
        - bool: `False`
        """

        # Always False to avoid browser validation on inputs hidden from the
        # user.
        self.assertIs(self.widget.use_required_attribute(None), False)
        self.assertIs(self.widget.use_required_attribute(''), False)
        self.assertIs(self.widget.use_required_attribute('foo'), False)
