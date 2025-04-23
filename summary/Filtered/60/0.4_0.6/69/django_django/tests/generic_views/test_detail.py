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
        """
        Tests the behavior of the `test_simple_object` method.
        
        This method sends a GET request to the '/detail/obj/' endpoint and checks the response status code, the content of the 'object' context variable, the type of the 'view' context variable, and the template used for rendering the response.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The response status code is 200.
        - The 'object' context variable contains a dictionary with the key 'foo
        """

        res = self.client.get('/detail/obj/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], {'foo': 'bar'})
        self.assertIsInstance(res.context['view'], View)
        self.assertTemplateUsed(res, 'generic_views/detail.html')

    def test_detail_by_pk(self):
        """
        Tests the detail view for an author by primary key.
        
        This function sends a GET request to the '/detail/author/<pk>/' URL with the primary key of an author and checks the response status code, the context data, and the used template.
        
        Parameters:
        - None (uses instance variables: self.author1, self.client)
        
        Returns:
        - None (performs assertions on the response)
        
        Key Assertions:
        - The response status code should be 200 (OK).
        - The context data
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
        """
        Tests the detail view for an author by slug.
        
        This function sends a GET request to the '/detail/author/byslug/scott-rosenberg/' endpoint and checks the response status code, context data, and template used.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The function uses the Django test client to make the request.
        - It asserts that the response status code is 200, indicating a successful request.
        - It checks that the context variables 'object
        """

        res = self.client.get('/detail/author/byslug/scott-rosenberg/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Author.objects.get(slug='scott-rosenberg'))
        self.assertEqual(res.context['author'], Author.objects.get(slug='scott-rosenberg'))
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_custom_slug(self):
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
        Tests the detail view for an author by primary key, ignoring slug mismatches.
        
        This function sends a GET request to the detail view for an author using a URL that includes the author's primary key but a mismatched slug. It verifies that the response status code is 200 (OK), the correct author object is retrieved, and the appropriate template is used.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The response status code is 200.
        - The context
        """

        res = self.client.get('/detail/author/bypkignoreslug/%s-scott-rosenberg/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_pk_and_slug(self):
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
        Tests the template name suffix functionality for a view that displays an author's details.
        
        This function sends a GET request to the '/detail/author/<author_id>/template_name_suffix/' URL, where <author_id> is the primary key of an author object. It then checks the response to ensure that:
        - The status code of the response is 200 (OK).
        - The context contains an 'object' and 'author' key, both of which refer to the author object.
        -
        """

        res = self.client.get('/detail/author/%s/template_name_suffix/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_view.html')

    def test_template_name_field(self):
        """
        Tests the template name field functionality for a page detail view.
        
        This function sends a GET request to the '/detail/page/<page_id>/field/' URL, where <page_id> is the primary key of a specific page object. It checks that the response status code is 200, indicating a successful request. The function then verifies that the context contains the correct page object and that the correct template is used.
        
        Parameters:
        - self: The current test case instance.
        
        Returns:
        - None:
        """

        res = self.client.get('/detail/page/%s/field/' % self.page1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.page1)
        self.assertEqual(res.context['page'], self.page1)
        self.assertTemplateUsed(res, 'generic_views/page_template.html')

    def test_context_object_name(self):
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
        """
        Tests the deferred queryset context object name functionality in a ModelFormMixin.
        
        This function creates an instance of FormContext, which is a subclass of ModelFormMixin. It sets up a request, model, and object with deferred fields. The function then calls get_context_data to retrieve the context data and checks that the 'object' and 'author' keys in the context data point to the correct Author instance.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Inputs:
        - None
        
        Outputs:
        -
        """

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
        This function is
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
