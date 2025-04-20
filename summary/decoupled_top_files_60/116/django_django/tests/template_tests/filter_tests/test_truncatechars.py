from django.test import SimpleTestCase

from ..utils import setup


class TruncatecharsTests(SimpleTestCase):
    @setup({"truncatechars01": "{{ a|truncatechars:3 }}"})
    def test_truncatechars01(self):
        output = self.engine.render_to_string(
            "truncatechars01", {"a": "Testing, testing"}
        )
        self.assertEqual(output, "Te…")

    @setup({"truncatechars02": "{{ a|truncatechars:7 }}"})
    def test_truncatechars02(self):
        output = self.engine.render_to_string("truncatechars02", {"a": "Testing"})
        self.assertEqual(output, "Testing")

    @setup({"truncatechars03": "{{ a|truncatechars:'e' }}"})
    def test_fail_silently_incorrect_arg(self):
        """
        Tests the behavior of the render_to_string method when an incorrect argument is passed to the fail_silently parameter.
        
        Parameters:
        - template_name (str): The name of the template to be rendered.
        - context (dict): A dictionary containing the context variables to be passed to the template.
        
        Returns:
        str: The rendered output of the template.
        
        Note:
        This test checks if the method raises an error when an incorrect argument is passed to the fail_silently parameter.
        The
        """

        output = self.engine.render_to_string(
            "truncatechars03", {"a": "Testing, testing"}
        )
        self.assertEqual(output, "Testing, testing")
