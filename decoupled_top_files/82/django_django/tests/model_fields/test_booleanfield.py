"""
This Python file contains unit tests for Django's `BooleanField` and `NullBooleanField`. It includes tests for various methods such as `get_prep_value`, `to_python`, and formfield generation. The tests cover scenarios like handling different input types, ensuring correct boolean conversions, and validating field behavior under different conditions. Additionally, it includes tests for selecting related objects and handling default values. The file uses Django's testing framework to validate the expected behavior of these fields. ```python
"""
from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.test import SimpleTestCase, TestCase

from .models import BooleanModel, FksToBooleans, NullBooleanModel


class BooleanFieldTests(TestCase):
    def _test_get_prep_value(self, f):
        """
        Tests the get_prep_value method of a field object (f). Verifies that the method correctly prepares boolean values and None for database storage by returning True for '1', 1, and True; False for '0', 0, and False; and None for None. The method is expected to handle different types of inputs and return appropriate boolean or null values.
        """

        self.assertIs(f.get_prep_value(True), True)
        self.assertIs(f.get_prep_value('1'), True)
        self.assertIs(f.get_prep_value(1), True)
        self.assertIs(f.get_prep_value(False), False)
        self.assertIs(f.get_prep_value('0'), False)
        self.assertIs(f.get_prep_value(0), False)
        self.assertIsNone(f.get_prep_value(None))

    def _test_to_python(self, f):
        self.assertIs(f.to_python(1), True)
        self.assertIs(f.to_python(0), False)

    def test_booleanfield_get_prep_value(self):
        self._test_get_prep_value(models.BooleanField())

    def test_nullbooleanfield_get_prep_value(self):
        self._test_get_prep_value(models.BooleanField(null=True))

    def test_booleanfield_to_python(self):
        self._test_to_python(models.BooleanField())

    def test_nullbooleanfield_to_python(self):
        self._test_to_python(models.BooleanField(null=True))

    def test_booleanfield_choices_blank(self):
        """
        BooleanField with choices and defaults doesn't generate a formfield
        with the blank option (#9640, #10549).
        """
        choices = [(1, 'Si'), (2, 'No')]
        f = models.BooleanField(choices=choices, default=1, null=False)
        self.assertEqual(f.formfield().choices, choices)

    def test_booleanfield_choices_blank_desired(self):
        """
        BooleanField with choices and no default should generated a formfield
        with the blank option.
        """
        choices = [(1, 'Si'), (2, 'No')]
        f = models.BooleanField(choices=choices)
        self.assertEqual(f.formfield().choices, [('', '---------')] + choices)

    def test_nullbooleanfield_formfield(self):
        f = models.BooleanField(null=True)
        self.assertIsInstance(f.formfield(), forms.NullBooleanField)

    def test_return_type(self):
        """
        Tests the return types of boolean fields and null boolean fields. The function creates instances of BooleanModel and NullBooleanModel, sets their boolean fields, and checks if the values are correctly stored and retrieved. It also verifies that the boolean conversion is applied correctly even when an extra clause is present.
        
        - `BooleanModel`: A model with a boolean field.
        - `NullBooleanModel`: A model with a null boolean field.
        - `bfield`: A boolean field in `BooleanModel`.
        """

        b = BooleanModel.objects.create(bfield=True)
        b.refresh_from_db()
        self.assertIs(b.bfield, True)

        b2 = BooleanModel.objects.create(bfield=False)
        b2.refresh_from_db()
        self.assertIs(b2.bfield, False)

        b3 = NullBooleanModel.objects.create(nbfield=True)
        b3.refresh_from_db()
        self.assertIs(b3.nbfield, True)

        b4 = NullBooleanModel.objects.create(nbfield=False)
        b4.refresh_from_db()
        self.assertIs(b4.nbfield, False)

        # When an extra clause exists, the boolean conversions are applied with
        # an offset (#13293).
        b5 = BooleanModel.objects.all().extra(select={'string_col': 'string'})[0]
        self.assertNotIsInstance(b5.pk, bool)

    def test_select_related(self):
        """
        Boolean fields retrieved via select_related() should return booleans.
        """
        bmt = BooleanModel.objects.create(bfield=True)
        bmf = BooleanModel.objects.create(bfield=False)
        nbmt = NullBooleanModel.objects.create(nbfield=True)
        nbmf = NullBooleanModel.objects.create(nbfield=False)
        m1 = FksToBooleans.objects.create(bf=bmt, nbf=nbmt)
        m2 = FksToBooleans.objects.create(bf=bmf, nbf=nbmf)

        # select_related('fk_field_name')
        ma = FksToBooleans.objects.select_related('bf').get(pk=m1.id)
        self.assertIs(ma.bf.bfield, True)
        self.assertIs(ma.nbf.nbfield, True)

        # select_related()
        mb = FksToBooleans.objects.select_related().get(pk=m1.id)
        mc = FksToBooleans.objects.select_related().get(pk=m2.id)
        self.assertIs(mb.bf.bfield, True)
        self.assertIs(mb.nbf.nbfield, True)
        self.assertIs(mc.bf.bfield, False)
        self.assertIs(mc.nbf.nbfield, False)

    def test_null_default(self):
        """
        A BooleanField defaults to None, which isn't a valid value (#15124).
        """
        boolean_field = BooleanModel._meta.get_field('bfield')
        self.assertFalse(boolean_field.has_default())
        b = BooleanModel()
        self.assertIsNone(b.bfield)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                b.save()

        nb = NullBooleanModel()
        self.assertIsNone(nb.nbfield)
        nb.save()  # no error


class ValidationTest(SimpleTestCase):

    def test_boolean_field_doesnt_accept_empty_input(self):
        """
        Tests that a BooleanField does not accept empty input.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If an empty value is passed to the BooleanField's clean method.
        
        Functions Used:
        - `models.BooleanField()`: Creates a BooleanField instance.
        - `f.clean(None, None)`: Cleans the input value (None in this case) and raises a ValidationError if the input is invalid.
        """

        f = models.BooleanField()
        with self.assertRaises(ValidationError):
            f.clean(None, None)

    def test_nullbooleanfield_blank(self):
        """
        NullBooleanField shouldn't throw a validation error when given a value
        of None.
        """
        nullboolean = NullBooleanModel(nbfield=None)
        nullboolean.full_clean()
