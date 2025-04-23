from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import ModelForm, modelformset_factory
from django.forms.models import BaseModelFormSet


class BaseGenericInlineFormSet(BaseModelFormSet):
    """
    A formset for generic inline objects to a parent.
    """

    def __init__(
        """
        Initializes a new instance of the model's related manager.
        
        Args:
        data (Optional[Dict[str, Any]]): Data to be used for form initialization.
        files (Optional[Dict[str, Any]]): Files to be used for form initialization.
        instance (Optional[Model]): The instance of the model to which the related objects belong.
        save_as_new (bool): Whether to save the related objects as new instances.
        prefix (Optional[str]): A prefix to use for the
        """

        self,
        data=None,
        files=None,
        instance=None,
        save_as_new=False,
        prefix=None,
        queryset=None,
        **kwargs,
    ):
        opts = self.model._meta
        self.instance = instance
        self.rel_name = (
            opts.app_label
            + "-"
            + opts.model_name
            + "-"
            + self.ct_field.name
            + "-"
            + self.ct_fk_field.name
        )
        self.save_as_new = save_as_new
        if self.instance is None or self.instance.pk is None:
            qs = self.model._default_manager.none()
        else:
            if queryset is None:
                queryset = self.model._default_manager
            qs = queryset.filter(
                **{
                    self.ct_field.name: ContentType.objects.get_for_model(
                        self.instance, for_concrete_model=self.for_concrete_model
                    ),
                    self.ct_fk_field.name: self.instance.pk,
                }
            )
        super().__init__(queryset=qs, data=data, files=files, prefix=prefix, **kwargs)

    def initial_form_count(self):
        """
        Counts the initial form count for the formset.
        
        Parameters:
        self (object): The instance of the class calling the method.
        
        Returns:
        int: The initial form count. Returns 0 if the instance's `save_as_new` attribute is True, otherwise returns the result of calling `super().initial_form_count()`.
        
        Notes:
        This method is used to determine the initial number of forms in a formset. If the `save_as_new` attribute is set to True, it indicates
        """

        if self.save_as_new:
            return 0
        return super().initial_form_count()

    @classmethod
    def get_default_prefix(cls):
        opts = cls.model._meta
        return (
            opts.app_label
            + "-"
            + opts.model_name
            + "-"
            + cls.ct_field.name
            + "-"
            + cls.ct_fk_field.name
        )

    def save_new(self, form, commit=True):
        """
        Saves a new instance of the model with the given form.
        
        Args:
        form (ModelForm): The form containing the data to be saved.
        commit (bool, optional): If True, the instance will be saved to the database. Defaults to True.
        
        Returns:
        Model: The saved model instance.
        
        This function sets the content type and content type foreign key fields on the form instance before saving it. The content type is determined by the current instance's model, and the content type foreign
        """

        setattr(
            form.instance,
            self.ct_field.get_attname(),
            ContentType.objects.get_for_model(self.instance).pk,
        )
        setattr(form.instance, self.ct_fk_field.get_attname(), self.instance.pk)
        return form.save(commit=commit)


def generic_inlineformset_factory(
    model,
    form=ModelForm,
    formset=BaseGenericInlineFormSet,
    ct_field="content_type",
    fk_field="object_id",
    fields=None,
    exclude=None,
    extra=3,
    can_order=False,
    can_delete=True,
    max_num=None,
    formfield_callback=None,
    validate_max=False,
    for_concrete_model=True,
    min_num=None,
    validate_min=False,
    absolute_max=None,
    can_delete_extra=True,
):
    """
    Return a ``GenericInlineFormSet`` for the given kwargs.

    You must provide ``ct_field`` and ``fk_field`` if they are different from
    the defaults ``content_type`` and ``object_id`` respectively.
    """
    opts = model._meta
    # if there is no field called `ct_field` let the exception propagate
    ct_field = opts.get_field(ct_field)
    if (
        not isinstance(ct_field, models.ForeignKey)
        or ct_field.remote_field.model != ContentType
    ):
        raise Exception("fk_name '%s' is not a ForeignKey to ContentType" % ct_field)
    fk_field = opts.get_field(fk_field)  # let the exception propagate
    exclude = [*(exclude or []), ct_field.name, fk_field.name]
    FormSet = modelformset_factory(
        model,
        form=form,
        formfield_callback=formfield_callback,
        formset=formset,
        extra=extra,
        can_delete=can_delete,
        can_order=can_order,
        fields=fields,
        exclude=exclude,
        max_num=max_num,
        validate_max=validate_max,
        min_num=min_num,
        validate_min=validate_min,
        absolute_max=absolute_max,
        can_delete_extra=can_delete_extra,
    )
    FormSet.ct_field = ct_field
    FormSet.ct_fk_field = fk_field
    FormSet.for_concrete_model = for_concrete_model
    return FormSet
ormSet.for_concrete_model = for_concrete_model
    return FormSet
