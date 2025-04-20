import datetime

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin

from .models import Artist, Author, Book, Page


@override_settings(ROOT_URLCONF='generic_views.urls')
class DetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the tests in the class.
        
        This method creates and initializes several test objects for use in the tests. It creates instances of the Artist, Author, Book, and Page models and adds relationships between them.
        
        Parameters:
        cls (cls): The class object that the method is being called on.
        
        Returns:
        None: This method does not return any value. It populates the class with test data.
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

    def test_simple_object(self):
        res = self.client.get('/detail/obj/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], {'foo': 'bar'})
        self.assertIsInstance(res.context['view'], View)
        self.assertTemplateUsed(res, 'generic_views/detail.html')

    def test_detail_by_pk(self):
        """
        Tests the detail view for an author by primary key.
        
        This function sends a GET request to the '/detail/author/<pk>/' URL with the primary key of a specific author and checks if the response status code is 200, if the context contains the correct author object, and if the correct template is used.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The function uses the client from Django's test framework to simulate a GET request.
        - The primary key
        """

        res = self.client.get('/detail/author/%s/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_missing_object(self):
        res = self.client.get('/detail/author/500/')
        self.assertEqual(res.status_code, 404)

    def test_detail_object_does_not_exist(self):
        with self.assertRaises(ObjectDoesNotExist):
            self.client.get('/detail/doesnotexist/1/')

    def test_detail_by_custom_pk(self):
        res = self.client.get('/detail/author/bycustompk/%s/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_slug(self):
        res = self.client.get('/detail/author/byslug/scott-rosenberg/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Author.objects.get(slug='scott-rosenberg'))
        self.assertEqual(res.context['author'], Author.objects.get(slug='scott-rosenberg'))
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_custom_slug(self):
        """
        Tests the 'test_detail_by_custom_slug' function.
        
        This function tests the detail view for an author with a custom slug. It sends a GET request to the '/detail/author/bycustomslug/scott-rosenberg/' endpoint and checks the response status code, context data, and template used.
        
        Key Parameters:
        - None
        
        Keywords:
        - No specific keywords
        
        Input:
        - No input parameters
        
        Output:
        - The function does not return any value. It asserts the correctness of the response.
        
        Assertions
        """

        res = self.client.get('/detail/author/bycustomslug/scott-rosenberg/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Author.objects.get(slug='scott-rosenberg'))
        self.assertEqual(res.context['author'], Author.objects.get(slug='scott-rosenberg'))
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_pk_ignore_slug(self):
        res = self.client.get('/detail/author/bypkignoreslug/%s-roberto-bolano/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_pk_ignore_slug_mismatch(self):
        """
        Tests the behavior of the author detail view when the URL slug does not match the object's slug.
        
        This function sends a GET request to the author detail view using a URL that does not match the object's slug and checks if the response status code is 200, if the correct author object is retrieved, and if the correct template is used.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The function uses the client to make a GET request to '/detail/author
        """

        res = self.client.get('/detail/author/bypkignoreslug/%s-scott-rosenberg/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_pk_and_slug(self):
        """
        Tests the detail view for an author with a primary key and slug.
        
        This function sends a GET request to the '/detail/author/bypkandslug/' URL with a specific author's primary key and slug. It then checks the response to ensure that the correct author object is returned, the status code is 200 (OK), and the correct template is used.
        
        Parameters:
        - None (the function uses pre-defined objects from the test setup)
        
        Returns:
        - None (the function asserts
        """

        res = self.client.get('/detail/author/bypkandslug/%s-roberto-bolano/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_pk_and_slug_mismatch_404(self):
        res = self.client.get('/detail/author/bypkandslug/%s-scott-rosenberg/' % self.author1.pk)
        self.assertEqual(res.status_code, 404)

    def test_verbose_name(self):
        res = self.client.get('/detail/artist/%s/' % self.artist1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.artist1)
        self.assertEqual(res.context['artist'], self.artist1)
        self.assertTemplateUsed(res, 'generic_views/artist_detail.html')

    def test_template_name(self):
        res = self.client.get('/detail/author/%s/template_name/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/about.html')

    def test_template_name_suffix(self):
        """
        Tests the template name suffix functionality for a view that retrieves an author's details.
        
        This function sends a GET request to the '/detail/author/<pk>/template_name_suffix/' URL, where <pk> is the primary key of an author. It then checks the response status code, the context data, and the template used.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function uses a client to simulate a GET request.
        - The primary key of the author
        """

        res = self.client.get('/detail/author/%s/template_name_suffix/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_view.html')

    def test_template_name_field(self):
        res = self.client.get('/detail/page/%s/field/' % self.page1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.page1)
        self.assertEqual(res.context['page'], self.page1)
        self.assertTemplateUsed(res, 'generic_views/page_template.html')

    def test_context_object_name(self):
        """
        Tests the context object name functionality in a Django view.
        
        This function sends a GET request to the '/detail/author/<pk>/context_object_name/' URL, where <pk> is the primary key of a specific author. It then checks the response status code, the context objects 'object' and 'thingy', and ensures that the 'author' context object is not present. Finally, it verifies that the correct template is used for rendering the response.
        
        Parameters:
        - self: The Django test
        """

        res = self.client.get('/detail/author/%s/context_object_name/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['thingy'], self.author1)
        self.assertNotIn('author', res.context)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_duplicated_context_object_name(self):
        res = self.client.get('/detail/author/%s/dupe_context_object_name/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertNotIn('author', res.context)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_custom_detail(self):
        """
        AuthorCustomDetail overrides get() and ensures that
        SingleObjectMixin.get_context_object_name() always uses the obj
        parameter instead of self.object.
        """
        res = self.client.get('/detail/author/%s/custom_detail/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['custom_author'], self.author1)
        self.assertNotIn('author', res.context)
        self.assertNotIn('object', res.context)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_deferred_queryset_template_name(self):
        class FormContext(SingleObjectTemplateResponseMixin):
            request = RequestFactory().get('/')
            model = Author
            object = Author.objects.defer('name').get(pk=self.author1.pk)

        self.assertEqual(FormContext().get_template_names()[0], 'generic_views/author_detail.html')

    def test_deferred_queryset_context_object_name(self):
        class FormContext(ModelFormMixin):
            request = RequestFactory().get('/')
            model = Author
            object = Author.objects.defer('name').get(pk=self.author1.pk)
            fields = ('name',)

        form_context_data = FormContext().get_context_data()
        self.assertEqual(form_context_data['object'], self.author1)
        self.assertEqual(form_context_data['author'], self.author1)

    def test_invalid_url(self):
        with self.assertRaises(AttributeError):
            self.client.get('/detail/author/invalid/url/')

    def test_invalid_queryset(self):
        """
        Tests the behavior of the AuthorDetail view when an invalid queryset is provided.
        
        This function checks if the AuthorDetail view raises an ImproperlyConfigured exception when it is missing a QuerySet. The view should define either AuthorDetail.model, AuthorDetail.queryset, or override AuthorDetail.get_queryset() to provide a valid queryset.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ImproperlyConfigured: If AuthorDetail is missing a QuerySet.
        
        Usage:
        This test function
        """

        msg = (
            'AuthorDetail is missing a QuerySet. Define AuthorDetail.model, '
            'AuthorDetail.queryset, or override AuthorDetail.get_queryset().'
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            self.client.get('/detail/author/invalid/qs/')

    def test_non_model_object_with_meta(self):
        res = self.client.get('/detail/nonmodel/1/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'].id, "non_model_1")
del_1")
