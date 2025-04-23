from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction
from django.test import SimpleTestCase, TestCase

from .models import BooleanModel, FksToBooleans, NullBooleanModel


class BooleanFieldTests(TestCase):
    def _test_get_prep_value(self, f):
        """
        Tests the get_prep_value method of a BooleanField.
        
        This method checks the conversion of various input values to their boolean equivalents. The function expects a field object `f` as an argument. It tests the following cases:
        - True is converted to True
        - "1" is converted to True
        - 1 is converted to True
        - False is converted to False
        - "0" is converted to False
        - 0 is converted to False
        - None is converted to None
        
        Parameters
        """

        self.assertIs(f.get_prep_value(True), True)
        self.assertIs(f.get_prep_value("1"), True)
        self.assertIs(f.get_prep_value(1), True)
        self.assertIs(f.get_prep_value(False), False)
        self.assertIs(f.get_prep_value("0"), False)
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
        choices = [(1, "Si"), (2, "No")]
        f = models.BooleanField(choices=choices, default=1, null=False)
        self.assertEqual(f.formfield().choices, choices)

    def test_booleanfield_choices_blank_desired(self):
        """
        BooleanField with choices and no default should generated a formfield
        with the blank option.
        """
        choices = [(1, "Si"), (2, "No")]
        f = models.BooleanField(choices=choices)
        self.assertEqual(f.formfield().choices, [("", "---------")] + choices)

    def test_nullbooleanfield_formfield(self):
        f = models.BooleanField(null=True)
        self.assertIsInstance(f.formfield(), forms.NullBooleanField)

    def test_return_type(self):
        """
        Tests the return type of boolean fields in the database models.
        
        This function tests the behavior of boolean fields in the database models by creating instances of `BooleanModel` and `NullBooleanModel` with different boolean values. It then checks if the values are correctly stored and retrieved from the database.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates and tests `BooleanModel` instances with `bfield` set to `True` and `False`.
        - Creates and tests `Null
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
        ma = FksToBooleans.objects.select_related("bf").get(pk=m1.id)
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
        boolean_field = BooleanModel._meta.get_field("bfield")
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
