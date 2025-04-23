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
        Tests the behavior of the render_to_string method with incorrect arguments.
        
        This function tests the render_to_string method of the engine to ensure it fails silently when provided with an incorrect argument. The method should not raise an error and should return the default output.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - template_name (str): The name of the template to render.
        - context (dict): The context data to pass to the template.
        
        Input:
        - template_name:
        """

        output = self.engine.render_to_string(
            "truncatechars03", {"a": "Testing, testing"}
        )
        self.assertEqual(output, "Testing, testing")
