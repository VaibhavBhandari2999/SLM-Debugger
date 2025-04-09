"""
This Python file contains unit tests for a Django application that involves form handling and testing of an autocomplete widget in the Django admin interface. The file defines several form classes (`AlbumForm`, `NotRequiredBandForm`, `RequiredBandForm`, and `VideoStreamForm`) and a test class (`AutocompleteMixinTests`). The form classes are used to create instances of Django forms for different models (`Album` and `VideoStream`), and the test class contains methods to verify the functionality of these forms, particularly focusing on the autocomplete widget's behavior. The tests cover scenarios such as building widget attributes, rendering form options, and checking media files for the autocomplete widget in different languages. The file also includes a custom form field widget (`AlbumForm.Meta.widgets`)
"""
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.forms import ModelChoiceField
from django.test import TestCase, override_settings
from django.utils import translation

from .models import Album, Band, ReleaseEvent, VideoStream


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['band', 'featuring']
        widgets = {
            'band': AutocompleteSelect(
                Album._meta.get_field('band'),
                admin.site,
                attrs={'class': 'my-class'},
            ),
            'featuring': AutocompleteSelect(
                Album._meta.get_field('featuring'),
                admin.site,
            )
        }


class NotRequiredBandForm(forms.Form):
    band = ModelChoiceField(
        queryset=Album.objects.all(),
        widget=AutocompleteSelect(Album._meta.get_field('band').remote_field, admin.site),
        required=False,
    )


class RequiredBandForm(forms.Form):
    band = ModelChoiceField(
        queryset=Album.objects.all(),
        widget=AutocompleteSelect(Album._meta.get_field('band').remote_field, admin.site),
        required=True,
    )


class VideoStreamForm(forms.ModelForm):
    class Meta:
        model = VideoStream
        fields = ['release_event']
        widgets = {
            'release_event': AutocompleteSelect(
                VideoStream._meta.get_field('release_event'),
                admin.site,
            ),
        }


@override_settings(ROOT_URLCONF='admin_widgets.urls')
class AutocompleteMixinTests(TestCase):
    empty_option = '<option value=""></option>'
    maxDiff = 1000

    def test_build_attrs(self):
        """
        Tests the construction of widget attributes for the 'band' field in an AlbumForm.
        
        This function creates an instance of AlbumForm and retrieves the widget attributes for the 'band' field using the `get_context` method. It then asserts that these attributes match the expected dictionary containing various class names, data attributes, and placeholder values.
        """

        form = AlbumForm()
        attrs = form['band'].field.widget.get_context(name='my_field', value=None, attrs={})['widget']['attrs']
        self.assertEqual(attrs, {
            'class': 'my-class admin-autocomplete',
            'data-ajax--cache': 'true',
            'data-ajax--delay': 250,
            'data-ajax--type': 'GET',
            'data-ajax--url': '/autocomplete/',
            'data-theme': 'admin-autocomplete',
            'data-allow-clear': 'false',
            'data-app-label': 'admin_widgets',
            'data-field-name': 'band',
            'data-model-name': 'album',
            'data-placeholder': ''
        })

    def test_build_attrs_no_custom_class(self):
        """
        Tests the behavior of the 'featuring' field widget's get_context method without a custom class.
        The function creates an instance of the AlbumForm, retrieves the 'featuring' field widget's context attributes,
        and asserts that the 'class' attribute is set to 'admin-autocomplete'.
        """

        form = AlbumForm()
        attrs = form['featuring'].field.widget.get_context(name='name', value=None, attrs={})['widget']['attrs']
        self.assertEqual(attrs['class'], 'admin-autocomplete')

    def test_build_attrs_not_required_field(self):
        """
        Tests the build_attrs method of the 'band' field's widget when the 'required' attribute is not set. The method generates HTML attributes for the widget, including a JSON representation of whether the field allows clearing its value. The expected result is that the 'data-allow-clear' attribute is set to True.
        """

        form = NotRequiredBandForm()
        attrs = form['band'].field.widget.build_attrs({})
        self.assertJSONEqual(attrs['data-allow-clear'], True)

    def test_build_attrs_required_field(self):
        """
        Builds and returns the attributes for the 'band' field widget in a RequiredBandForm, ensuring that the 'data-allow-clear' attribute is set to False. The function takes no input arguments and returns a dictionary of widget attributes.
        """

        form = RequiredBandForm()
        attrs = form['band'].field.widget.build_attrs({})
        self.assertJSONEqual(attrs['data-allow-clear'], False)

    def test_get_url(self):
        """
        Tests the get_url method of the AutocompleteSelect widget for the 'band' field in the Album model's Meta class. The method returns the URL '/autocomplete/'.
        
        Args:
        None
        
        Returns:
        None
        
        Methods Used:
        - `_meta.get_field`: Retrieves the 'band' field from the Album model's Meta class.
        - `AutocompleteSelect`: Instantiates the AutocompleteSelect widget with the retrieved field and the admin site.
        - `get_url`:
        """

        rel = Album._meta.get_field('band')
        w = AutocompleteSelect(rel, admin.site)
        url = w.get_url()
        self.assertEqual(url, '/autocomplete/')

    def test_render_options(self):
        """
        Tests the rendering of options in an AlbumForm.
        
        This function tests how the `AlbumForm` renders options for a ForeignKey field ('band') and a ManyToManyField ('featuring'). It creates instances of `Band` objects and uses them to initialize the form with specific values. The function then checks if the rendered HTML contains the expected selected options for each field.
        """

        beatles = Band.objects.create(name='The Beatles', style='rock')
        who = Band.objects.create(name='The Who', style='rock')
        # With 'band', a ForeignKey.
        form = AlbumForm(initial={'band': beatles.uuid})
        output = form.as_table()
        selected_option = '<option value="%s" selected>The Beatles</option>' % beatles.uuid
        option = '<option value="%s">The Who</option>' % who.uuid
        self.assertIn(selected_option, output)
        self.assertNotIn(option, output)
        # With 'featuring', a ManyToManyField.
        form = AlbumForm(initial={'featuring': [beatles.pk, who.pk]})
        output = form.as_table()
        selected_option = '<option value="%s" selected>The Beatles</option>' % beatles.pk
        option = '<option value="%s" selected>The Who</option>' % who.pk
        self.assertIn(selected_option, output)
        self.assertIn(option, output)

    def test_render_options_required_field(self):
        """Empty option is present if the field isn't required."""
        form = NotRequiredBandForm()
        output = form.as_table()
        self.assertIn(self.empty_option, output)

    def test_render_options_not_required_field(self):
        """Empty option isn't present if the field isn't required."""
        form = RequiredBandForm()
        output = form.as_table()
        self.assertNotIn(self.empty_option, output)

    def test_render_options_fk_as_pk(self):
        """
        Tests rendering of options for a ForeignKey field in a form.
        
        This function creates instances of `Band`, `Album`, and `ReleaseEvent` models,
        initializes a `VideoStreamForm` with the primary key of the `ReleaseEvent`,
        and checks if the rendered form output contains the selected option for the
        `ReleaseEvent`.
        
        - Models involved: `Band`, `Album`, `ReleaseEvent`
        - Form used: `VideoStreamForm`
        - Input: Primary key
        """

        beatles = Band.objects.create(name='The Beatles', style='rock')
        rubber_soul = Album.objects.create(name='Rubber Soul', band=beatles)
        release_event = ReleaseEvent.objects.create(name='Test Target', album=rubber_soul)
        form = VideoStreamForm(initial={'release_event': release_event.pk})
        output = form.as_table()
        selected_option = '<option value="%s" selected>Test Target</option>' % release_event.pk
        self.assertIn(selected_option, output)

    def test_media(self):
        """
        Tests the media files for the AutocompleteSelect widget in the Django admin interface. This function iterates over a list of language codes, overrides the current language using Django's translation module, and checks if the media files for the AutocompleteSelect widget include the appropriate language-specific JavaScript files based on the language code. The function uses the `Album` model's `band` field relationship, the `AutocompleteSelect` widget, and the `media` attribute to generate and compare the expected and actual media
        """

        rel = Album._meta.get_field('band').remote_field
        base_files = (
            'admin/js/vendor/jquery/jquery.min.js',
            'admin/js/vendor/select2/select2.full.min.js',
            # Language file is inserted here.
            'admin/js/jquery.init.js',
            'admin/js/autocomplete.js',
        )
        languages = (
            ('de', 'de'),
            # Language with code 00 does not exist.
            ('00', None),
            # Language files are case sensitive.
            ('sr-cyrl', 'sr-Cyrl'),
            ('zh-hans', 'zh-CN'),
            ('zh-hant', 'zh-TW'),
        )
        for lang, select_lang in languages:
            with self.subTest(lang=lang):
                if select_lang:
                    expected_files = (
                        base_files[:2] +
                        (('admin/js/vendor/select2/i18n/%s.js' % select_lang),) +
                        base_files[2:]
                    )
                else:
                    expected_files = base_files
                with translation.override(lang):
                    self.assertEqual(AutocompleteSelect(rel, admin.site).media._js, list(expected_files))
