from django.test import TestCase

from .models import Article, Car, Driver, Reporter


class ManyToOneNullTests(TestCase):
    def setUp(self):
        """
        Sets up the test environment with various instances of Reporter and Article objects.
        
        This method initializes the test environment by creating several instances of Reporter and Article objects. The setup includes:
        
        - Creating a Reporter named 'John Smith' and saving it to the database.
        - Creating an Article titled "First" associated with the 'John Smith' Reporter.
        - Creating another Article titled "Second" associated with the 'John Smith' Reporter using the Reporter's related manager.
        - Creating an Article titled "Third" without associ
        """

        # Create a Reporter.
        self.r = Reporter(name='John Smith')
        self.r.save()
        # Create an Article.
        self.a = Article(headline="First", reporter=self.r)
        self.a.save()
        # Create an Article via the Reporter object.
        self.a2 = self.r.article_set.create(headline="Second")
        # Create an Article with no Reporter by passing "reporter=None".
        self.a3 = Article(headline="Third", reporter=None)
        self.a3.save()
        # Create another article and reporter
        self.r2 = Reporter(name='Paul Jones')
        self.r2.save()
        self.a4 = self.r2.article_set.create(headline='Fourth')

    def test_get_related(self):
        """
        Tests the functionality of the 'get_related' method in a model.
        
        This method verifies that an Article object can access its related Reporter object and that both methods yield the same reporter ID.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The reporter ID of the Article object should match the reporter ID of the related Reporter object.
        - The reporter ID of the Article object should match the reporter ID of the second related Reporter object.
        """

        self.assertEqual(self.a.reporter.id, self.r.id)
        # Article objects have access to their related Reporter objects.
        r = self.a.reporter
        self.assertEqual(r.id, self.r.id)

    def test_created_via_related_set(self):
        self.assertEqual(self.a2.reporter.id, self.r.id)

    def test_related_set(self):
        # Reporter objects have access to their related Article objects.
        self.assertQuerysetEqual(self.r.article_set.all(), ['<Article: First>', '<Article: Second>'])
        self.assertQuerysetEqual(self.r.article_set.filter(headline__startswith='Fir'), ['<Article: First>'])
        self.assertEqual(self.r.article_set.count(), 2)

    def test_created_without_related(self):
        self.assertIsNone(self.a3.reporter)
        # Need to reget a3 to refresh the cache
        a3 = Article.objects.get(pk=self.a3.pk)
        with self.assertRaises(AttributeError):
            getattr(a3.reporter, 'id')
        # Accessing an article's 'reporter' attribute returns None
        # if the reporter is set to None.
        self.assertIsNone(a3.reporter)
        # To retrieve the articles with no reporters set, use "reporter__isnull=True".
        self.assertQuerysetEqual(Article.objects.filter(reporter__isnull=True), ['<Article: Third>'])
        # We can achieve the same thing by filtering for the case where the
        # reporter is None.
        self.assertQuerysetEqual(Article.objects.filter(reporter=None), ['<Article: Third>'])
        # Set the reporter for the Third article
        self.assertQuerysetEqual(self.r.article_set.all(), ['<Article: First>', '<Article: Second>'])
        self.r.article_set.add(a3)
        self.assertQuerysetEqual(
            self.r.article_set.all(),
            ['<Article: First>', '<Article: Second>', '<Article: Third>']
        )
        # Remove an article from the set, and check that it was removed.
        self.r.article_set.remove(a3)
        self.assertQuerysetEqual(self.r.article_set.all(), ['<Article: First>', '<Article: Second>'])
        self.assertQuerysetEqual(Article.objects.filter(reporter__isnull=True), ['<Article: Third>'])

    def test_remove_from_wrong_set(self):
        self.assertQuerysetEqual(self.r2.article_set.all(), ['<Article: Fourth>'])
        # Try to remove a4 from a set it does not belong to
        with self.assertRaises(Reporter.DoesNotExist):
            self.r.article_set.remove(self.a4)
        self.assertQuerysetEqual(self.r2.article_set.all(), ['<Article: Fourth>'])

    def test_set(self):
        """
        Tests the functionality of the ForeignKey set() method in Django.
        
        This method is used to set the related objects for a ForeignKey. It can be used to:
        1. Set the related objects, allowing existing members of the set that are not in the assignment set to be set to null.
        2. Set the related objects and clear the rest of the set.
        3. Clear the set entirely.
        
        Parameters:
        - self: The current test case instance.
        
        Key Methods:
        - `self.r2.article_set.set
        """

        # Use manager.set() to allocate ForeignKey. Null is legal, so existing
        # members of the set that are not in the assignment set are set to null.
        self.r2.article_set.set([self.a2, self.a3])
        self.assertQuerysetEqual(self.r2.article_set.all(), ['<Article: Second>', '<Article: Third>'])
        # Use manager.set(clear=True)
        self.r2.article_set.set([self.a3, self.a4], clear=True)
        self.assertQuerysetEqual(self.r2.article_set.all(), ['<Article: Fourth>', '<Article: Third>'])
        # Clear the rest of the set
        self.r2.article_set.set([])
        self.assertQuerysetEqual(self.r2.article_set.all(), [])
        self.assertQuerysetEqual(
            Article.objects.filter(reporter__isnull=True),
            ['<Article: Fourth>', '<Article: Second>', '<Article: Third>']
        )

    def test_set_clear_non_bulk(self):
        # 2 queries for clear(), 1 for add(), and 1 to select objects.
        with self.assertNumQueries(4):
            self.r.article_set.set([self.a], bulk=False, clear=True)

    def test_assign_clear_related_set(self):
        """
        Tests the functionality of the `clear` method for a ForeignKey relationship.
        
        This function tests the `clear` method of a ForeignKey relationship. It first assigns a set of articles to a reporter, ensuring that the existing members of the set that are not in the new assignment are set to null. Then, it clears the set of articles for another reporter, verifying that all associated articles are set to null.
        
        Key Parameters:
        - `self`: The test case instance.
        
        Keywords:
        - None
        
        Inputs:
        -
        """

        # Use descriptor assignment to allocate ForeignKey. Null is legal, so
        # existing members of the set that are not in the assignment set are
        # set to null.
        self.r2.article_set.set([self.a2, self.a3])
        self.assertQuerysetEqual(self.r2.article_set.all(), ['<Article: Second>', '<Article: Third>'])
        # Clear the rest of the set
        self.r.article_set.clear()
        self.assertQuerysetEqual(self.r.article_set.all(), [])
        self.assertQuerysetEqual(
            Article.objects.filter(reporter__isnull=True),
            ['<Article: First>', '<Article: Fourth>']
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
        r = Reporter.objects.create()
        for _ in range(3):
            r.article_set.create()
        with self.assertNumQueries(1):
            r.article_set.clear()
        self.assertEqual(r.article_set.count(), 0)

    def test_related_null_to_field(self):
        """
        Tests the behavior of a related field that is initially set to null for a Driver model with respect to a Car model.
        
        This function creates an instance of a Car and a Driver. It then checks if the car field of the Driver instance is null and verifies that the list of drivers associated with the Car is empty.
        
        Parameters:
        None
        
        Keywords:
        None
        
        Returns:
        None
        
        Assertions:
        - The car field of the Driver instance should be None.
        - The list of drivers associated
        """

        c1 = Car.objects.create()
        d1 = Driver.objects.create()
        self.assertIs(d1.car, None)
        with self.assertNumQueries(0):
            self.assertEqual(list(c1.drivers.all()), [])
