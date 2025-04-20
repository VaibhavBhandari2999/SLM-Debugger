from operator import attrgetter
from unittest import skipUnless

from django.core.exceptions import FieldError, ValidationError
from django.db import connection, models
from django.test import SimpleTestCase, TestCase
from django.test.utils import CaptureQueriesContext, isolate_apps
from django.utils.version import PY37

from .models import (
    Base, Chef, CommonInfo, GrandChild, GrandParent, ItalianRestaurant,
    MixinModel, Parent, ParkingLot, Place, Post, Restaurant, Student, SubBase,
    Supplier, Title, Worker,
)


class ModelInheritanceTests(TestCase):
    def test_abstract(self):
        """
        This function tests the behavior of abstract models in Django.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - The function performs several assertions to check the behavior of abstract models and their children. It creates instances of `Worker` and `Student` models, checks the string representation of these instances, and verifies the ordering and Meta class behavior.
        
        Expected Behavior:
        - The function asserts that the string representation of `Worker` and `Student` instances is correct.
        """

        # The Student and Worker models both have 'name' and 'age' fields on
        # them and inherit the __str__() method, just as with normal Python
        # subclassing. This is useful if you want to factor out common
        # information for programming purposes, but still completely
        # independent separate models at the database level.
        w1 = Worker.objects.create(name="Fred", age=35, job="Quarry worker")
        Worker.objects.create(name="Barney", age=34, job="Quarry worker")

        s = Student.objects.create(name="Pebbles", age=5, school_class="1B")

        self.assertEqual(str(w1), "Worker Fred")
        self.assertEqual(str(s), "Student Pebbles")

        # The children inherit the Meta class of their parents (if they don't
        # specify their own).
        self.assertSequenceEqual(
            Worker.objects.values("name"), [
                {"name": "Barney"},
                {"name": "Fred"},
            ],
        )

        # Since Student does not subclass CommonInfo's Meta, it has the effect
        # of completely overriding it. So ordering by name doesn't take place
        # for Students.
        self.assertEqual(Student._meta.ordering, [])

        # However, the CommonInfo class cannot be used as a normal model (it
        # doesn't exist as a model).
        with self.assertRaisesMessage(AttributeError, "'CommonInfo' has no attribute 'objects'"):
            CommonInfo.objects.all()

    def test_reverse_relation_for_different_hierarchy_tree(self):
        # Even though p.supplier for a Place 'p' (a parent of a Supplier), a
        # Restaurant object cannot access that reverse relation, since it's not
        # part of the Place-Supplier Hierarchy.
        self.assertQuerysetEqual(Place.objects.filter(supplier__name="foo"), [])
        msg = (
            "Cannot resolve keyword 'supplier' into field. Choices are: "
            "address, chef, chef_id, id, italianrestaurant, lot, name, "
            "place_ptr, place_ptr_id, provider, rating, serves_hot_dogs, serves_pizza"
        )
        with self.assertRaisesMessage(FieldError, msg):
            Restaurant.objects.filter(supplier__name="foo")

    def test_model_with_distinct_accessors(self):
        """
        Tests the behavior of distinct accessors in a Django model.
        
        This function creates a Post object and attaches a Comment and a Link to it using distinct accessors. It then attempts to access an attribute that does not exist, expecting an AttributeError to be raised.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Inputs:
        - None
        
        Outputs:
        - The function asserts that an AttributeError is raised when attempting to access a non-existent attribute.
        
        Raises:
        - AttributeError: If the attribute 'attached_%(class
        """

        # The Post model has distinct accessors for the Comment and Link models.
        post = Post.objects.create(title="Lorem Ipsum")
        post.attached_comment_set.create(content="Save $ on V1agr@", is_spam=True)
        post.attached_link_set.create(
            content="The Web framework for perfections with deadlines.",
            url="http://www.djangoproject.com/"
        )

        # The Post model doesn't have an attribute called
        # 'attached_%(class)s_set'.
        msg = "'Post' object has no attribute 'attached_%(class)s_set'"
        with self.assertRaisesMessage(AttributeError, msg):
            getattr(post, "attached_%(class)s_set")

    def test_model_with_distinct_related_query_name(self):
        self.assertQuerysetEqual(Post.objects.filter(attached_model_inheritance_comments__is_spam=True), [])

        # The Post model doesn't have a related query accessor based on
        # related_name (attached_comment_set).
        msg = "Cannot resolve keyword 'attached_comment_set' into field."
        with self.assertRaisesMessage(FieldError, msg):
            Post.objects.filter(attached_comment_set__is_spam=True)

    def test_meta_fields_and_ordering(self):
        # Make sure Restaurant and ItalianRestaurant have the right fields in
        # the right order.
        self.assertEqual(
            [f.name for f in Restaurant._meta.fields],
            ["id", "name", "address", "place_ptr", "rating", "serves_hot_dogs",
             "serves_pizza", "chef"]
        )
        self.assertEqual(
            [f.name for f in ItalianRestaurant._meta.fields],
            ["id", "name", "address", "place_ptr", "rating", "serves_hot_dogs",
             "serves_pizza", "chef", "restaurant_ptr", "serves_gnocchi"],
        )
        self.assertEqual(Restaurant._meta.ordering, ["-rating"])

    def test_custompk_m2m(self):
        b = Base.objects.create()
        b.titles.add(Title.objects.create(title="foof"))
        s = SubBase.objects.create(sub_id=b.id)
        b = Base.objects.get(pk=s.id)
        self.assertNotEqual(b.pk, s.pk)
        # Low-level test for related_val
        self.assertEqual(s.titles.related_val, (s.id,))
        # Higher level test for correct query values (title foof not
        # accidentally found).
        self.assertQuerysetEqual(s.titles.all(), [])

    def test_update_parent_filtering(self):
        """
        Updating a field of a model subclass doesn't issue an UPDATE
        query constrained by an inner query (#10399).
        """
        supplier = Supplier.objects.create(
            name='Central market',
            address='610 some street',
        )
        # Capture the expected query in a database agnostic way
        with CaptureQueriesContext(connection) as captured_queries:
            Place.objects.filter(pk=supplier.pk).update(name=supplier.name)
        expected_sql = captured_queries[0]['sql']
        # Capture the queries executed when a subclassed model instance is saved.
        with CaptureQueriesContext(connection) as captured_queries:
            supplier.save(update_fields=('name',))
        for query in captured_queries:
            sql = query['sql']
            if 'UPDATE' in sql:
                self.assertEqual(expected_sql, sql)

    def test_create_child_no_update(self):
        """Creating a child with non-abstract parents only issues INSERTs."""
        def a():
            """
            Creates a new GrandChild object in the database.
            
            This function creates a new instance of the GrandChild model and saves it to the database.
            
            Parameters:
            None
            
            Returns:
            None
            
            Example:
            >>> a()
            # A new GrandChild object is created with the email 'grand_parent@example.com', first name 'grand', and last name 'parent'.
            """

            GrandChild.objects.create(
                email='grand_parent@example.com',
                first_name='grand',
                last_name='parent',
            )

        def b():
            GrandChild().save()
        for i, test in enumerate([a, b]):
            with self.subTest(i=i), self.assertNumQueries(4), CaptureQueriesContext(connection) as queries:
                test()
                for query in queries:
                    sql = query['sql']
                    self.assertIn('INSERT INTO', sql, sql)

    def test_eq(self):
        # Equality doesn't transfer in multitable inheritance.
        self.assertNotEqual(Place(id=1), Restaurant(id=1))
        self.assertNotEqual(Restaurant(id=1), Place(id=1))

    def test_mixin_init(self):
        m = MixinModel()
        self.assertEqual(m.other_attr, 1)

    @isolate_apps('model_inheritance')
    def test_abstract_parent_link(self):
        """
        Tests the functionality of the parent_link attribute in a OneToOneField for an abstract model.
        
        This function creates a hierarchy of abstract models to test the parent_link attribute in Django's OneToOneField. The key steps are:
        1. Define a base abstract model 'A' with no fields.
        2. Define an abstract model 'B' that inherits from 'A' and includes a OneToOneField to 'A' with parent_link=True.
        3. Define a concrete model 'C' that inherits from
        """

        class A(models.Model):
            pass

        class B(A):
            a = models.OneToOneField('A', parent_link=True, on_delete=models.CASCADE)

            class Meta:
                abstract = True

        class C(B):
            pass

        self.assertIs(C._meta.parents[A], C._meta.get_field('a'))

    @isolate_apps('model_inheritance')
    def test_init_subclass(self):
        saved_kwargs = {}

        class A(models.Model):
            def __init_subclass__(cls, **kwargs):
                super().__init_subclass__()
                saved_kwargs.update(kwargs)

        kwargs = {'x': 1, 'y': 2, 'z': 3}

        class B(A, **kwargs):
            pass

        self.assertEqual(saved_kwargs, kwargs)

    @isolate_apps('model_inheritance')
    def test_set_name(self):
        class ClassAttr:
            called = None

            def __set_name__(self_, owner, name):
                self.assertIsNone(self_.called)
                self_.called = (owner, name)

        class A(models.Model):
            attr = ClassAttr()

        self.assertEqual(A.attr.called, (A, 'attr'))

    def test_inherited_ordering_pk_desc(self):
        """
        Tests the ordering of a queryset based on a parent model's primary key in descending order.
        
        This function creates two instances of the Parent model with different first names and emails. It then queries the database to retrieve all Parent objects in descending order based on the grandparent's primary key. The expected SQL query is checked to ensure it includes the correct ORDER BY clause.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The returned queryset should contain the Parent instances in the order [p2,
        """

        p1 = Parent.objects.create(first_name='Joe', email='joe@email.com')
        p2 = Parent.objects.create(first_name='Jon', email='jon@email.com')
        expected_order_by_sql = 'ORDER BY %s.%s DESC' % (
            connection.ops.quote_name(Parent._meta.db_table),
            connection.ops.quote_name(
                Parent._meta.get_field('grandparent_ptr').column
            ),
        )
        qs = Parent.objects.all()
        self.assertSequenceEqual(qs, [p2, p1])
        self.assertIn(expected_order_by_sql, str(qs.query))

    @skipUnless(PY37, '__class_getitem__() was added in Python 3.7')
    def test_queryset_class_getitem(self):
        self.assertIs(models.QuerySet[Post], models.QuerySet)
        self.assertIs(models.QuerySet[Post, Post], models.QuerySet)
        self.assertIs(models.QuerySet[Post, int, str], models.QuerySet)


class ModelInheritanceDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls):
        A class method that sets up test data for the class. It creates a Restaurant object and an ItalianRestaurant object for testing purposes.
        
        Parameters:
        cls: The class object that this method is bound to. This is used to create class-level test data.
        
        Returns:
        None: This method does not return anything. It sets up class-level test data for use in tests.
        
        Key Parameters:
        - restaurant: A Restaurant object with the following attributes:
        - name:
        """

        cls.restaurant = Restaurant.objects.create(
            name="Demon Dogs",
            address="944 W. Fullerton",
            serves_hot_dogs=True,
            serves_pizza=False,
            rating=2,
        )

        chef = Chef.objects.create(name="Albert")
        cls.italian_restaurant = ItalianRestaurant.objects.create(
            name="Ristorante Miron",
            address="1234 W. Ash",
            serves_hot_dogs=False,
            serves_pizza=False,
            serves_gnocchi=True,
            rating=4,
            chef=chef,
        )

    def test_filter_inherited_model(self):
        self.assertQuerysetEqual(
            ItalianRestaurant.objects.filter(address="1234 W. Ash"), [
                "Ristorante Miron",
            ],
            attrgetter("name")
        )

    def test_update_inherited_model(self):
        self.italian_restaurant.address = "1234 W. Elm"
        self.italian_restaurant.save()
        self.assertQuerysetEqual(
            ItalianRestaurant.objects.filter(address="1234 W. Elm"), [
                "Ristorante Miron",
            ],
            attrgetter("name")
        )

    def test_parent_fields_available_for_filtering_in_child_model(self):
        # Parent fields can be used directly in filters on the child model.
        self.assertQuerysetEqual(
            Restaurant.objects.filter(name="Demon Dogs"), [
                "Demon Dogs",
            ],
            attrgetter("name")
        )
        self.assertQuerysetEqual(
            ItalianRestaurant.objects.filter(address="1234 W. Ash"), [
                "Ristorante Miron",
            ],
            attrgetter("name")
        )

    def test_filter_on_parent_returns_object_of_parent_type(self):
        """
        Test that filtering on a parent model returns objects of the parent type.
        
        Parameters:
        p (Place): A Place object retrieved from the database.
        
        Returns:
        None: This function asserts the type of the object returned by the filter, but does not return any value.
        
        Key Points:
        - The function checks if the type of the filtered object is of the same type as the parent model (Place).
        - The Place object is retrieved using the primary key and name "Demon Dogs".
        - The assertion
        """

        # Filters against the parent model return objects of the parent's type.
        p = Place.objects.get(name="Demon Dogs")
        self.assertIs(type(p), Place)

    def test_parent_child_one_to_one_link(self):
        """
        Tests the functionality of a one-to-one link between a parent and child model.
        
        This function verifies that a parent model can access its child model through a OneToOneField. It checks three scenarios:
        1. A parent model (Place) with a OneToOneField to a child model (Restaurant).
        2. A parent model (Restaurant) with a OneToOneField to a child model (ItalianRestaurant).
        3. A parent model (Restaurant) with a OneToOneField to a child model (ItalianRestaurant
        """

        # Since the parent and child are linked by an automatically created
        # OneToOneField, you can get from the parent to the child by using the
        # child's name.
        self.assertEqual(
            Place.objects.get(name="Demon Dogs").restaurant,
            Restaurant.objects.get(name="Demon Dogs")
        )
        self.assertEqual(
            Place.objects.get(name="Ristorante Miron").restaurant.italianrestaurant,
            ItalianRestaurant.objects.get(name="Ristorante Miron")
        )
        self.assertEqual(
            Restaurant.objects.get(name="Ristorante Miron").italianrestaurant,
            ItalianRestaurant.objects.get(name="Ristorante Miron")
        )

    def test_parent_child_one_to_one_link_on_nonrelated_objects(self):
        # This won't work because the Demon Dogs restaurant is not an Italian
        # restaurant.
        with self.assertRaises(ItalianRestaurant.DoesNotExist):
            Place.objects.get(name="Demon Dogs").restaurant.italianrestaurant

    def test_inherited_does_not_exist_exception(self):
        # An ItalianRestaurant which does not exist is also a Place which does
        # not exist.
        with self.assertRaises(Place.DoesNotExist):
            ItalianRestaurant.objects.get(name="The Noodle Void")

    def test_inherited_multiple_objects_returned_exception(self):
        # MultipleObjectsReturned is also inherited.
        with self.assertRaises(Place.MultipleObjectsReturned):
            Restaurant.objects.get()

    def test_related_objects_for_inherited_models(self):
        # Related objects work just as they normally do.
        s1 = Supplier.objects.create(name="Joe's Chickens", address="123 Sesame St")
        s1.customers.set([self.restaurant, self.italian_restaurant])
        s2 = Supplier.objects.create(name="Luigi's Pasta", address="456 Sesame St")
        s2.customers.set([self.italian_restaurant])

        # This won't work because the Place we select is not a Restaurant (it's
        # a Supplier).
        p = Place.objects.get(name="Joe's Chickens")
        with self.assertRaises(Restaurant.DoesNotExist):
            p.restaurant

        self.assertEqual(p.supplier, s1)
        self.assertQuerysetEqual(
            self.italian_restaurant.provider.order_by("-name"), [
                "Luigi's Pasta",
                "Joe's Chickens"
            ],
            attrgetter("name")
        )
        self.assertQuerysetEqual(
            Restaurant.objects.filter(provider__name__contains="Chickens"), [
                "Ristorante Miron",
                "Demon Dogs",
            ],
            attrgetter("name")
        )
        self.assertQuerysetEqual(
            ItalianRestaurant.objects.filter(provider__name__contains="Chickens"), [
                "Ristorante Miron",
            ],
            attrgetter("name"),
        )

        ParkingLot.objects.create(
            name="Main St", address="111 Main St", main_site=s1
        )
        ParkingLot.objects.create(
            name="Well Lit", address="124 Sesame St", main_site=self.italian_restaurant
        )

        self.assertEqual(
            Restaurant.objects.get(lot__name="Well Lit").name,
            "Ristorante Miron"
        )

    def test_update_works_on_parent_and_child_models_at_once(self):
        """
        Test the update() method to verify that it can update fields in both parent and child models simultaneously.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The update() method is used to modify fields in related models (parent and child) in a single operation.
        - The method executes multiple SQL queries to update the fields.
        - The filter() method is used to specify the conditions for the rows to be updated.
        - The update() method takes a dictionary of field-value pairs to
        """

        # The update() command can update fields in parent and child classes at
        # once (although it executed multiple SQL queries to do so).
        rows = Restaurant.objects.filter(
            serves_hot_dogs=True, name__contains="D"
        ).update(
            name="Demon Puppies", serves_hot_dogs=False
        )
        self.assertEqual(rows, 1)

        r1 = Restaurant.objects.get(pk=self.restaurant.pk)
        self.assertFalse(r1.serves_hot_dogs)
        self.assertEqual(r1.name, "Demon Puppies")

    def test_values_works_on_parent_model_fields(self):
        # The values() command also works on fields from parent models.
        self.assertSequenceEqual(
            ItalianRestaurant.objects.values("name", "rating"), [
                {"rating": 4, "name": "Ristorante Miron"},
            ],
        )

    def test_select_related_works_on_parent_model_fields(self):
        """
        Tests the functionality of `select_related` on parent model fields.
        
        This function checks if `select_related` works correctly with fields from the parent object, treating them as if they were part of the model. It measures the number of queries executed before and after applying `select_related` to ensure that related objects are fetched in a single query, optimizing performance.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The number of queries executed without `select_related` should be 2.
        -
        """

        # select_related works with fields from the parent object as if they
        # were a normal part of the model.
        self.assertNumQueries(
            2, lambda: ItalianRestaurant.objects.all()[0].chef
        )
        self.assertNumQueries(
            1, lambda: ItalianRestaurant.objects.select_related("chef")[0].chef
        )

    def test_select_related_defer(self):
        """
        #23370 - Should be able to defer child fields when using
        select_related() from parent to child.
        """
        qs = (Restaurant.objects.select_related("italianrestaurant")
              .defer("italianrestaurant__serves_gnocchi").order_by("rating"))

        # The field was actually deferred
        with self.assertNumQueries(2):
            objs = list(qs.all())
            self.assertTrue(objs[1].italianrestaurant.serves_gnocchi)

        # Model fields where assigned correct values
        self.assertEqual(qs[0].name, 'Demon Dogs')
        self.assertEqual(qs[0].rating, 2)
        self.assertEqual(qs[1].italianrestaurant.name, 'Ristorante Miron')
        self.assertEqual(qs[1].italianrestaurant.rating, 4)

    def test_parent_cache_reuse(self):
        place = Place.objects.create()
        GrandChild.objects.create(place=place)
        grand_parent = GrandParent.objects.latest('pk')
        with self.assertNumQueries(1):
            self.assertEqual(grand_parent.place, place)
        parent = grand_parent.parent
        with self.assertNumQueries(0):
            self.assertEqual(parent.place, place)
        child = parent.child
        with self.assertNumQueries(0):
            self.assertEqual(child.place, place)
        grandchild = child.grandchild
        with self.assertNumQueries(0):
            self.assertEqual(grandchild.place, place)

    def test_update_query_counts(self):
        """
        Update queries do not generate unnecessary queries (#18304).
        """
        with self.assertNumQueries(3):
            self.italian_restaurant.save()

    def test_filter_inherited_on_null(self):
        """
        Tests filtering on inherited models with null values.
        
        This function tests filtering on inherited models where the related field can be null. It creates a supplier instance and then performs two queries:
        1. Filters places that have a non-null supplier and checks if the name matches "Central market".
        2. Filters places that have a null supplier and orders them by name, expecting to find "Demon Dogs" and "Ristorante Miron".
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - Creates
        """

        # Refs #12567
        Supplier.objects.create(
            name="Central market",
            address="610 some street",
        )
        self.assertQuerysetEqual(
            Place.objects.filter(supplier__isnull=False), [
                "Central market",
            ],
            attrgetter("name")
        )
        self.assertQuerysetEqual(
            Place.objects.filter(supplier__isnull=True).order_by("name"), [
                "Demon Dogs",
                "Ristorante Miron",
            ],
            attrgetter("name")
        )

    def test_exclude_inherited_on_null(self):
        # Refs #12567
        Supplier.objects.create(
            name="Central market",
            address="610 some street",
        )
        self.assertQuerysetEqual(
            Place.objects.exclude(supplier__isnull=False).order_by("name"), [
                "Demon Dogs",
                "Ristorante Miron",
            ],
            attrgetter("name")
        )
        self.assertQuerysetEqual(
            Place.objects.exclude(supplier__isnull=True), [
                "Central market",
            ],
            attrgetter("name")
        )


@isolate_apps('model_inheritance', 'model_inheritance.tests')
class InheritanceSameModelNameTests(SimpleTestCase):
    def test_abstract_fk_related_name(self):
        """
        Tests the behavior of related_name for abstract ForeignKey fields in Django models.
        
        This function checks the related_name attribute for an abstract ForeignKey field in a Django model. It involves creating a Referenced model and an abstract Referent model with a ForeignKey to Referenced. Two separate Referent models are then defined in different apps ('model_inheritance' and 'tests') to test the related_name resolution. The function ensures that the related_name is correctly set for the ForeignKey field in the Referenced model, pointing to
        """

        related_name = '%(app_label)s_%(class)s_references'

        class Referenced(models.Model):
            class Meta:
                app_label = 'model_inheritance'

        class AbstractReferent(models.Model):
            reference = models.ForeignKey(Referenced, models.CASCADE, related_name=related_name)

            class Meta:
                app_label = 'model_inheritance'
                abstract = True

        class Referent(AbstractReferent):
            class Meta:
                app_label = 'model_inheritance'

        LocalReferent = Referent

        class Referent(AbstractReferent):
            class Meta:
                app_label = 'tests'

        ForeignReferent = Referent

        self.assertFalse(hasattr(Referenced, related_name))
        self.assertIs(Referenced.model_inheritance_referent_references.field.model, LocalReferent)
        self.assertIs(Referenced.tests_referent_references.field.model, ForeignReferent)


class InheritanceUniqueTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData(cls)
        This method is a class method used to set up test data for a test class. It is called once before any test method is run.
        
        Parameters:
        cls (cls): The test class itself, used to create and store test data.
        
        Returns:
        None: This method does not return any value. It creates and stores test data as class attributes for use in test methods.
        
        Example Usage:
        class TestGrandParentModel(TestCase):
        @classmethod
        def
        """

        cls.grand_parent = GrandParent.objects.create(
            email='grand_parent@example.com',
            first_name='grand',
            last_name='parent',
        )

    def test_unique(self):
        grand_child = GrandChild(
            email=self.grand_parent.email,
            first_name='grand',
            last_name='child',
        )
        msg = 'Grand parent with this Email already exists.'
        with self.assertRaisesMessage(ValidationError, msg):
            grand_child.validate_unique()

    def test_unique_together(self):
        grand_child = GrandChild(
            email='grand_child@example.com',
            first_name=self.grand_parent.first_name,
            last_name=self.grand_parent.last_name,
        )
        msg = 'Grand parent with this First name and Last name already exists.'
        with self.assertRaisesMessage(ValidationError, msg):
            grand_child.validate_unique()
d.validate_unique()
ge(ValidationError, msg):
            grand_child.validate_unique()
d.validate_unique()
