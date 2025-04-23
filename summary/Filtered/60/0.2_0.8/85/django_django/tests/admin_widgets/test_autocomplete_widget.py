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
        Tests the build_attrs method of the AlbumForm's band field widget.
        
        This function creates an instance of the AlbumForm and retrieves the widget's attributes for the 'band' field. The attributes are then compared to a set of expected values to ensure they match.
        
        Parameters:
        None
        
        Returns:
        None
        
        Expected Output:
        The function asserts that the widget's attributes match the expected dictionary. If the attributes do not match, an AssertionError is raised.
        
        Key Attributes:
        - 'class': '
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
            'data-placeholder': '',
            'lang': 'en',
        })

    def test_build_attrs_no_custom_class(self):
        form = AlbumForm()
        attrs = form['featuring'].field.widget.get_context(name='name', value=None, attrs={})['widget']['attrs']
        self.assertEqual(attrs['class'], 'admin-autocomplete')

    def test_build_attrs_not_required_field(self):
        """
        Tests the build_attrs method for a form field with an optional band. The method should return a dictionary with a JSON-serialized 'data-allow-clear' attribute set to True.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - The test checks if the 'data-allow-clear' attribute is correctly set to True when the 'band' field is optional in the form.
        - The method 'build_attrs' is called with an empty dictionary as an argument.
        - The assertion uses
        """

        form = NotRequiredBandForm()
        attrs = form['band'].field.widget.build_attrs({})
        self.assertJSONEqual(attrs['data-allow-clear'], True)

    def test_build_attrs_required_field(self):
        form = RequiredBandForm()
        attrs = form['band'].field.widget.build_attrs({})
        self.assertJSONEqual(attrs['data-allow-clear'], False)

    def test_get_url(self):
        rel = Album._meta.get_field('band')
        w = AutocompleteSelect(rel, admin.site)
        url = w.get_url()
        self.assertEqual(url, '/autocomplete/')

    def test_render_options(self):
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
        beatles = Band.objects.create(name='The Beatles', style='rock')
        rubber_soul = Album.objects.create(name='Rubber Soul', band=beatles)
        release_event = ReleaseEvent.objects.create(name='Test Target', album=rubber_soul)
        form = VideoStreamForm(initial={'release_event': release_event.pk})
        output = form.as_table()
        selected_option = '<option value="%s" selected>Test Target</option>' % release_event.pk
        self.assertIn(selected_option, output)

    def test_media(self):
        """
        Tests the media files for the AutocompleteSelect widget in the Django admin interface.
        
        This function verifies that the correct media files are loaded for the AutocompleteSelect widget based on the language settings. It iterates over a list of languages, overriding the current language for each iteration. Depending on the language, it constructs a list of expected media files, which includes base files and language-specific files if available. The function then compares the actual media files generated by the widget with the expected ones.
        
        Parameters:
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
