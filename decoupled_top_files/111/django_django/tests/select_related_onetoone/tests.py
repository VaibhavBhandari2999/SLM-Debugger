from django.core.exceptions import FieldError
from django.db.models import FilteredRelation
from django.test import SimpleTestCase, TestCase

from .models import (
    AdvancedUserStat,
    Child1,
    Child2,
    Child3,
    Child4,
    Image,
    LinkedList,
    Parent1,
    Parent2,
    Product,
    StatDetails,
    User,
    UserProfile,
    UserStat,
    UserStatResult,
)


class ReverseSelectRelatedTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the tests.
        
        This method creates several instances of models including User, UserProfile, UserStatResult, UserStat, StatDetails, AdvancedUserStat, Parent1, and Child1. It also creates an instance of Parent2 and Child2. The important functions used are:
        - `User.objects.create`: Creates a new user with a given username.
        - `UserProfile.objects.create`: Creates a new user profile with specified attributes.
        - `UserStatResult.objects.create
        """

        user = User.objects.create(username="test")
        UserProfile.objects.create(user=user, state="KS", city="Lawrence")
        results = UserStatResult.objects.create(results="first results")
        userstat = UserStat.objects.create(user=user, posts=150, results=results)
        StatDetails.objects.create(base_stats=userstat, comments=259)

        user2 = User.objects.create(username="bob")
        results2 = UserStatResult.objects.create(results="moar results")
        advstat = AdvancedUserStat.objects.create(
            user=user2, posts=200, karma=5, results=results2
        )
        StatDetails.objects.create(base_stats=advstat, comments=250)
        p1 = Parent1(name1="Only Parent1")
        p1.save()
        c1 = Child1(name1="Child1 Parent1", name2="Child1 Parent2", value=1)
        c1.save()
        p2 = Parent2(name2="Child2 Parent2")
        p2.save()
        c2 = Child2(name1="Child2 Parent1", parent2=p2, value=2)
        c2.save()

    def test_basic(self):
        """
        Tests basic functionality of retrieving a user with their associated UserProfile. Uses `assertNumQueries` to ensure only one query is executed. Selects related UserProfile using `select_related`. Verifies that the retrieved user's UserProfile state is 'KS'.
        """

        with self.assertNumQueries(1):
            u = User.objects.select_related("userprofile").get(username="test")
            self.assertEqual(u.userprofile.state, "KS")

    def test_follow_next_level(self):
        """
        Tests the retrieval of a user's details including their userstat and associated results. This method ensures that only one database query is executed by using `select_related` to fetch related objects. The function asserts that the user's userstat contains the correct number of posts (150) and the expected results string ("first results").
        
        :raises AssertionError: If the assertions fail, indicating incorrect data retrieval or mismatched values.
        """

        with self.assertNumQueries(1):
            u = User.objects.select_related("userstat__results").get(username="test")
            self.assertEqual(u.userstat.posts, 150)
            self.assertEqual(u.userstat.results.results, "first results")

    def test_follow_two(self):
        """
        Tests the retrieval of a user with specific related objects using `select_related`. The function asserts that exactly one database query is executed and checks if the user's `userprofile` state is 'KS' and `userstat` posts count is 150.
        
        :param None: No additional parameters are required for this test function.
        :raises AssertionError: If the number of queries does not match the expected value or if the attributes of the user profile or user statistics do not match the expected
        """

        with self.assertNumQueries(1):
            u = User.objects.select_related("userprofile", "userstat").get(
                username="test"
            )
            self.assertEqual(u.userprofile.state, "KS")
            self.assertEqual(u.userstat.posts, 150)

    def test_follow_two_next_level(self):
        """
        Tests following a user and accessing their related statistics and details.
        
        This function asserts that querying a user with the username 'test' using `select_related` to fetch related objects (`userstat__results`, `userstat__statdetails`) in a single database query results in the expected values for `results` and `statdetails.comments`.
        
        :raises AssertionError: If the expected values do not match the actual values fetched from the database.
        """

        with self.assertNumQueries(1):
            u = User.objects.select_related(
                "userstat__results", "userstat__statdetails"
            ).get(username="test")
            self.assertEqual(u.userstat.results.results, "first results")
            self.assertEqual(u.userstat.statdetails.comments, 259)

    def test_forward_and_back(self):
        """
        Tests the forward and backward relationships between UserStat and UserProfile models.
        
        This function asserts that a single database query is made when retrieving a UserStat instance
        related to a specific user. It then checks the state of the associated UserProfile and the number
        of posts in the UserStat.
        
        :raises AssertionError: If the state or number of posts do not match the expected values.
        """

        with self.assertNumQueries(1):
            stat = UserStat.objects.select_related("user__userprofile").get(
                user__username="test"
            )
            self.assertEqual(stat.user.userprofile.state, "KS")
            self.assertEqual(stat.user.userstat.posts, 150)

    def test_back_and_forward(self):
        """
        Tests the back and forth navigation between related objects using `select_related`. Ensures that querying a user with a related user statistic object requires only one database query.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the related user statistic's user does not match the queried user.
        
        Important Functions:
        - `User.objects.select_related("userstat").get(username="test")`: Retrieves a user with the username 'test' and its related user statistic in
        """

        with self.assertNumQueries(1):
            u = User.objects.select_related("userstat").get(username="test")
            self.assertEqual(u.userstat.user.username, "test")

    def test_not_followed_by_default(self):
        """
        Tests if a user is not followed by any default value. Queries the database twice to retrieve the user with the username 'test' using `select_related()` and checks if their associated `userstat` object has `posts` equal to 150.
        """

        with self.assertNumQueries(2):
            u = User.objects.select_related().get(username="test")
            self.assertEqual(u.userstat.posts, 150)

    def test_follow_from_child_class(self):
        """
        Tests the retrieval of an `AdvancedUserStat` instance with specific conditions using `select_related`. The function asserts that the retrieved instance has the correct `comments` count from its related `statdetails` and the expected `username` from its related `user`. It ensures that only one database query is executed during this process.
        
        :raises AssertionError: If the assertions fail.
        """

        with self.assertNumQueries(1):
            stat = AdvancedUserStat.objects.select_related("user", "statdetails").get(
                posts=200
            )
            self.assertEqual(stat.statdetails.comments, 250)
            self.assertEqual(stat.user.username, "bob")

    def test_follow_inheritance(self):
        """
        Tests following inheritance relationships in the database.
        
        This function asserts that querying a `UserStat` object with `select_related`
        for both `user` and `advanceduserstat` fields results in only one query being
        executed. It then checks if the `posts` attribute of `advanceduserstat` and
        the `username` attribute of `user` are correctly fetched.
        
        - `UserStat`: The model being queried.
        - `select_related`: Used to fetch related
        """

        with self.assertNumQueries(1):
            stat = UserStat.objects.select_related("user", "advanceduserstat").get(
                posts=200
            )
            self.assertEqual(stat.advanceduserstat.posts, 200)
            self.assertEqual(stat.user.username, "bob")
        with self.assertNumQueries(0):
            self.assertEqual(stat.advanceduserstat.user.username, "bob")

    def test_nullable_relation(self):
        """
        Tests the behavior of nullable relations in a database query.
        
        This function creates two `Product` instances, one associated with an `Image`
        and another without. It then performs a database query using `select_related`
        to fetch related objects efficiently. The function asserts that the products
        are correctly ordered by name and checks that the `image` field is properly
        handled, including cases where the relation is null.
        
        - `Image`: An instance of the `Image` model.
        """

        im = Image.objects.create(name="imag1")
        p1 = Product.objects.create(name="Django Plushie", image=im)
        p2 = Product.objects.create(name="Talking Django Plushie")

        with self.assertNumQueries(1):
            result = sorted(
                Product.objects.select_related("image"), key=lambda x: x.name
            )
            self.assertEqual(
                [p.name for p in result], ["Django Plushie", "Talking Django Plushie"]
            )

            self.assertEqual(p1.image, im)
            # Check for ticket #13839
            self.assertIsNone(p2.image)

    def test_missing_reverse(self):
        """
        Ticket #13839: select_related() should NOT cache None
        for missing objects on a reverse 1-1 relation.
        """
        with self.assertNumQueries(1):
            user = User.objects.select_related("userprofile").get(username="bob")
            with self.assertRaises(UserProfile.DoesNotExist):
                user.userprofile

    def test_nullable_missing_reverse(self):
        """
        Ticket #13839: select_related() should NOT cache None
        for missing objects on a reverse 0-1 relation.
        """
        Image.objects.create(name="imag1")

        with self.assertNumQueries(1):
            image = Image.objects.select_related("product").get()
            with self.assertRaises(Product.DoesNotExist):
                image.product

    def test_parent_only(self):
        """
        Tests retrieving a `Parent1` instance with its related `Child1` using `select_related`. The function performs two queries:
        - The first query retrieves the `Parent1` instance with its related `Child1` using `select_related`.
        - The second query attempts to access the `child1` attribute of the retrieved `Parent1` instance, expecting it to raise a `DoesNotExist` exception without performing any additional database queries.
        
        :raises: `Child1.DoesNotExist`
        """

        with self.assertNumQueries(1):
            p = Parent1.objects.select_related("child1").get(name1="Only Parent1")
        with self.assertNumQueries(0):
            with self.assertRaises(Child1.DoesNotExist):
                p.child1

    def test_multiple_subclass(self):
        """
        Tests the retrieval of a Parent1 object with its related Child1 object using select_related. Ensures that only one database query is executed and verifies that the related Child1 object has the correct name2 attribute.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the retrieved Parent1 object does not have the expected related Child1 object or if the name2 attribute of the Child1 object is incorrect.
        
        Important Functions:
        - `Parent1.objects.select
        """

        with self.assertNumQueries(1):
            p = Parent1.objects.select_related("child1").get(name1="Child1 Parent1")
            self.assertEqual(p.child1.name2, "Child1 Parent2")

    def test_onetoone_with_subclass(self):
        """
        Tests one-to-one relationship with a subclass using `select_related`. The function queries the database to retrieve a `Parent2` instance with the name 'Child2 Parent2' and its related `Child2` instance. It then asserts that the `name1` attribute of the `Child2` instance is 'Child2 Parent1'. The query is optimized using `select_related` to reduce the number of queries to the database to 1.
        """

        with self.assertNumQueries(1):
            p = Parent2.objects.select_related("child2").get(name2="Child2 Parent2")
            self.assertEqual(p.child2.name1, "Child2 Parent1")

    def test_onetoone_with_two_subclasses(self):
        """
        Tests the behavior of one-to-one relationships with two subclasses using `select_related`.
        
        This function verifies that when querying a `Parent2` instance with related `Child2` and `Child3` instances,
        the appropriate number of database queries are executed and the expected relationships are correctly fetched.
        
        - `Parent2`: The primary parent model.
        - `Child2`: A subclass of `Parent2` with a one-to-one relationship to `Child3`.
        - `Child3`:
        """

        with self.assertNumQueries(1):
            p = Parent2.objects.select_related("child2", "child2__child3").get(
                name2="Child2 Parent2"
            )
            self.assertEqual(p.child2.name1, "Child2 Parent1")
            with self.assertRaises(Child3.DoesNotExist):
                p.child2.child3
        p3 = Parent2(name2="Child3 Parent2")
        p3.save()
        c2 = Child3(name1="Child3 Parent1", parent2=p3, value=2, value3=3)
        c2.save()
        with self.assertNumQueries(1):
            p = Parent2.objects.select_related("child2", "child2__child3").get(
                name2="Child3 Parent2"
            )
            self.assertEqual(p.child2.name1, "Child3 Parent1")
            self.assertEqual(p.child2.child3.value3, 3)
            self.assertEqual(p.child2.child3.value, p.child2.value)
            self.assertEqual(p.child2.name1, p.child2.child3.name1)

    def test_multiinheritance_two_subclasses(self):
        """
        Tests multi-inheritance with two subclasses.
        
        This function verifies that when querying `Parent1` and `Parent2` objects,
        related objects such as `child1` and `child1__child4` are correctly fetched
        using `select_related`. It ensures that the relationships between the parent
        and child objects are properly established and that queries are optimized
        by limiting the number of database queries to one.
        
        - `Parent1` and `Parent2`: The parent models
        """

        with self.assertNumQueries(1):
            p = Parent1.objects.select_related("child1", "child1__child4").get(
                name1="Child1 Parent1"
            )
            self.assertEqual(p.child1.name2, "Child1 Parent2")
            self.assertEqual(p.child1.name1, p.name1)
            with self.assertRaises(Child4.DoesNotExist):
                p.child1.child4
        Child4(name1="n1", name2="n2", value=1, value4=4).save()
        with self.assertNumQueries(1):
            p = Parent2.objects.select_related("child1", "child1__child4").get(
                name2="n2"
            )
            self.assertEqual(p.name2, "n2")
            self.assertEqual(p.child1.name1, "n1")
            self.assertEqual(p.child1.name2, p.name2)
            self.assertEqual(p.child1.value, 1)
            self.assertEqual(p.child1.child4.name1, p.child1.name1)
            self.assertEqual(p.child1.child4.name2, p.child1.name2)
            self.assertEqual(p.child1.child4.value, p.child1.value)
            self.assertEqual(p.child1.child4.value4, 4)

    def test_inheritance_deferred(self):
        """
        Tests inheritance and deferred loading of related objects.
        
        This function creates an instance of `Child4` and then performs multiple queries
        to retrieve related data from `Parent2`. It uses `select_related` and `only` to
        optimize the queries. The function asserts that the correct values are retrieved
        and that deferred loading works as expected.
        
        - `Child4`: The child model being created.
        - `Parent2`: The parent model being queried.
        - `select
        """

        c = Child4.objects.create(name1="n1", name2="n2", value=1, value4=4)
        with self.assertNumQueries(1):
            p = (
                Parent2.objects.select_related("child1")
                .only("id2", "child1__value")
                .get(name2="n2")
            )
            self.assertEqual(p.id2, c.id2)
            self.assertEqual(p.child1.value, 1)
        p = (
            Parent2.objects.select_related("child1")
            .only("id2", "child1__value")
            .get(name2="n2")
        )
        with self.assertNumQueries(1):
            self.assertEqual(p.name2, "n2")
        p = (
            Parent2.objects.select_related("child1")
            .only("id2", "child1__value")
            .get(name2="n2")
        )
        with self.assertNumQueries(1):
            self.assertEqual(p.child1.name2, "n2")

    def test_inheritance_deferred2(self):
        """
        Tests deferred loading of related objects in a multi-level inheritance scenario.
        
        This function creates an instance of `Child4` and queries `Parent2` objects using
        `select_related` and `only` to optimize database queries. It then verifies that
        related objects are correctly loaded and accessed.
        
        - `Child4`: The child model with multiple inheritance.
        - `Parent2`: The parent model with a related object.
        - `select_related`: Used to perform optimized joins for
        """

        c = Child4.objects.create(name1="n1", name2="n2", value=1, value4=4)
        qs = Parent2.objects.select_related("child1", "child1__child4").only(
            "id2", "child1__value", "child1__child4__value4"
        )
        with self.assertNumQueries(1):
            p = qs.get(name2="n2")
            self.assertEqual(p.id2, c.id2)
            self.assertEqual(p.child1.value, 1)
            self.assertEqual(p.child1.child4.value4, 4)
            self.assertEqual(p.child1.child4.id2, c.id2)
        p = qs.get(name2="n2")
        with self.assertNumQueries(1):
            self.assertEqual(p.child1.name2, "n2")
        p = qs.get(name2="n2")
        with self.assertNumQueries(0):
            self.assertEqual(p.child1.name1, "n1")
            self.assertEqual(p.child1.child4.name1, "n1")

    def test_self_relation(self):
        """
        Tests the functionality of a self-referential linked list model.
        
        This test creates two instances of `LinkedList` where one instance points to another using the `previous_item` field. It then queries the database to retrieve the first item and checks if its `next_item` is correctly set to the second item.
        
        :param self: The current instance of the test class.
        :return: None
        """

        item1 = LinkedList.objects.create(name="item1")
        LinkedList.objects.create(name="item2", previous_item=item1)
        with self.assertNumQueries(1):
            item1_db = LinkedList.objects.select_related("next_item").get(name="item1")
            self.assertEqual(item1_db.next_item.name, "item2")


class ReverseSelectRelatedValidationTests(SimpleTestCase):
    """
    Rverse related fields should be listed in the validation message when an
    invalid field is given in select_related().
    """

    non_relational_error = (
        "Non-relational field given in select_related: '%s'. Choices are: %s"
    )
    invalid_error = (
        "Invalid field name(s) given in select_related: '%s'. Choices are: %s"
    )

    def test_reverse_related_validation(self):
        """
        Tests reverse related validation for specific fields.
        
        Args:
        None
        
        Raises:
        FieldError: If the field is not related or invalid.
        
        Summary:
        This function tests reverse related validation by attempting to select related objects using invalid and non-relational fields. It raises a FieldError with specific error messages for both cases.
        
        Important Functions:
        - `FieldError`: Raised when the field is not related or invalid.
        - `select_related`: Used to fetch related objects in a
        """

        fields = "userprofile, userstat"

        with self.assertRaisesMessage(
            FieldError, self.invalid_error % ("foobar", fields)
        ):
            list(User.objects.select_related("foobar"))

        with self.assertRaisesMessage(
            FieldError, self.non_relational_error % ("username", fields)
        ):
            list(User.objects.select_related("username"))

    def test_reverse_related_validation_with_filtered_relation(self):
        """
        Tests reverse related validation with a filtered relation.
        
        Args:
        None
        
        Raises:
        FieldError: If the `select_related` method is called with an invalid field name.
        
        Summary:
        This function tests the validation of reverse related fields when using a filtered relation. It uses the `FilteredRelation` function to filter the 'userprofile' field and attempts to select related objects with an invalid field name ('foobar'). The expected outcome is to raise a `FieldError` with a specific
        """

        fields = "userprofile, userstat, relation"
        with self.assertRaisesMessage(
            FieldError, self.invalid_error % ("foobar", fields)
        ):
            list(
                User.objects.annotate(
                    relation=FilteredRelation("userprofile")
                ).select_related("foobar")
            )
