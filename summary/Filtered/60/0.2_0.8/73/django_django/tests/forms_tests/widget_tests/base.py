from django.forms.renderers import DjangoTemplates, Jinja2
from django.test import SimpleTestCase

try:
    import jinja2
except ImportError:
    jinja2 = None


class WidgetTest(SimpleTestCase):
    beatles = (('J', 'John'), ('P', 'Paul'), ('G', 'George'), ('R', 'Ringo'))

    @classmethod
    def setUpClass(cls):
        """
        Sets up class-level renderers for testing.
        
        This method initializes class-level renderers for DjangoTemplates and optionally Jinja2, and stores them in a list. The renderers are used for rendering templates during test cases.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - `cls.django_renderer`: An instance of DjangoTemplates used for rendering Django templates.
        - `cls.jinja2_renderer`: An instance of Jinja2 used for rendering Jinja2 templates, if
        """

        cls.django_renderer = DjangoTemplates()
        cls.jinja2_renderer = Jinja2() if jinja2 else None
        cls.renderers = [cls.django_renderer] + ([cls.jinja2_renderer] if cls.jinja2_renderer else [])
        super().setUpClass()

    def check_html(self, widget, name, value, html='', attrs=None, strict=False, **kwargs):
        """
        Check the HTML output of a widget.
        
        This function compares the HTML output of a widget with an expected HTML string. It supports two rendering methods: Django's renderer and Jinja2's renderer. The comparison is done using `assertEqual` for the Django renderer and `assertHTMLEqual` for the Jinja2 renderer. If `strict` is set to `False`, `assertHTMLEqual` is used for both renderers.
        
        Parameters:
        widget (Widget): The widget to render
        """

        assertEqual = self.assertEqual if strict else self.assertHTMLEqual
        if self.jinja2_renderer:
            output = widget.render(name, value, attrs=attrs, renderer=self.jinja2_renderer, **kwargs)
            # Django escapes quotes with '&quot;' while Jinja2 uses '&#34;'.
            output = output.replace('&#34;', '&quot;')
            # Django escapes single quotes with '&#x27;' while Jinja2 uses '&#39;'.
            output = output.replace('&#39;', '&#x27;')
            assertEqual(output, html)

        output = widget.render(name, value, attrs=attrs, renderer=self.django_renderer, **kwargs)
        assertEqual(output, html)
