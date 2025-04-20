from django.test import TestCase

from .models import Article, Car, Driver, Reporter


class ManyToOneNullTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a Reporter.
        cls.r = Reporter(name="John Smith")
        cls.r.save()
        # Create an Article.
        cls.a = Article(headline="First", reporter=cls.r)
        cls.a.save()
        # Create an Article via the Reporter object.
        cls.a2 = cls.r.article_set.create(headline="Second")
        # Create an Article with no Reporter by passing "reporter=None".
        cls.a3 = Article(headline="Third", reporter=None)
        cls.a3.save()
        # Create another article and reporter
        cls.r2 = Reporter(name="Paul Jones")
        cls.r2.save()
        cls.a4 = cls.r2.article_set.create(headline="Fourth")

    def test_get_related(self):
        """
        Tests the functionality of getting related objects in a model relationship.
        
        This function asserts that the reporter of an article is correctly linked to the expected reporter object.
        It first checks the direct relationship using the 'reporter' field of the article instance.
        Then, it retrieves the reporter object through the 'reporter' field and asserts its ID matches the expected reporter's ID.
        
        Parameters:
        self (TestInstance): The test instance that contains the article and reporter objects.
        
        Returns:
        None: This function does
        """

        self.assertEqual(self.a.reporter.id, self.r.id)
        # Article objects have access to their related Reporter objects.
        r = self.a.reporter
        self.assertEqual(r.id, self.r.id)

    def test_created_via_related_set(self):
        self.assertEqual(self.a2.reporter.id, self.r.id)

    def test_related_set(self):
        # Reporter objects have access to their related Article objects.
        self.assertSequenceEqual(self.r.article_set.all(), [self.a, self.a2])
        self.assertSequenceEqual(
            self.r.article_set.filter(headline__startswith="Fir"), [self.a]
        )
        self.assertEqual(self.r.article_set.count(), 2)

    def test_created_without_related(self):
        """
        Tests the creation and management of an Article instance without a related Reporter.
        
        This function verifies that an Article instance can be created without a related Reporter and that the related field can be managed properly. It also checks the behavior of filtering and modifying the related set.
        
        Key Parameters:
        - None
        
        Keywords:
        - reporter: The related Reporter instance associated with the Article.
        - a3: The Article instance being tested.
        - r: The Reporter instance related to the Article.
        
        Input:
        - The function does not take
        """

        self.assertIsNone(self.a3.reporter)
        # Need to reget a3 to refresh the cache
        a3 = Article.objects.get(pk=self.a3.pk)
        with self.assertRaises(AttributeError):
            getattr(a3.reporter, "id")
        # Accessing an article's 'reporter' attribute returns None
        # if the reporter is set to None.
        self.assertIsNone(a3.reporter)
        # To retrieve the articles with no reporters set, use "reporter__isnull=True".
        self.assertSequenceEqual(
            Article.objects.filter(reporter__isnull=True), [self.a3]
        )
        # We can achieve the same thing by filtering for the case where the
        # reporter is None.
        self.assertSequenceEqual(Article.objects.filter(reporter=None), [self.a3])
        # Set the reporter for the Third article
        self.assertSequenceEqual(self.r.article_set.all(), [self.a, self.a2])
        self.r.article_set.add(a3)
        self.assertSequenceEqual(
            self.r.article_set.all(),
            [self.a, self.a2, self.a3],
        )
        # Remove an article from the set, and check that it was removed.
        self.r.article_set.remove(a3)
        self.assertSequenceEqual(self.r.article_set.all(), [self.a, self.a2])
        self.assertSequenceEqual(
            Article.objects.filter(reporter__isnull=True), [self.a3]
        )

    def test_remove_from_wrong_set(self):
        self.assertSequenceEqual(self.r2.article_set.all(), [self.a4])
        # Try to remove a4 from a set it does not belong to
        with self.assertRaises(Reporter.DoesNotExist):
            self.r.article_set.remove(self.a4)
        self.assertSequenceEqual(self.r2.article_set.all(), [self.a4])

    def test_set(self):
        # Use manager.set() to allocate ForeignKey. Null is legal, so existing
        # members of the set that are not in the assignment set are set to null.
        self.r2.article_set.set([self.a2, self.a3])
        self.assertSequenceEqual(self.r2.article_set.all(), [self.a2, self.a3])
        # Use manager.set(clear=True)
        self.r2.article_set.set([self.a3, self.a4], clear=True)
        self.assertSequenceEqual(self.r2.article_set.all(), [self.a4, self.a3])
        # Clear the rest of the set
        self.r2.article_set.set([])
        self.assertSequenceEqual(self.r2.article_set.all(), [])
        self.assertSequenceEqual(
            Article.objects.filter(reporter__isnull=True),
            [self.a4, self.a2, self.a3],
        )

    def test_set_clear_non_bulk(self):
        # 2 queries for clear(), 1 for add(), and 1 to select objects.
        with self.assertNumQueries(4):
            self.r.article_set.set([self.a], bulk=False, clear=True)

    def test_assign_clear_related_set(self):
        """
        Test the assignment and clearing of a related set.
        
        This function tests the assignment and clearing of a related set using the ForeignKey descriptor. It sets the related articles for reporter r2 and then clears the related articles for reporter r. The function asserts that the related articles are correctly set and cleared.
        
        Parameters:
        - self: The test case instance.
        
        Returns:
        - None: This function is used for testing and does not return any value.
        
        Key Steps:
        1. Assign a set of articles to the reporter r
        """

        # Use descriptor assignment to allocate ForeignKey. Null is legal, so
        # existing members of the set that are not in the assignment set are
        # set to null.
        self.r2.article_set.set([self.a2, self.a3])
        self.assertSequenceEqual(self.r2.article_set.all(), [self.a2, self.a3])
        # Clear the rest of the set
        self.r.article_set.clear()
        self.assertSequenceEqual(self.r.article_set.all(), [])
        self.assertSequenceEqual(
            Article.objects.filter(reporter__isnull=True),
            [self.a, self.a4],
        )

    def test_assign_with_queryset(self):
        # Querysets used in reverse FK assignments are pre-evaluated
        # so their value isn't affected by the clearing operation in
        # RelatedManager.set() (#19816).
        self.r2.article_set.set([self.a2, self.a3])

        qs = self.r2.article_set.filter(headline="Second")
        self.r2.article_set.set(qs)

        self.assertEqual(1, self.r2.article_set.count())
        self.assertEqual(1, qs.count())

    def test_add_efficiency(self):
        r = Reporter.objects.create()
        articles = []
        for _ in range(3):
            articles.append(Article.objects.create())
        with self.assertNumQueries(1):
            r.article_set.add(*articles)
        self.assertEqual(r.article_set.count(), 3)

    def test_clear_efficiency(self):
        """
        Tests the efficiency of the clear method for a Reporter model's article_set.
        
        This function creates a Reporter instance and three associated Article instances. It then measures the efficiency of the clear method by clearing the article_set and ensuring that no queries are executed in the process. Finally, it verifies that the article_set is empty after the clear operation.
        
        Parameters:
        None
        
        Keywords:
        None
        
        Returns:
        None
        """

        r = Reporter.objects.create()
        for _ in range(3):
            r.article_set.create()
        with self.assertNumQueries(1):
            r.article_set.clear()
        self.assertEqual(r.article_set.count(), 0)

    def test_related_null_to_field(self):
        c1 = Car.objects.create()
        d1 = Driver.objects.create()
        self.assertIs(d1.car, None)
        with self.assertNumQueries(0):
            self.assertEqual(list(c1.drivers.all()), [])

    def test_unsaved(self):
        """
        Tests the behavior of the 'drivers' relationship on a 'Car' instance that has not been saved to the database.
        
        This function asserts that attempting to access the 'drivers' relationship on a 'Car' instance without a primary key value raises a ValueError with a specific error message.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Returns:
        - None
        
        Raises:
        - ValueError: If the 'Car' instance is accessed without a primary key value, a ValueError is raised with the message: "'
        """

        msg = (
            "'Car' instance needs to have a primary key value before this relationship "
            "can be used."
        )
        with self.assertRaisesMessage(ValueError, msg):
            Car(make="Ford").drivers.all()

    def test_related_null_to_field_related_managers(self):
        car = Car.objects.create(make=None)
        driver = Driver.objects.create()
        msg = (
            f'"{car!r}" needs to have a value for field "make" before this '
            f"relationship can be used."
        )
        with self.assertRaisesMessage(ValueError, msg):
            car.drivers.add(driver)
        with self.assertRaisesMessage(ValueError, msg):
            car.drivers.create()
        with self.assertRaisesMessage(ValueError, msg):
            car.drivers.get_or_create()
        with self.assertRaisesMessage(ValueError, msg):
            car.drivers.update_or_create()
        with self.assertRaisesMessage(ValueError, msg):
            car.drivers.remove(driver)
        with self.assertRaisesMessage(ValueError, msg):
            car.drivers.clear()
        with self.assertRaisesMessage(ValueError, msg):
            car.drivers.set([driver])

        with self.assertNumQueries(0):
            self.assertEqual(car.drivers.count(), 0)
