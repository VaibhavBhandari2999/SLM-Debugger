from django.core.exceptions import FieldError
from django.test import SimpleTestCase, TestCase

from .models import (
    Bookmark,
    Domain,
    Family,
    Genus,
    HybridSpecies,
    Kingdom,
    Klass,
    Order,
    Phylum,
    Pizza,
    Species,
    TaggedItem,
)


class SelectRelatedTests(TestCase):
    @classmethod
    def create_tree(cls, stringtree):
        """
        Helper to create a complete tree.
        """
        names = stringtree.split()
        models = [Domain, Kingdom, Phylum, Klass, Order, Family, Genus, Species]
        assert len(names) == len(models), (names, models)

        parent = None
        for name, model in zip(names, models):
            try:
                obj = model.objects.get(name=name)
            except model.DoesNotExist:
                obj = model(name=name)
            if parent:
                setattr(obj, parent.__class__.__name__.lower(), parent)
            obj.save()
            parent = obj

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data by creating biological trees using the `create_tree` method.
        
        This method initializes test data for biological classification trees, which are created using the `create_tree` method. The trees represent different taxonomic classifications:
        
        - Eukaryota, Animalia, Anthropoda, Insecta, Diptera, Drosophilidae, Drosophila melanogaster
        - Eukaryota, Animalia, Chordata, Mammalia, Prim
        """

        cls.create_tree(
            "Eukaryota Animalia Anthropoda Insecta Diptera Drosophilidae Drosophila "
            "melanogaster"
        )
        cls.create_tree(
            "Eukaryota Animalia Chordata Mammalia Primates Hominidae Homo sapiens"
        )
        cls.create_tree(
            "Eukaryota Plantae Magnoliophyta Magnoliopsida Fabales Fabaceae Pisum "
            "sativum"
        )
        cls.create_tree(
            "Eukaryota Fungi Basidiomycota Homobasidiomycatae Agaricales Amanitacae "
            "Amanita muscaria"
        )

    def test_access_fks_without_select_related(self):
        """
        Normally, accessing FKs doesn't fill in related objects
        """
        with self.assertNumQueries(8):
            fly = Species.objects.get(name="melanogaster")
            domain = fly.genus.family.order.klass.phylum.kingdom.domain
            self.assertEqual(domain.name, "Eukaryota")

    def test_access_fks_with_select_related(self):
        """
        A select_related() call will fill in those related objects without any
        extra queries
        """
        with self.assertNumQueries(1):
            person = Species.objects.select_related(
                "genus__family__order__klass__phylum__kingdom__domain"
            ).get(name="sapiens")
            domain = person.genus.family.order.klass.phylum.kingdom.domain
            self.assertEqual(domain.name, "Eukaryota")

    def test_list_without_select_related(self):
        """
        Tests retrieving a list of species without using select_related.
        
        This function asserts that the number of database queries is 9 when
        retrieving all species and extracting their family names. The input is
        an empty queryset of species, and the output is a list of family names
        sorted alphabetically.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the extracted family names do not match the expected
        list ['Amanitacae',
        """

        with self.assertNumQueries(9):
            world = Species.objects.all()
            families = [o.genus.family.name for o in world]
            self.assertEqual(
                sorted(families),
                [
                    "Amanitacae",
                    "Drosophilidae",
                    "Fabaceae",
                    "Hominidae",
                ],
            )

    def test_list_with_select_related(self):
        """select_related() applies to entire lists, not just items."""
        with self.assertNumQueries(1):
            world = Species.objects.select_related()
            families = [o.genus.family.name for o in world]
            self.assertEqual(
                sorted(families),
                [
                    "Amanitacae",
                    "Drosophilidae",
                    "Fabaceae",
                    "Hominidae",
                ],
            )

    def test_list_with_depth(self):
        """
        Passing a relationship field lookup specifier to select_related() will
        stop the descent at a particular level. This can be used on lists as
        well.
        """
        with self.assertNumQueries(5):
            world = Species.objects.select_related("genus__family")
            orders = [o.genus.family.order.name for o in world]
            self.assertEqual(
                sorted(orders), ["Agaricales", "Diptera", "Fabales", "Primates"]
            )

    def test_select_related_with_extra(self):
        """
        Retrieve all species with select-related fields and an extra SQL select clause. The first species object is returned and its 'id' plus 10 is compared to the 'a' attribute, which is derived from the extra select clause.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `Species.objects.all()`: Retrieves all species objects.
        - `select_related()`: Prefetches related objects using SQL joins to reduce the number of database queries.
        """

        s = (
            Species.objects.all()
            .select_related()
            .extra(select={"a": "select_related_species.id + 10"})[0]
        )
        self.assertEqual(s.id + 10, s.a)

    def test_certain_fields(self):
        """
        The optional fields passed to select_related() control which related
        models we pull in. This allows for smaller queries.

        In this case, we explicitly say to select the 'genus' and
        'genus.family' models, leading to the same number of queries as before.
        """
        with self.assertNumQueries(1):
            world = Species.objects.select_related("genus__family")
            families = [o.genus.family.name for o in world]
            self.assertEqual(
                sorted(families),
                ["Amanitacae", "Drosophilidae", "Fabaceae", "Hominidae"],
            )

    def test_more_certain_fields(self):
        """
        In this case, we explicitly say to select the 'genus' and
        'genus.family' models, leading to the same number of queries as before.
        """
        with self.assertNumQueries(2):
            world = Species.objects.filter(genus__name="Amanita").select_related(
                "genus__family"
            )
            orders = [o.genus.family.order.name for o in world]
            self.assertEqual(orders, ["Agaricales"])

    def test_field_traversal(self):
        """
        Tests field traversal for related models.
        
        This method asserts that a single database query is executed when traversing fields across multiple related models. It retrieves the first species object, selects related genus, family, and order models, and then accesses the name of the order model.
        
        :raises AssertionError: If the number of queries does not match the expected value or if the accessed field value is incorrect.
        """

        with self.assertNumQueries(1):
            s = (
                Species.objects.all()
                .select_related("genus__family__order")
                .order_by("id")[0:1]
                .get()
                .genus.family.order.name
            )
            self.assertEqual(s, "Diptera")

    def test_none_clears_list(self):
        queryset = Species.objects.select_related("genus").select_related(None)
        self.assertIs(queryset.query.select_related, False)

    def test_chaining(self):
        """
        Tests the chaining of select_related queries on HybridSpecies objects.
        
        This function creates a hybrid species object and then queries it using
        select_related to fetch related parent species. It ensures that only one
        database query is executed by using assertNumQueries.
        
        :param parent_1: The first parent species object.
        :param parent_2: The second parent species object.
        """

        parent_1, parent_2 = Species.objects.all()[:2]
        HybridSpecies.objects.create(
            name="hybrid", parent_1=parent_1, parent_2=parent_2
        )
        queryset = HybridSpecies.objects.select_related("parent_1").select_related(
            "parent_2"
        )
        with self.assertNumQueries(1):
            obj = queryset[0]
            self.assertEqual(obj.parent_1, parent_1)
            self.assertEqual(obj.parent_2, parent_2)

    def test_reverse_relation_caching(self):
        """
        Tests the caching behavior of reverse relations in Django ORM.
        
        This function verifies that the `genus` field of a `Species` object is properly
        cached when accessed using `select_related`, and that accessing the `species_set`
        reverse relation does not reuse this cache.
        
        - `Species.objects.select_related("genus")`: Selects related `genus` objects
        for `Species` instances.
        - `species.genus.name`: Accesses the name of the related
        """

        species = (
            Species.objects.select_related("genus").filter(name="melanogaster").first()
        )
        with self.assertNumQueries(0):
            self.assertEqual(species.genus.name, "Drosophila")
        # The species_set reverse relation isn't cached.
        self.assertEqual(species.genus._state.fields_cache, {})
        with self.assertNumQueries(1):
            self.assertEqual(species.genus.species_set.first().name, "melanogaster")

    def test_select_related_after_values(self):
        """
        Running select_related() after calling values() raises a TypeError
        """
        message = "Cannot call select_related() after .values() or .values_list()"
        with self.assertRaisesMessage(TypeError, message):
            list(Species.objects.values("name").select_related("genus"))

    def test_select_related_after_values_list(self):
        """
        Running select_related() after calling values_list() raises a TypeError
        """
        message = "Cannot call select_related() after .values() or .values_list()"
        with self.assertRaisesMessage(TypeError, message):
            list(Species.objects.values_list("name").select_related("genus"))


class SelectRelatedValidationTests(SimpleTestCase):
    """
    select_related() should thrown an error on fields that do not exist and
    non-relational fields.
    """

    non_relational_error = (
        "Non-relational field given in select_related: '%s'. Choices are: %s"
    )
    invalid_error = (
        "Invalid field name(s) given in select_related: '%s'. Choices are: %s"
    )

    def test_non_relational_field(self):
        """
        Tests various scenarios involving `select_related` with non-relational fields.
        
        This function checks that using `select_related` on non-relational fields
        raises appropriate `FieldError` exceptions. It tests three different cases:
        
        1. Attempting to use `select_related` on a non-relational field of a related model.
        2. Attempting to use `select_related` on a non-relational field without specifying a related field.
        3. Attempting to use
        """

        with self.assertRaisesMessage(
            FieldError, self.non_relational_error % ("name", "genus")
        ):
            list(Species.objects.select_related("name__some_field"))

        with self.assertRaisesMessage(
            FieldError, self.non_relational_error % ("name", "genus")
        ):
            list(Species.objects.select_related("name"))

        with self.assertRaisesMessage(
            FieldError, self.non_relational_error % ("name", "(none)")
        ):
            list(Domain.objects.select_related("name"))

    def test_non_relational_field_nested(self):
        """
        Tests that non-relational fields cannot be accessed in nested queries.
        
        This function attempts to select related objects using `select_related` on
        nested fields ('genus__name') and expects a `FieldError` to be raised due
        to the non-relational nature of the field access.
        
        Args:
        None
        
        Raises:
        FieldError: If the non-relational field is incorrectly accessed in the
        nested query.
        
        Returns:
        None
        """

        with self.assertRaisesMessage(
            FieldError, self.non_relational_error % ("name", "family")
        ):
            list(Species.objects.select_related("genus__name"))

    def test_many_to_many_field(self):
        """
        Tests the behavior of a many-to-many field in a Pizza model.
        
        This function attempts to select related toppings for a list of pizzas
        using `select_related`. It raises a `FieldError` if no toppings are selected,
        indicating that the many-to-many relationship is not being handled correctly.
        
        Args:
        None
        
        Raises:
        FieldError: If no toppings are selected for any pizza.
        
        Returns:
        None
        """

        with self.assertRaisesMessage(
            FieldError, self.invalid_error % ("toppings", "(none)")
        ):
            list(Pizza.objects.select_related("toppings"))

    def test_reverse_relational_field(self):
        """
        Tests the behavior of reverse relational fields when using `select_related`.
        
        This function attempts to retrieve a list of `Species` objects with their related `child_1` objects selected. It expects to raise a `FieldError` due to an invalid reverse relational field query.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        FieldError: If the query does not raise the expected error message.
        
        Important Functions:
        - `select_related`: Used to optimize the retrieval
        """

        with self.assertRaisesMessage(
            FieldError, self.invalid_error % ("child_1", "genus")
        ):
            list(Species.objects.select_related("child_1"))

    def test_invalid_field(self):
        """
        Tests invalid field usage in select_related.
        
        This function checks for FieldError exceptions when attempting to use
        non-existent fields in select_related queries. It tests three scenarios:
        1. Using an invalid field directly in select_related.
        2. Using an invalid related field in a nested select_related.
        3. Using an invalid field on a different model in select_related.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        FieldError: When an
        """

        with self.assertRaisesMessage(
            FieldError, self.invalid_error % ("invalid_field", "genus")
        ):
            list(Species.objects.select_related("invalid_field"))

        with self.assertRaisesMessage(
            FieldError, self.invalid_error % ("related_invalid_field", "family")
        ):
            list(Species.objects.select_related("genus__related_invalid_field"))

        with self.assertRaisesMessage(
            FieldError, self.invalid_error % ("invalid_field", "(none)")
        ):
            list(Domain.objects.select_related("invalid_field"))

    def test_generic_relations(self):
        """
        Tests generic relations by asserting that specific field errors are raised when attempting to select related fields using `select_related`.
        
        - `tags`: The first test checks for a `FieldError` when trying to select related fields on the `tags` attribute of `Bookmark` objects.
        - `content_object` and `content_type`: The second test checks for a `FieldError` when trying to select related fields on the `content_object` attribute of `TaggedItem` objects, specifically when both
        """

        with self.assertRaisesMessage(FieldError, self.invalid_error % ("tags", "")):
            list(Bookmark.objects.select_related("tags"))

        with self.assertRaisesMessage(
            FieldError, self.invalid_error % ("content_object", "content_type")
        ):
            list(TaggedItem.objects.select_related("content_object"))
