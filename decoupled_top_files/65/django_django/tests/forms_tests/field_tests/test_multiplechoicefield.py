"""
The provided Python file contains unit tests for the `MultipleChoiceField` class from Django's forms module. The tests cover various scenarios such as required fields, input validation, handling of different data types, and the behavior of the `has_changed` method. Each test method focuses on specific aspects of the `MultipleChoiceField` and ensures that it behaves correctly under different conditions.

- **Classes and Functions Defined:**
  - `MultipleChoiceFieldTest`: A test case class that inherits from `SimpleTestCase`.
  - Test methods (`test_multiplechoicefield_1`, `test_multiplechoicefield_2`, `test_multiplechoicefield_3`, `test_multiplechoicefield_changed`, `test_disabled_has_changed`): These methods test the `Multiple
"""
from django.core.exceptions import ValidationError
from django.forms import MultipleChoiceField
from django.test import SimpleTestCase


class MultipleChoiceFieldTest(SimpleTestCase):

    def test_multiplechoicefield_1(self):
        """
        Tests the behavior of the MultipleChoiceField with various inputs and edge cases.
        
        This function tests the `MultipleChoiceField` by validating different types of input values and ensuring that the field behaves as expected. It checks for required fields, correct value cleaning, invalid inputs, and validation errors.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions and Keywords:
        - `MultipleChoiceField`: The field being tested.
        - `clean`: Method used to clean and validate input
        """

        f = MultipleChoiceField(choices=[('1', 'One'), ('2', 'Two')])
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        self.assertEqual(['1'], f.clean([1]))
        self.assertEqual(['1'], f.clean(['1']))
        self.assertEqual(['1', '2'], f.clean(['1', '2']))
        self.assertEqual(['1', '2'], f.clean([1, '2']))
        self.assertEqual(['1', '2'], f.clean((1, '2')))
        with self.assertRaisesMessage(ValidationError, "'Enter a list of values.'"):
            f.clean('hello')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean([])
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(())
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['3'])

    def test_multiplechoicefield_2(self):
        """
        Tests the behavior of the MultipleChoiceField when cleaning various inputs. The function verifies that the field correctly handles empty strings, None values, lists, tuples, and invalid inputs, raising appropriate validation errors where necessary.
        
        Args:
        None (The function is a test method and does not take any arguments)
        
        Returns:
        None (The function performs assertions and does not return any value)
        
        Important Functions:
        - `clean`: Cleans and validates the input data according to the defined choices.
        """

        f = MultipleChoiceField(choices=[('1', 'One'), ('2', 'Two')], required=False)
        self.assertEqual([], f.clean(''))
        self.assertEqual([], f.clean(None))
        self.assertEqual(['1'], f.clean([1]))
        self.assertEqual(['1'], f.clean(['1']))
        self.assertEqual(['1', '2'], f.clean(['1', '2']))
        self.assertEqual(['1', '2'], f.clean([1, '2']))
        self.assertEqual(['1', '2'], f.clean((1, '2')))
        with self.assertRaisesMessage(ValidationError, "'Enter a list of values.'"):
            f.clean('hello')
        self.assertEqual([], f.clean([]))
        self.assertEqual([], f.clean(()))
        msg = "'Select a valid choice. 3 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['3'])

    def test_multiplechoicefield_3(self):
        """
        Tests the behavior of the MultipleChoiceField with various inputs and edge cases.
        
        This function tests the `MultipleChoiceField` by validating its response to different inputs, including lists of integers and strings, and ensuring that invalid choices raise a `ValidationError`.
        
        Args:
        None (This is a test method, no arguments are expected).
        
        Returns:
        None (This method does not return any value, it only performs assertions).
        
        Important Functions:
        - `MultipleChoiceField`: The field being
        """

        f = MultipleChoiceField(
            choices=[('Numbers', (('1', 'One'), ('2', 'Two'))), ('Letters', (('3', 'A'), ('4', 'B'))), ('5', 'Other')]
        )
        self.assertEqual(['1'], f.clean([1]))
        self.assertEqual(['1'], f.clean(['1']))
        self.assertEqual(['1', '5'], f.clean([1, 5]))
        self.assertEqual(['1', '5'], f.clean([1, '5']))
        self.assertEqual(['1', '5'], f.clean(['1', 5]))
        self.assertEqual(['1', '5'], f.clean(['1', '5']))
        msg = "'Select a valid choice. 6 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['6'])
        msg = "'Select a valid choice. 6 is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(['1', '6'])

    def test_multiplechoicefield_changed(self):
        """
        Tests the behavior of the `has_changed` method for a MultipleChoiceField.
        
        This method checks how the `has_changed` method behaves with different inputs,
        including `None`, empty lists, and lists with specific choices. It uses the
        `MultipleChoiceField` class and its `choices` attribute to define the available
        options.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Used:
        - has_changed: Determines if the field's value has changed
        """

        f = MultipleChoiceField(choices=[('1', 'One'), ('2', 'Two'), ('3', 'Three')])
        self.assertFalse(f.has_changed(None, None))
        self.assertFalse(f.has_changed([], None))
        self.assertTrue(f.has_changed(None, ['1']))
        self.assertFalse(f.has_changed([1, 2], ['1', '2']))
        self.assertFalse(f.has_changed([2, 1], ['1', '2']))
        self.assertTrue(f.has_changed([1, 2], ['1']))
        self.assertTrue(f.has_changed([1, 2], ['1', '3']))

    def test_disabled_has_changed(self):
        f = MultipleChoiceField(choices=[('1', 'One'), ('2', 'Two')], disabled=True)
        self.assertIs(f.has_changed('x', 'y'), False)
