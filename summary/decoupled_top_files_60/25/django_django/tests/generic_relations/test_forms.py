from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import TestCase
from django.test.utils import isolate_apps

from .models import (
    Animal, ForProxyModelModel, Gecko, Mineral, ProxyRelatedModel, TaggedItem,
)


class CustomWidget(forms.TextInput):
    pass


class TaggedItemForm(forms.ModelForm):
    class Meta:
        model = TaggedItem
        fields = '__all__'
        widgets = {'tag': CustomWidget}


class GenericInlineFormsetTests(TestCase):

    def test_output(self):
        """
        Tests the output of the generic inline formset for TaggedItem model.
        
        This function tests the output of the generic inline formset for the TaggedItem model. It creates a formset without an instance, with an instance, and with an instance that already has a TaggedItem associated with it. It also tests formset with a custom prefix.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Points:
        - Tests formset output without an instance.
        - Tests formset output with an
        """

        GenericFormSet = generic_inlineformset_factory(TaggedItem, extra=1)
        formset = GenericFormSet()
        self.assertHTMLEqual(
            ''.join(form.as_p() for form in formset.forms),
            """<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-tag">
Tag:</label> <input id="id_generic_relations-taggeditem-content_type-object_id-0-tag" type="text"
name="generic_relations-taggeditem-content_type-object_id-0-tag" maxlength="50"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">Delete:</label>
<input type="checkbox" name="generic_relations-taggeditem-content_type-object_id-0-DELETE"
id="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">
<input type="hidden" name="generic_relations-taggeditem-content_type-object_id-0-id"
id="id_generic_relations-taggeditem-content_type-object_id-0-id"></p>"""
        )
        formset = GenericFormSet(instance=Animal())
        self.assertHTMLEqual(
            ''.join(form.as_p() for form in formset.forms),
            """<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-tag">
Tag:</label> <input id="id_generic_relations-taggeditem-content_type-object_id-0-tag"
type="text" name="generic_relations-taggeditem-content_type-object_id-0-tag" maxlength="50"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">Delete:</label>
<input type="checkbox" name="generic_relations-taggeditem-content_type-object_id-0-DELETE"
id="id_generic_relations-taggeditem-content_type-object_id-0-DELETE"><input type="hidden"
name="generic_relations-taggeditem-content_type-object_id-0-id"
id="id_generic_relations-taggeditem-content_type-object_id-0-id"></p>"""
        )
        platypus = Animal.objects.create(
            common_name='Platypus', latin_name='Ornithorhynchus anatinus',
        )
        platypus.tags.create(tag='shiny')
        GenericFormSet = generic_inlineformset_factory(TaggedItem, extra=1)
        formset = GenericFormSet(instance=platypus)
        tagged_item_id = TaggedItem.objects.get(tag='shiny', object_id=platypus.id).id
        self.assertHTMLEqual(
            ''.join(form.as_p() for form in formset.forms),
            """<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-tag">Tag:</label>
<input id="id_generic_relations-taggeditem-content_type-object_id-0-tag" type="text"
name="generic_relations-taggeditem-content_type-object_id-0-tag" value="shiny" maxlength="50"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">Delete:</label>
<input type="checkbox" name="generic_relations-taggeditem-content_type-object_id-0-DELETE"
id="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">
<input type="hidden" name="generic_relations-taggeditem-content_type-object_id-0-id"
value="%s" id="id_generic_relations-taggeditem-content_type-object_id-0-id"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-1-tag">Tag:</label>
<input id="id_generic_relations-taggeditem-content_type-object_id-1-tag" type="text"
name="generic_relations-taggeditem-content_type-object_id-1-tag" maxlength="50"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-1-DELETE">Delete:</label>
<input type="checkbox" name="generic_relations-taggeditem-content_type-object_id-1-DELETE"
id="id_generic_relations-taggeditem-content_type-object_id-1-DELETE">
<input type="hidden" name="generic_relations-taggeditem-content_type-object_id-1-id"
id="id_generic_relations-taggeditem-content_type-object_id-1-id"></p>""" % tagged_item_id
        )
        lion = Animal.objects.create(common_name='Lion', latin_name='Panthera leo')
        formset = GenericFormSet(instance=lion, prefix='x')
        self.assertHTMLEqual(
            ''.join(form.as_p() for form in formset.forms),
            """<p><label for="id_x-0-tag">Tag:</label>
<input id="id_x-0-tag" type="text" name="x-0-tag" maxlength="50"></p>
<p><label for="id_x-0-DELETE">Delete:</label> <input type="checkbox" name="x-0-DELETE" id="id_x-0-DELETE">
<input type="hidden" name="x-0-id" id="id_x-0-id"></p>"""
        )

    def test_options(self):
        """
        Tests the behavior of the TaggedItemFormSet with different querysets and configurations.
        
        This function tests the TaggedItemFormSet, which is a generic inline formset for the TaggedItem model. It checks how the formset behaves with and without a queryset, and how the queryset affects the display ordering and omission of items.
        
        Key Parameters:
        - instance: The instance of the model (Animal) to which the TaggedItems are related.
        
        Key Keywords:
        - queryset: An optional queryset to
        """

        TaggedItemFormSet = generic_inlineformset_factory(
            TaggedItem,
            can_delete=False,
            exclude=['tag'],
            extra=3,
        )
        platypus = Animal.objects.create(common_name='Platypus', latin_name='Ornithorhynchus anatinus')
        harmless = platypus.tags.create(tag='harmless')
        mammal = platypus.tags.create(tag='mammal')
        # Works without a queryset.
        formset = TaggedItemFormSet(instance=platypus)
        self.assertEqual(len(formset.forms), 5)
        self.assertHTMLEqual(
            formset.forms[0].as_p(),
            '<input type="hidden" name="generic_relations-taggeditem-content_type-object_id-0-id" value="%s" '
            'id="id_generic_relations-taggeditem-content_type-object_id-0-id">' % harmless.pk
        )
        self.assertEqual(formset.forms[0].instance, harmless)
        self.assertEqual(formset.forms[1].instance, mammal)
        self.assertIsNone(formset.forms[2].instance.pk)
        # A queryset can be used to alter display ordering.
        formset = TaggedItemFormSet(instance=platypus, queryset=TaggedItem.objects.order_by('-tag'))
        self.assertEqual(len(formset.forms), 5)
        self.assertEqual(formset.forms[0].instance, mammal)
        self.assertEqual(formset.forms[1].instance, harmless)
        self.assertIsNone(formset.forms[2].instance.pk)
        # A queryset that omits items.
        formset = TaggedItemFormSet(instance=platypus, queryset=TaggedItem.objects.filter(tag__startswith='harm'))
        self.assertEqual(len(formset.forms), 4)
        self.assertEqual(formset.forms[0].instance, harmless)
        self.assertIsNone(formset.forms[1].instance.pk)

    def test_get_queryset_ordering(self):
        """
        BaseGenericInlineFormSet.get_queryset() adds default ordering, if
        needed.
        """
        inline_formset = generic_inlineformset_factory(TaggedItem, exclude=('tag',))
        formset = inline_formset(instance=Gecko.objects.create())
        self.assertIs(formset.get_queryset().ordered, True)

    def test_initial(self):
        quartz = Mineral.objects.create(name='Quartz', hardness=7)
        GenericFormSet = generic_inlineformset_factory(TaggedItem, extra=1)
        ctype = ContentType.objects.get_for_model(quartz)
        initial_data = [{
            'tag': 'lizard',
            'content_type': ctype.pk,
            'object_id': quartz.pk,
        }]
        formset = GenericFormSet(initial=initial_data)
        self.assertEqual(formset.forms[0].initial, initial_data[0])

    def test_meta_widgets(self):
        """TaggedItemForm has a widget defined in Meta."""
        Formset = generic_inlineformset_factory(TaggedItem, TaggedItemForm)
        form = Formset().forms[0]
        self.assertIsInstance(form['tag'].field.widget, CustomWidget)

    @isolate_apps('generic_relations')
    def test_incorrect_content_type(self):
        class BadModel(models.Model):
            content_type = models.PositiveIntegerField()

        msg = "fk_name 'generic_relations.BadModel.content_type' is not a ForeignKey to ContentType"
        with self.assertRaisesMessage(Exception, msg):
            generic_inlineformset_factory(BadModel, TaggedItemForm)

    def test_save_new_uses_form_save(self):
        """
        Tests the behavior of a formset when saving a new instance with a custom save method.
        
        This function creates a formset using a custom form that overrides the save method to set a specific attribute on the saved instance. It then validates the formset with some data and checks if the custom save method was called correctly.
        
        Key Parameters:
        - `self`: The test case instance.
        
        Key Keywords:
        - `formset`: The formset instance created for testing.
        - `instance`: The instance of the model
        """

        class SaveTestForm(forms.ModelForm):
            def save(self, *args, **kwargs):
                self.instance.saved_by = 'custom method'
                return super().save(*args, **kwargs)

        Formset = generic_inlineformset_factory(ForProxyModelModel, fields='__all__', form=SaveTestForm)
        instance = ProxyRelatedModel.objects.create()
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
            'form-0-title': 'foo',
        }
        formset = Formset(data, instance=instance, prefix='form')
        self.assertTrue(formset.is_valid())
        new_obj = formset.save()[0]
        self.assertEqual(new_obj.saved_by, 'custom method')

    def test_save_new_for_proxy(self):
        Formset = generic_inlineformset_factory(ForProxyModelModel, fields='__all__', for_concrete_model=False)
        instance = ProxyRelatedModel.objects.create()
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
            'form-0-title': 'foo',
        }
        formset = Formset(data, instance=instance, prefix='form')
        self.assertTrue(formset.is_valid())
        new_obj, = formset.save()
        self.assertEqual(new_obj.obj, instance)

    def test_save_new_for_concrete(self):
        """
        Test saving a new instance using a generic inline formset for a concrete model.
        
        This function tests the creation of a new instance of `ForProxyModelModel` using a formset that is associated with a concrete model. The formset is instantiated with a given data dictionary and an instance of `ProxyRelatedModel`. The formset is expected to be valid, and after saving, the new object should not be an instance of `ProxyRelatedModel`.
        
        Parameters:
        - data (dict): A dictionary containing
        """

        Formset = generic_inlineformset_factory(ForProxyModelModel, fields='__all__', for_concrete_model=True)
        instance = ProxyRelatedModel.objects.create()
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
            'form-0-title': 'foo',
        }
        formset = Formset(data, instance=instance, prefix='form')
        self.assertTrue(formset.is_valid())
        new_obj, = formset.save()
        self.assertNotIsInstance(new_obj.obj, ProxyRelatedModel)

    def test_initial_count(self):
        GenericFormSet = generic_inlineformset_factory(TaggedItem)
        data = {
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '3',
            'form-MAX_NUM_FORMS': '',
        }
        formset = GenericFormSet(data=data, prefix='form')
        self.assertEqual(formset.initial_form_count(), 3)
        formset = GenericFormSet(data=data, prefix='form', save_as_new=True)
        self.assertEqual(formset.initial_form_count(), 0)

    def test_save_as_new(self):
        """
        The save_as_new parameter creates new items that are associated with
        the object.
        """
        lion = Animal.objects.create(common_name='Lion', latin_name='Panthera leo')
        yellow = lion.tags.create(tag='yellow')
        hairy = lion.tags.create(tag='hairy')
        GenericFormSet = generic_inlineformset_factory(TaggedItem)
        data = {
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '2',
            'form-MAX_NUM_FORMS': '',
            'form-0-id': str(yellow.pk),
            'form-0-tag': 'hunts',
            'form-1-id': str(hairy.pk),
            'form-1-tag': 'roars',
        }
        formset = GenericFormSet(data, instance=lion, prefix='form', save_as_new=True)
        self.assertTrue(formset.is_valid())
        tags = formset.save()
        self.assertEqual([tag.tag for tag in tags], ['hunts', 'roars'])
        hunts, roars = tags
        self.assertSequenceEqual(lion.tags.order_by('tag'), [hairy, hunts, roars, yellow])
