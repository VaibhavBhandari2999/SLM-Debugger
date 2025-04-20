import datetime

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.views.generic.base import View

from .models import Artist, Author, Book, Page


@override_settings(ROOT_URLCONF='generic_views.urls')
class ListViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the tests in the class.
        
        This method creates and initializes several test instances of models: an Artist, an Author, a Book, and a Page. The Artist and Author instances are created with specific names and slugs. The Book instances are created with names, slugs, page counts, and publication dates. The Book instances are also associated with the Author instances. The Page instance is created with a content string and a template.
        
        Parameters:
        cls (cls): The test
        """

        cls.artist1 = Artist.objects.create(name='Rene Magritte')
        cls.author1 = Author.objects.create(name='Roberto Bolaño', slug='roberto-bolano')
        cls.author2 = Author.objects.create(name='Scott Rosenberg', slug='scott-rosenberg')
        cls.book1 = Book.objects.create(name='2066', slug='2066', pages=800, pubdate=datetime.date(2008, 10, 1))
        cls.book1.authors.add(cls.author1)
        cls.book2 = Book.objects.create(
            name='Dreaming in Code', slug='dreaming-in-code', pages=300, pubdate=datetime.date(2006, 5, 1)
        )
        cls.page1 = Page.objects.create(
            content='I was once bitten by a moose.', template='generic_views/page_template.html'
        )

    def test_items(self):
        res = self.client.get('/list/dict/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/list.html')
        self.assertEqual(res.context['object_list'][0]['first'], 'John')

    def test_queryset(self):
        res = self.client.get('/list/authors/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/author_list.html')
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertIsInstance(res.context['view'], View)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertIsNone(res.context['paginator'])
        self.assertIsNone(res.context['page_obj'])
        self.assertFalse(res.context['is_paginated'])

    def test_paginated_queryset(self):
        """
        Tests the paginated queryset functionality for the author list view.
        
        This test method verifies that the paginated author list view returns the correct status code, template, and paginated data. It checks that the context contains the expected paginated objects, the correct number of objects per page, the total number of pages, and the first and last objects in the paginated list.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The test assumes the existence of a view that lists authors
        """

        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTrue(res.context['is_paginated'])
        self.assertEqual(res.context['page_obj'].number, 1)
        self.assertEqual(res.context['paginator'].num_pages, 4)
        self.assertEqual(res.context['author_list'][0].name, 'Author 00')
        self.assertEqual(list(res.context['author_list'])[-1].name, 'Author 29')

    def test_paginated_queryset_shortdata(self):
        # Short datasets also result in a paginated view.
        res = self.client.get('/list/authors/paginated/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/author_list.html')
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['page_obj'].number, 1)
        self.assertEqual(res.context['paginator'].num_pages, 1)
        self.assertFalse(res.context['is_paginated'])

    def test_paginated_get_page_by_query_string(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/', {'page': '2'})
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 30')
        self.assertEqual(res.context['page_obj'].number, 2)

    def test_paginated_get_last_page_by_query_string(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/', {'page': 'last'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['object_list']), 10)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 90')
        self.assertEqual(res.context['page_obj'].number, 4)

    def test_paginated_get_page_by_urlvar(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/3/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 60')
        self.assertEqual(res.context['page_obj'].number, 3)

    def test_paginated_page_out_of_range(self):
        """
        Tests the behavior of the paginated author list endpoint when a page number is out of range.
        
        This function sends a GET request to the '/list/authors/paginated/<page_number>/' endpoint with a page number that exceeds the total number of available pages. It verifies that the response status code is 404, indicating that the requested page does not exist.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - HTTP status code 4
        """

        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/42/')
        self.assertEqual(res.status_code, 404)

    def test_paginated_invalid_page(self):
        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/?page=frog')
        self.assertEqual(res.status_code, 404)

    def test_paginated_custom_paginator_class(self):
        self._make_authors(7)
        res = self.client.get('/list/authors/paginated/custom_class/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['paginator'].num_pages, 1)
        # Custom pagination allows for 2 orphans on a page size of 5
        self.assertEqual(len(res.context['object_list']), 7)

    def test_paginated_custom_page_kwarg(self):
        """
        Tests the paginated view with a custom page keyword argument.
        
        This function sends a GET request to the '/list/authors/paginated/custom_page_kwarg/' endpoint with a 'pagina' parameter set to '2'. It then checks the response to ensure that the view is functioning correctly.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - pagina: The page number to request, passed as a query parameter.
        
        Input:
        - None
        
        Output:
        - None
        
        Assertions:
        - The status code of the
        """

        self._make_authors(100)
        res = self.client.get('/list/authors/paginated/custom_page_kwarg/', {'pagina': '2'})
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/author_list.html')
        self.assertEqual(len(res.context['object_list']), 30)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertEqual(res.context['author_list'][0].name, 'Author 30')
        self.assertEqual(res.context['page_obj'].number, 2)

    def test_paginated_custom_paginator_constructor(self):
        self._make_authors(7)
        res = self.client.get('/list/authors/paginated/custom_constructor/')
        self.assertEqual(res.status_code, 200)
        # Custom pagination allows for 2 orphans on a page size of 5
        self.assertEqual(len(res.context['object_list']), 7)

    def test_paginated_orphaned_queryset(self):
        """
        Tests for paginated and orphaned queryset handling.
        
        This function tests the behavior of paginated and orphaned queryset in a view. It checks the response status codes and the page number of the paginated queryset.
        
        Parameters:
        - None (the function uses internal data and client setup)
        
        Returns:
        - None (the function asserts conditions through the test framework)
        
        Key Points:
        - The function creates 92 authors using `_make_authors(92)`.
        - It then makes several GET requests to the
        """

        self._make_authors(92)
        res = self.client.get('/list/authors/paginated-orphaned/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 1)
        res = self.client.get(
            '/list/authors/paginated-orphaned/', {'page': 'last'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 3)
        res = self.client.get(
            '/list/authors/paginated-orphaned/', {'page': '3'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['page_obj'].number, 3)
        res = self.client.get(
            '/list/authors/paginated-orphaned/', {'page': '4'})
        self.assertEqual(res.status_code, 404)

    def test_paginated_non_queryset(self):
        res = self.client.get('/list/dict/paginated/')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.context['object_list']), 1)

    def test_verbose_name(self):
        res = self.client.get('/list/artists/')
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/list.html')
        self.assertEqual(list(res.context['object_list']), list(Artist.objects.all()))
        self.assertIs(res.context['artist_list'], res.context['object_list'])
        self.assertIsNone(res.context['paginator'])
        self.assertIsNone(res.context['page_obj'])
        self.assertFalse(res.context['is_paginated'])

    def test_allow_empty_false(self):
        res = self.client.get('/list/authors/notempty/')
        self.assertEqual(res.status_code, 200)
        Author.objects.all().delete()
        res = self.client.get('/list/authors/notempty/')
        self.assertEqual(res.status_code, 404)

    def test_template_name(self):
        res = self.client.get('/list/authors/template_name/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'generic_views/list.html')

    def test_template_name_suffix(self):
        """
        Tests the template name suffix functionality for a view.
        
        This function sends a GET request to the '/list/authors/template_name_suffix/' endpoint and checks the response status code, the context data, and the template used.
        
        Parameters:
        - None (uses self.client and Author model from the test environment)
        
        Returns:
        - None (assertions are used to validate the response)
        
        Key Assertions:
        - The response status code is 200 (OK).
        - The context's 'object_list' contains all authors
        """

        res = self.client.get('/list/authors/template_name_suffix/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'generic_views/author_objects.html')

    def test_context_object_name(self):
        res = self.client.get('/list/authors/context_object_name/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertNotIn('authors', res.context)
        self.assertIs(res.context['author_list'], res.context['object_list'])
        self.assertTemplateUsed(res, 'generic_views/author_list.html')

    def test_duplicate_context_object_name(self):
        """
        Tests the behavior of a view that uses a context object name that is a duplicate of a template context variable.
        
        This function sends a GET request to the '/list/authors/dupe_context_object_name/' URL and checks the response status code, context data, and template used.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The response status code should be 200.
        - The 'object_list' context variable should contain all authors.
        - The 'authors
        """

        res = self.client.get('/list/authors/dupe_context_object_name/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(list(res.context['object_list']), list(Author.objects.all()))
        self.assertNotIn('authors', res.context)
        self.assertNotIn('author_list', res.context)
        self.assertTemplateUsed(res, 'generic_views/author_list.html')

    def test_missing_items(self):
        msg = (
            'AuthorList is missing a QuerySet. Define AuthorList.model, '
            'AuthorList.queryset, or override AuthorList.get_queryset().'
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            self.client.get('/list/authors/invalid/')

    def test_invalid_get_queryset(self):
        """
        Tests the behavior of the AuthorListGetQuerysetReturnsNone view when it does not provide a valid queryset.
        
        This test ensures that if the AuthorListGetQuerysetReturnsNone view is not properly configured with either a 'template_name' attribute or a get_queryset() method that returns a QuerySet, it raises an ImproperlyConfigured exception with a specific error message.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Output:
        - Raises an ImproperlyConfigured exception with the
        """

        msg = (
            "AuthorListGetQuerysetReturnsNone requires either a 'template_name' "
            "attribute or a get_queryset() method that returns a QuerySet."
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            self.client.get('/list/authors/get_queryset/')

    def test_paginated_list_view_does_not_load_entire_table(self):
        """
        Tests the behavior of paginated list views to ensure they do not load the entire database table.
        
        This function verifies that paginated list views only make a limited number of database queries, specifically for testing the pagination of a list of authors. It includes two test cases:
        1. The first test case checks that the non-paginated list view of authors does not load the entire table, ensuring only one query is made.
        2. The second test case checks that the paginated list view of authors also
        """

        # Regression test for #17535
        self._make_authors(3)
        # 1 query for authors
        with self.assertNumQueries(1):
            self.client.get('/list/authors/notempty/')
        # same as above + 1 query to test if authors exist + 1 query for pagination
        with self.assertNumQueries(3):
            self.client.get('/list/authors/notempty/paginated/')

    def test_explicitly_ordered_list_view(self):
        Book.objects.create(name="Zebras for Dummies", pages=800, pubdate=datetime.date(2006, 9, 1))
        res = self.client.get('/list/books/sorted/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object_list'][0].name, '2066')
        self.assertEqual(res.context['object_list'][1].name, 'Dreaming in Code')
        self.assertEqual(res.context['object_list'][2].name, 'Zebras for Dummies')

        res = self.client.get('/list/books/sortedbypagesandnamedec/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object_list'][0].name, 'Dreaming in Code')
        self.assertEqual(res.context['object_list'][1].name, 'Zebras for Dummies')
        self.assertEqual(res.context['object_list'][2].name, '2066')

    @override_settings(DEBUG=True)
    def test_paginated_list_view_returns_useful_message_on_invalid_page(self):
        """
        Tests for paginated list view with invalid page.
        
        This function tests that when a paginated list view receives an invalid page number, it returns a 404 status code and includes a specific error message in the context.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - HTTP response with status code 404 and context containing 'reason' key with the message "Invalid page (2): That page contains no results".
        """

        # test for #19240
        # tests that source exception's message is included in page
        self._make_authors(1)
        res = self.client.get('/list/authors/paginated/2/')
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.context.get('reason'), "Invalid page (2): That page contains no results")

    def _make_authors(self, n):
        Author.objects.all().delete()
        for i in range(n):
            Author.objects.create(name='Author %02i' % i, slug='a%s' % i)
ects.create(name='Author %02i' % i, slug='a%s' % i)
