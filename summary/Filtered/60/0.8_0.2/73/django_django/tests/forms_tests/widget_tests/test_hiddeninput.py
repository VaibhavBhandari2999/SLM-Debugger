from django.forms import HiddenInput

from .base import WidgetTest


class HiddenInputTest(WidgetTest):
    widget = HiddenInput()

    def test_render(self):
        self.check_html(self.widget, 'email', '', html='<input type="hidden" name="email">')

    def test_use_required_attribute(self):
        """
        Tests the `use_required_attribute` method of the widget.
        
        This method is used to determine if a required attribute should be applied to
        an HTML input element. The method returns `False` for all inputs, including
        those that are `None`, empty strings, or non-empty strings.
        
        Parameters:
        value (str or None): The value of the input element.
        
        Returns:
        bool: Always returns `False`.
        
        Examples:
        >>> widget = YourWidgetClass()
        >>> widget.use_required_attribute
        """

        # Always False to avoid browser validation on inputs hidden from the
        # user.
        self.assertIs(self.widget.use_required_attribute(None), False)
        self.assertIs(self.widget.use_required_attribute(''), False)
        self.assertIs(self.widget.use_required_attribute('foo'), False)
