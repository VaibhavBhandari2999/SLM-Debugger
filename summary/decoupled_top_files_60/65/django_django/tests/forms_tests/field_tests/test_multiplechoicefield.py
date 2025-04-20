from django.core.exceptions import ValidationError
from django.forms import MultipleChoiceField
from django.test import SimpleTestCase


class MultipleChoiceFieldTest(SimpleTestCase):

    def test_multiplechoicefield_1(self):
        """
        Tests for the MultipleChoiceField.
        
        This function tests various scenarios for the MultipleChoiceField, including:
        - Validation of empty and None inputs
        - Correct handling of valid choices
        - Error handling for invalid inputs
        - Validation of choice values
        
        Parameters:
        - f: An instance of MultipleChoiceField with predefined choices.
        
        Returns:
        - None: The function asserts expected outcomes and does not return any value.
        
        Raises:
        - ValidationError: When the input does not meet the expected criteria.
        
        Key Scenarios:
        1
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
        Tests for the MultipleChoiceField.
        
        This function tests the validation and cleaning of a MultipleChoiceField with nested choices. The field is initialized with a set of choices that include nested tuples for 'Numbers' and 'Letters', and a single choice '5'.
        
        Parameters:
        - None (The function uses internal assertions to test the field's behavior)
        
        Returns:
        - None (The function asserts expected outcomes and raises ValidationError for invalid inputs)
        
        Key Points:
        - The field is tested with various valid and invalid inputs.
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
