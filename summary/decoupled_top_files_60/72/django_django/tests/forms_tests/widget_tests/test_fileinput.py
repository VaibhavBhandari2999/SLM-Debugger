from django.forms import FileInput

from .base import WidgetTest


class FileInputTest(WidgetTest):
    widget = FileInput()

    def test_render(self):
        """
        FileInput widgets never render the value attribute. The old value
        isn't useful if a form is updated or an error occurred.
        """
        self.check_html(self.widget, 'email', 'test@example.com', html='<input type="file" name="email">')
        self.check_html(self.widget, 'email', '', html='<input type="file" name="email">')
        self.check_html(self.widget, 'email', None, html='<input type="file" name="email">')

    def test_value_omitted_from_data(self):
        self.assertIs(self.widget.value_omitted_from_data({}, {}, 'field'), True)
        self.assertIs(self.widget.value_omitted_from_data({}, {'field': 'value'}, 'field'), False)

    def test_use_required_attribute(self):
        """
        Tests the use_required_attribute method of the widget.
        
        This method checks whether a required attribute is used based on the provided value.
        When no value is provided (None), the method returns True, indicating that the required attribute is used.
        When a value is provided (a string representing a file name), the method returns False, indicating that the required attribute is not used.
        
        Parameters:
        value (str or None): The value to check. If None, it means the file input is left blank
        """

        # False when initial data exists. The file input is left blank by the
        # user to keep the existing, initial value.
        self.assertIs(self.widget.use_required_attribute(None), True)
        self.assertIs(self.widget.use_required_attribute('resume.txt'), False)
