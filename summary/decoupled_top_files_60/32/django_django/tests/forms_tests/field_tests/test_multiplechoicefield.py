from django.forms import MultipleChoiceField, ValidationError
from django.test import SimpleTestCase


class MultipleChoiceFieldTest(SimpleTestCase):

    def test_multiplechoicefield_1(self):
        """
        Tests the behavior of the MultipleChoiceField in various scenarios.
        
        This function tests the MultipleChoiceField by validating different inputs and checking for expected validation errors. The field is initialized with a list of choices.
        
        Parameters:
        - No external parameters are passed to this function.
        
        Key Behaviors:
        - Validates that empty strings and None values raise a ValidationError with the message "'This field is required.'".
        - Validates that a single valid choice ('1') is correctly cleaned and returned.
        - Validates that multiple valid choices ('
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
        Tests the behavior of the MultipleChoiceField's has_changed method.
        
        This function checks the has_changed method of the MultipleChoiceField class, which is used to determine if the field's value has changed. The method takes two arguments: the initial value and the current value. It returns a boolean indicating whether the field's value has changed.
        
        Parameters:
        - f (MultipleChoiceField): The MultipleChoiceField instance to test.
        
        Returns:
        None: This function does not return any value. It only
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
 'Two')], disabled=True)
        self.assertIs(f.has_changed('x', 'y'), False)
