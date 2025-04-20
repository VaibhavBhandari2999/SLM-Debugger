from django.core.exceptions import FieldError
from django.db.models import FilteredRelation
from django.test import SimpleTestCase, TestCase

from .models import (
    AdvancedUserStat, Child1, Child2, Child3, Child4, Image, LinkedList,
    Parent1, Parent2, Product, StatDetails, User, UserProfile, UserStat,
    UserStatResult,
)


class ReverseSelectRelatedTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the tests.
        
        This method creates a series of test data objects for use in testing. It creates:
        - Two User objects with usernames "test" and "bob".
        - UserStat and AdvancedUserStat objects with various attributes like posts, karma, and results.
        - StatDetails objects associated with the UserStat and AdvancedUserStat objects.
        - Parent1 and Child1 objects.
        - Parent2 and Child2 objects.
        
        Parameters:
        None
        
        Returns:
        None
        """

        user = User.objects.create(username="test")
        UserProfile.objects.create(user=user, state="KS", city="Lawrence")
        results = UserStatResult.objects.create(results='first results')
        userstat = UserStat.objects.create(user=user, posts=150, results=results)
        StatDetails.objects.create(base_stats=userstat, comments=259)

        user2 = User.objects.create(username="bob")
        results2 = UserStatResult.objects.create(results='moar results')
        advstat = AdvancedUserStat.objects.create(user=user2, posts=200, karma=5, results=results2)
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
        with self.assertNumQueries(1):
            u = User.objects.select_related("userprofile").get(username="test")
            self.assertEqual(u.userprofile.state, "KS")

    def test_follow_next_level(self):
        with self.assertNumQueries(1):
            u = User.objects.select_related("userstat__results").get(username="test")
            self.assertEqual(u.userstat.posts, 150)
            self.assertEqual(u.userstat.results.results, 'first results')

    def test_follow_two(self):
        """
        Tests the follow_two method.
        
        This method performs a database query to retrieve a user object with the username 'test',
        selecting related userprofile and userstat objects. It then checks the state of the user's
        userprofile and the number of posts in the userstat.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The state of the user's userprofile should be 'KS'.
        - The number of posts in the userstat should be 150.
        """

        with self.assertNumQueries(1):
            u = User.objects.select_related("userprofile", "userstat").get(username="test")
            self.assertEqual(u.userprofile.state, "KS")
            self.assertEqual(u.userstat.posts, 150)

    def test_follow_two_next_level(self):
        with self.assertNumQueries(1):
            u = User.objects.select_related("userstat__results", "userstat__statdetails").get(username="test")
            self.assertEqual(u.userstat.results.results, 'first results')
            self.assertEqual(u.userstat.statdetails.comments, 259)

    def test_forward_and_back(self):
        with self.assertNumQueries(1):
            stat = UserStat.objects.select_related("user__userprofile").get(user__username="test")
            self.assertEqual(stat.user.userprofile.state, 'KS')
            self.assertEqual(stat.user.userstat.posts, 150)

    def test_back_and_forward(self):
        with self.assertNumQueries(1):
            u = User.objects.select_related("userstat").get(username="test")
            self.assertEqual(u.userstat.user.username, 'test')

    def test_not_followed_by_default(self):
        """
        Tests if a user is not followed by any default value.
        
        This method asserts that exactly two database queries are executed when retrieving a user with the username 'test' and then checking their associated userstat's posts count. The user is expected to be fetched with select_related to optimize the query.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Raises:
        - AssertionError: If the number of queries does not match the expected count or if the user's
        """

        with self.assertNumQueries(2):
            u = User.objects.select_related().get(username="test")
            self.assertEqual(u.userstat.posts, 150)

    def test_follow_from_child_class(self):
        """
        Tests the follow functionality from a child class.
        
        This method asserts that the number of database queries is limited to one when fetching an AdvancedUserStat object with specific conditions. The object is expected to be pre-joined with its related 'user' and 'statdetails' models. The test checks that the 'comments' field from 'statdetails' and the 'username' field from 'user' match the expected values.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The number
        """

        with self.assertNumQueries(1):
            stat = AdvancedUserStat.objects.select_related('user', 'statdetails').get(posts=200)
            self.assertEqual(stat.statdetails.comments, 250)
            self.assertEqual(stat.user.username, 'bob')

    def test_follow_inheritance(self):
        with self.assertNumQueries(1):
            stat = UserStat.objects.select_related('user', 'advanceduserstat').get(posts=200)
            self.assertEqual(stat.advanceduserstat.posts, 200)
            self.assertEqual(stat.user.username, 'bob')
        with self.assertNumQueries(0):
            self.assertEqual(stat.advanceduserstat.user.username, 'bob')

    def test_nullable_relation(self):
        im = Image.objects.create(name="imag1")
        p1 = Product.objects.create(name="Django Plushie", image=im)
        p2 = Product.objects.create(name="Talking Django Plushie")

        with self.assertNumQueries(1):
            result = sorted(Product.objects.select_related("image"), key=lambda x: x.name)
            self.assertEqual([p.name for p in result], ["Django Plushie", "Talking Django Plushie"])

            self.assertEqual(p1.image, im)
            # Check for ticket #13839
            self.assertIsNone(p2.image)

    def test_missing_reverse(self):
        """
        Ticket #13839: select_related() should NOT cache None
        for missing objects on a reverse 1-1 relation.
        """
        with self.assertNumQueries(1):
            user = User.objects.select_related('userprofile').get(username='bob')
            with self.assertRaises(UserProfile.DoesNotExist):
                user.userprofile

    def test_nullable_missing_reverse(self):
        """
        Ticket #13839: select_related() should NOT cache None
        for missing objects on a reverse 0-1 relation.
        """
        Image.objects.create(name="imag1")

        with self.assertNumQueries(1):
            image = Image.objects.select_related('product').get()
            with self.assertRaises(Product.DoesNotExist):
                image.product

    def test_parent_only(self):
        with self.assertNumQueries(1):
            p = Parent1.objects.select_related('child1').get(name1="Only Parent1")
        with self.assertNumQueries(0):
            with self.assertRaises(Child1.DoesNotExist):
                p.child1

    def test_multiple_subclass(self):
        """
        Tests the retrieval of a Parent1 object with its related Child1 object using select_related. The function asserts that only one database query is executed during the retrieval. The Parent1 object is fetched based on the name1 field, and the related Child1 object is expected to have a specific name2 value.
        
        Parameters:
        None
        
        Keywords:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the number of database queries exceeds one or if the name2 field of the related Child1
        """

        with self.assertNumQueries(1):
            p = Parent1.objects.select_related('child1').get(name1="Child1 Parent1")
            self.assertEqual(p.child1.name2, 'Child1 Parent2')

    def test_onetoone_with_subclass(self):
        """
        Tests the one-to-one relationship with a subclass. This function retrieves a Parent2 object with its related Child2 object using select_related. It asserts that the number of queries executed is exactly one and verifies that the related Child2 object's name1 attribute is 'Child2 Parent1'.
        
        Parameters:
        None
        
        Keywords:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the number of queries is not one or if the related Child2 object's name1 attribute does not match '
        """

        with self.assertNumQueries(1):
            p = Parent2.objects.select_related('child2').get(name2="Child2 Parent2")
            self.assertEqual(p.child2.name1, 'Child2 Parent1')

    def test_onetoone_with_two_subclasses(self):
        with self.assertNumQueries(1):
            p = Parent2.objects.select_related('child2', "child2__child3").get(name2="Child2 Parent2")
            self.assertEqual(p.child2.name1, 'Child2 Parent1')
            with self.assertRaises(Child3.DoesNotExist):
                p.child2.child3
        p3 = Parent2(name2="Child3 Parent2")
        p3.save()
        c2 = Child3(name1="Child3 Parent1", parent2=p3, value=2, value3=3)
        c2.save()
        with self.assertNumQueries(1):
            p = Parent2.objects.select_related('child2', "child2__child3").get(name2="Child3 Parent2")
            self.assertEqual(p.child2.name1, 'Child3 Parent1')
            self.assertEqual(p.child2.child3.value3, 3)
            self.assertEqual(p.child2.child3.value, p.child2.value)
            self.assertEqual(p.child2.name1, p.child2.child3.name1)

    def test_multiinheritance_two_subclasses(self):
        with self.assertNumQueries(1):
            p = Parent1.objects.select_related('child1', 'child1__child4').get(name1="Child1 Parent1")
            self.assertEqual(p.child1.name2, 'Child1 Parent2')
            self.assertEqual(p.child1.name1, p.name1)
            with self.assertRaises(Child4.DoesNotExist):
                p.child1.child4
        Child4(name1='n1', name2='n2', value=1, value4=4).save()
        with self.assertNumQueries(1):
            p = Parent2.objects.select_related('child1', 'child1__child4').get(name2="n2")
            self.assertEqual(p.name2, 'n2')
            self.assertEqual(p.child1.name1, 'n1')
            self.assertEqual(p.child1.name2, p.name2)
            self.assertEqual(p.child1.value, 1)
            self.assertEqual(p.child1.child4.name1, p.child1.name1)
            self.assertEqual(p.child1.child4.name2, p.child1.name2)
            self.assertEqual(p.child1.child4.value, p.child1.value)
            self.assertEqual(p.child1.child4.value4, 4)

    def test_inheritance_deferred(self):
        """
        Tests inheritance and deferred loading in a database query scenario.
        
        This function creates an instance of Child4 and then performs multiple database queries to retrieve and verify data from Parent2, which is related to Child4 through inheritance. The queries are optimized using `select_related` and `only` to minimize the number of database hits.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
        
        Assertions:
        - Verifies that the correct values are retrieved and that deferred loading
        """

        c = Child4.objects.create(name1='n1', name2='n2', value=1, value4=4)
        with self.assertNumQueries(1):
            p = Parent2.objects.select_related('child1').only(
                'id2', 'child1__value').get(name2="n2")
            self.assertEqual(p.id2, c.id2)
            self.assertEqual(p.child1.value, 1)
        p = Parent2.objects.select_related('child1').only(
            'id2', 'child1__value').get(name2="n2")
        with self.assertNumQueries(1):
            self.assertEqual(p.name2, 'n2')
        p = Parent2.objects.select_related('child1').only(
            'id2', 'child1__value').get(name2="n2")
        with self.assertNumQueries(1):
            self.assertEqual(p.child1.name2, 'n2')

    def test_inheritance_deferred2(self):
        c = Child4.objects.create(name1='n1', name2='n2', value=1, value4=4)
        qs = Parent2.objects.select_related('child1', 'child1__child4').only(
            'id2', 'child1__value', 'child1__child4__value4')
        with self.assertNumQueries(1):
            p = qs.get(name2="n2")
            self.assertEqual(p.id2, c.id2)
            self.assertEqual(p.child1.value, 1)
            self.assertEqual(p.child1.child4.value4, 4)
            self.assertEqual(p.child1.child4.id2, c.id2)
        p = qs.get(name2="n2")
        with self.assertNumQueries(1):
            self.assertEqual(p.child1.name2, 'n2')
        p = qs.get(name2="n2")
        with self.assertNumQueries(0):
            self.assertEqual(p.child1.name1, 'n1')
            self.assertEqual(p.child1.child4.name1, 'n1')

    def test_self_relation(self):
        item1 = LinkedList.objects.create(name='item1')
        LinkedList.objects.create(name='item2', previous_item=item1)
        with self.assertNumQueries(1):
            item1_db = LinkedList.objects.select_related('next_item').get(name='item1')
            self.assertEqual(item1_db.next_item.name, 'item2')


class ReverseSelectRelatedValidationTests(SimpleTestCase):
    """
    Rverse related fields should be listed in the validation message when an
    invalid field is given in select_related().
    """
    non_relational_error = "Non-relational field given in select_related: '%s'. Choices are: %s"
    invalid_error = "Invalid field name(s) given in select_related: '%s'. Choices are: %s"

    def test_reverse_related_validation(self):
        """
        Tests the validation of reverse related fields in a query.
        
        This function checks if the provided fields are valid reverse related fields for the User model. It raises a FieldError with a specific message if the field is invalid or non-relational.
        
        Parameters:
        None
        
        Raises:
        FieldError: If the provided field is invalid or non-relational.
        
        Usage:
        This function is used to test the validation of reverse related fields in a query. It is expected to be called within a test case to ensure
        """

        fields = 'userprofile, userstat'

        with self.assertRaisesMessage(FieldError, self.invalid_error % ('foobar', fields)):
            list(User.objects.select_related('foobar'))

        with self.assertRaisesMessage(FieldError, self.non_relational_error % ('username', fields)):
            list(User.objects.select_related('username'))

    def test_reverse_related_validation_with_filtered_relation(self):
        fields = 'userprofile, userstat, relation'
        with self.assertRaisesMessage(FieldError, self.invalid_error % ('foobar', fields)):
            list(User.objects.annotate(relation=FilteredRelation('userprofile')).select_related('foobar'))


        with self.assertRaisesMessage(FieldError, self.invalid_error % ('foobar', fields)):
            list(User.objects.select_related('foobar'))

        with self.assertRaisesMessage(FieldError, self.non_relational_error % ('username', fields)):
            list(User.objects.select_related('username'))

    def test_reverse_related_validation_with_filtered_relation(self):
        fields = 'userprofile, userstat, relation'
        with self.assertRaisesMessage(FieldError, self.invalid_error % ('foobar', fields)):
            list(User.objects.annotate(relation=FilteredRelation('userprofile')).select_related('foobar'))
'userprofile')).select_related('foobar'))
