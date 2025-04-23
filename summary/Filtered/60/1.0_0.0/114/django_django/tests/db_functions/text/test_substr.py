from django.db.models import Value as V
from django.db.models.functions import Lower, StrIndex, Substr, Upper
from django.test import TestCase

from ..models import Author


class SubstrTests(TestCase):
    def test_basic(self):
        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda")
        authors = Author.objects.annotate(name_part=Substr("name", 5, 3))
        self.assertQuerySetEqual(
            authors.order_by("name"), [" Sm", "da"], lambda a: a.name_part
        )
        authors = Author.objects.annotate(name_part=Substr("name", 2))
        self.assertQuerySetEqual(
            authors.order_by("name"), ["ohn Smith", "honda"], lambda a: a.name_part
        )
        # If alias is null, set to first 5 lower characters of the name.
        Author.objects.filter(alias__isnull=True).update(
            alias=Lower(Substr("name", 1, 5)),
        )
        self.assertQuerySetEqual(
            authors.order_by("name"), ["smithj", "rhond"], lambda a: a.alias
        )

    def test_start(self):
        """
        Tests the functionality of the Substr function in the context of an Author model.
        
        This test function creates an Author instance with the name "John Smith" and alias "smithj". It then queries the database to retrieve the author and uses the Substr function to extract the first and second parts of the name. The test asserts that the second part of the name is the same as the first part, excluding the first character.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - AssertionError
        """

        Author.objects.create(name="John Smith", alias="smithj")
        a = Author.objects.annotate(
            name_part_1=Substr("name", 1),
            name_part_2=Substr("name", 2),
        ).get(alias="smithj")

        self.assertEqual(a.name_part_1[1:], a.name_part_2)

    def test_pos_gt_zero(self):
        with self.assertRaisesMessage(ValueError, "'pos' must be greater than 0"):
            Author.objects.annotate(raises=Substr("name", 0))

    def test_expressions(self):
        Author.objects.create(name="John Smith", alias="smithj")
        Author.objects.create(name="Rhonda")
        substr = Substr(Upper("name"), StrIndex("name", V("h")), 5)
        authors = Author.objects.annotate(name_part=substr)
        self.assertQuerySetEqual(
            authors.order_by("name"), ["HN SM", "HONDA"], lambda a: a.name_part
        )
