from collections import defaultdict

from django.contrib.contenttypes.models import ContentType
from django.core import checks
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db import DEFAULT_DB_ALIAS, models, router, transaction
from django.db.models import DO_NOTHING
from django.db.models.base import ModelBase, make_foreign_order_accessors
from django.db.models.fields.mixins import FieldCacheMixin
from django.db.models.fields.related import (
    ForeignObject, ForeignObjectRel, ReverseManyToOneDescriptor,
    lazy_related_operation,
)
from django.db.models.query_utils import PathInfo
from django.utils.functional import cached_property


class GenericForeignKey(FieldCacheMixin):
    """
    Provide a generic many-to-one relation through the ``content_type`` and
    ``object_id`` fields.

    This class also doubles as an accessor to the related object (similar to
    ForwardManyToOneDescriptor) by adding itself as a model attribute.
    """

    # Field flags
    auto_created = False
    concrete = False
    editable = False
    hidden = False

    is_relation = True
    many_to_many = False
    many_to_one = True
    one_to_many = False
    one_to_one = False
    related_model = None
    remote_field = None

    def __init__(self, ct_field='content_type', fk_field='object_id', for_concrete_model=True):
        """
        Initialize a generic relation field.
        
        Args:
        ct_field (str, optional): The name of the field that will store the content type ID. Defaults to 'content_type'.
        fk_field (str, optional): The name of the field that will store the object ID. Defaults to 'object_id'.
        for_concrete_model (bool, optional): Indicates whether the model is a concrete model. Defaults to True.
        
        Attributes:
        ct_field (str): The name of the field storing the content
        """

        self.ct_field = ct_field
        self.fk_field = fk_field
        self.for_concrete_model = for_concrete_model
        self.editable = False
        self.rel = None
        self.column = None

    def contribute_to_class(self, cls, name, **kwargs):
        self.name = name
        self.model = cls
        cls._meta.add_field(self, private=True)
        setattr(cls, name, self)

    def get_filter_kwargs_for_object(self, obj):
        """See corresponding method on Field"""
        return {
            self.fk_field: getattr(obj, self.fk_field),
            self.ct_field: getattr(obj, self.ct_field),
        }

    def get_forward_related_filter(self, obj):
        """See corresponding method on RelatedField"""
        return {
            self.fk_field: obj.pk,
            self.ct_field: ContentType.objects.get_for_model(obj).pk,
        }

    def __str__(self):
        model = self.model
        app = model._meta.app_label
        return '%s.%s.%s' % (app, model._meta.object_name, self.name)

    def check(self, **kwargs):
        return [
            *self._check_field_name(),
            *self._check_object_id_field(),
            *self._check_content_type_field(),
        ]

    def _check_field_name(self):
        """
        Function to validate the name of a field.
        
        This function checks if the name of a field ends with an underscore. If it does, it returns a list containing a single error message indicating that field names must not end with an underscore. If the name does not end with an underscore, it returns an empty list.
        
        Args:
        self (Field): The field object to be validated.
        
        Returns:
        list: A list containing a single `checks.Error` object if the field name ends with an underscore
        """

        if self.name.endswith("_"):
            return [
                checks.Error(
                    'Field names must not end with an underscore.',
                    obj=self,
                    id='fields.E001',
                )
            ]
        else:
            return []

    def _check_object_id_field(self):
        try:
            self.model._meta.get_field(self.fk_field)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "The GenericForeignKey object ID references the "
                    "nonexistent field '%s'." % self.fk_field,
                    obj=self,
                    id='contenttypes.E001',
                )
            ]
        else:
            return []

    def _check_content_type_field(self):
        """
        Check if field named `field_name` in model `model` exists and is a
        valid content_type field (is a ForeignKey to ContentType).
        """
        try:
            field = self.model._meta.get_field(self.ct_field)
        except FieldDoesNotExist:
            return [
                checks.Error(
                    "The GenericForeignKey content type references the "
                    "nonexistent field '%s.%s'." % (
                        self.model._meta.object_name, self.ct_field
                    ),
                    obj=self,
                    id='contenttypes.E002',
                )
            ]
        else:
            if not isinstance(field, models.ForeignKey):
                return [
                    checks.Error(
                        "'%s.%s' is not a ForeignKey." % (
                            self.model._meta.object_name, self.ct_field
                        ),
                        hint=(
                            "GenericForeignKeys must use a ForeignKey to "
                            "'contenttypes.ContentType' as the 'content_type' field."
                        ),
                        obj=self,
                        id='contenttypes.E003',
                    )
                ]
            elif field.remote_field.model != ContentType:
                return [
                    checks.Error(
                        "'%s.%s' is not a ForeignKey to 'contenttypes.ContentType'." % (
                            self.model._meta.object_name, self.ct_field
                        ),
                        hint=(
                            "GenericForeignKeys must use a ForeignKey to "
                            "'contenttypes.ContentType' as the 'content_type' field."
                        ),
                        obj=self,
                        id='contenttypes.E004',
                    )
                ]
            else:
                return []

    def get_cache_name(self):
        return self.name

    def get_content_type(self, obj=None, id=None, using=None):
        """
        Retrieve the content type for a given object or ID.
        
        This function returns the content type for a Django model instance or a content type ID.
        
        Parameters:
        obj (object, optional): The Django model instance for which to get the content type.
        id (int, optional): The content type ID to retrieve.
        using (str, optional): The database alias to use for the query. Defaults to the model's default database.
        
        Returns:
        django.contrib.contenttypes.models.ContentType: The content type
        """

        if obj is not None:
            return ContentType.objects.db_manager(obj._state.db).get_for_model(
                obj, for_concrete_model=self.for_concrete_model)
        elif id is not None:
            return ContentType.objects.db_manager(using).get_for_id(id)
        else:
            # This should never happen. I love comments like this, don't you?
            raise Exception("Impossible arguments to GFK.get_content_type!")

    def get_prefetch_queryset(self, instances, queryset=None):
        if queryset is not None:
            raise ValueError("Custom queryset can't be used for this lookup.")

        # For efficiency, group the instances by content type and then do one
        # query per model
        fk_dict = defaultdict(set)
        # We need one instance for each group in order to get the right db:
        instance_dict = {}
        ct_attname = self.model._meta.get_field(self.ct_field).get_attname()
        for instance in instances:
            # We avoid looking for values if either ct_id or fkey value is None
            ct_id = getattr(instance, ct_attname)
            if ct_id is not None:
                fk_val = getattr(instance, self.fk_field)
                if fk_val is not None:
                    fk_dict[ct_id].add(fk_val)
                    instance_dict[ct_id] = instance

        ret_val = []
        for ct_id, fkeys in fk_dict.items():
            instance = instance_dict[ct_id]
            ct = self.get_content_type(id=ct_id, using=instance._state.db)
            ret_val.extend(ct.get_all_objects_for_this_type(pk__in=fkeys))

        # For doing the join in Python, we have to match both the FK val and the
        # content type, so we use a callable that returns a (fk, class) pair.
        def gfk_key(obj):
            ct_id = getattr(obj, ct_attname)
            if ct_id is None:
                return None
            else:
                model = self.get_content_type(id=ct_id,
                                              using=obj._state.db).model_class()
                return (model._meta.pk.get_prep_value(getattr(obj, self.fk_field)),
                        model)

        return (
            ret_val,
            lambda obj: (obj.pk, obj.__class__),
            gfk_key,
            True,
            self.name,
            True,
        )

    def __get__(self, instance, cls=None):
        """
        Retrieve the related object for the given instance.
        
        This method is used to fetch the related object based on the content type and primary key of the instance. It checks if the related object is already cached, and if not, it retrieves the content type and primary key from the instance. It then attempts to get the related object from the content type's model using the primary key. If the related object is found, it is cached for future use.
        
        Parameters:
        instance (object): The instance of the
        """

        if instance is None:
            return self

        # Don't use getattr(instance, self.ct_field) here because that might
        # reload the same ContentType over and over (#5570). Instead, get the
        # content type ID here, and later when the actual instance is needed,
        # use ContentType.objects.get_for_id(), which has a global cache.
        f = self.model._meta.get_field(self.ct_field)
        ct_id = getattr(instance, f.get_attname(), None)
        pk_val = getattr(instance, self.fk_field)

        rel_obj = self.get_cached_value(instance, default=None)
        if rel_obj is not None:
            ct_match = ct_id == self.get_content_type(obj=rel_obj, using=instance._state.db).id
            pk_match = rel_obj._meta.pk.to_python(pk_val) == rel_obj.pk
            if ct_match and pk_match:
                return rel_obj
            else:
                rel_obj = None
        if ct_id is not None:
            ct = self.get_content_type(id=ct_id, using=instance._state.db)
            try:
                rel_obj = ct.get_object_for_this_type(pk=pk_val)
            except ObjectDoesNotExist:
                pass
        self.set_cached_value(instance, rel_obj)
        return rel_obj

    def __set__(self, instance, value):
        ct = None
        fk = None
        if value is not None:
            ct = self.get_content_type(obj=value)
            fk = value.pk

        setattr(instance, self.ct_field, ct)
        setattr(instance, self.fk_field, fk)
        self.set_cached_value(instance, value)


class GenericRel(ForeignObjectRel):
    """
    Used by GenericRelation to store information about the relation.
    """

    def __init__(self, field, to, related_name=None, related_query_name=None, limit_choices_to=None):
        """
        Initialize a ForeignKey relationship.
        
        Args:
        field (Field): The field to which the foreign key is related.
        to (Model): The model to which the foreign key points.
        related_name (str, optional): The name to use for the relation from the related object back to this one. Defaults to None.
        related_query_name (str, optional): The name to use for the related query name. If not provided, a default value of '+' is used. Defaults to None.
        """

        super().__init__(
            field, to, related_name=related_query_name or '+',
            related_query_name=related_query_name,
            limit_choices_to=limit_choices_to, on_delete=DO_NOTHING,
        )


class GenericRelation(ForeignObject):
    """
    Provide a reverse to a relation created by a GenericForeignKey.
    """

    # Field flags
    auto_created = False

    many_to_many = False
    many_to_one = False
    one_to_many = True
    one_to_one = False

    rel_class = GenericRel

    mti_inherited = False

    def __init__(self, to, object_id_field='object_id', content_type_field='content_type',
                 for_concrete_model=True, related_query_name=None, limit_choices_to=None, **kwargs):
        kwargs['rel'] = self.rel_class(
            self, to,
            related_query_name=related_query_name,
            limit_choices_to=limit_choices_to,
        )

        kwargs['blank'] = True
        kwargs['on_delete'] = models.CASCADE
        kwargs['editable'] = False
        kwargs['serialize'] = False

        # This construct is somewhat of an abuse of ForeignObject. This field
        # represents a relation from pk to object_id field. But, this relation
        # isn't direct, the join is generated reverse along foreign key. So,
        # the from_field is object_id field, to_field is pk because of the
        # reverse join.
        super().__init__(to, from_fields=[object_id_field], to_fields=[], **kwargs)

        self.object_id_field_name = object_id_field
        self.content_type_field_name = content_type_field
        self.for_concrete_model = for_concrete_model

    def check(self, **kwargs):
        """
        Checks for the existence of generic foreign keys.
        
        This method performs validation checks by first calling the superclass's `check` method with the provided keyword arguments (`**kwargs`). It then appends the results of the `_check_generic_foreign_key_existence` method to the returned list. The function returns a list of validation results.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments to be passed to the superclass's `check` method.
        
        Returns:
        list: A list of validation results, which includes the results
        """

        return [
            *super().check(**kwargs),
            *self._check_generic_foreign_key_existence(),
        ]

    def _is_matching_generic_foreign_key(self, field):
        """
        Return True if field is a GenericForeignKey whose content type and
        object id fields correspond to the equivalent attributes on this
        GenericRelation.
        """
        return (
            isinstance(field, GenericForeignKey) and
            field.ct_field == self.content_type_field_name and
            field.fk_field == self.object_id_field_name
        )

    def _check_generic_foreign_key_existence(self):
        target = self.remote_field.model
        if isinstance(target, ModelBase):
            fields = target._meta.private_fields
            if any(self._is_matching_generic_foreign_key(field) for field in fields):
                return []
            else:
                return [
                    checks.Error(
                        "The GenericRelation defines a relation with the model "
                        "'%s.%s', but that model does not have a GenericForeignKey." % (
                            target._meta.app_label, target._meta.object_name
                        ),
                        obj=self,
                        id='contenttypes.E004',
                    )
                ]
        else:
            return []

    def resolve_related_fields(self):
        self.to_fields = [self.model._meta.pk.name]
        return [(self.remote_field.model._meta.get_field(self.object_id_field_name), self.model._meta.pk)]

    def _get_path_info_with_parent(self, filtered_relation):
        """
        Return the path that joins the current model through any parent models.
        The idea is that if you have a GFK defined on a parent model then we
        need to join the parent model first, then the child model.
        """
        # With an inheritance chain ChildTag -> Tag and Tag defines the
        # GenericForeignKey, and a TaggedItem model has a GenericRelation to
        # ChildTag, then we need to generate a join from TaggedItem to Tag
        # (as Tag.object_id == TaggedItem.pk), and another join from Tag to
        # ChildTag (as that is where the relation is to). Do this by first
        # generating a join to the parent model, then generating joins to the
        # child models.
        path = []
        opts = self.remote_field.model._meta.concrete_model._meta
        parent_opts = opts.get_field(self.object_id_field_name).model._meta
        target = parent_opts.pk
        path.append(PathInfo(
            from_opts=self.model._meta,
            to_opts=parent_opts,
            target_fields=(target,),
            join_field=self.remote_field,
            m2m=True,
            direct=False,
            filtered_relation=filtered_relation,
        ))
        # Collect joins needed for the parent -> child chain. This is easiest
        # to do if we collect joins for the child -> parent chain and then
        # reverse the direction (call to reverse() and use of
        # field.remote_field.get_path_info()).
        parent_field_chain = []
        while parent_opts != opts:
            field = opts.get_ancestor_link(parent_opts.model)
            parent_field_chain.append(field)
            opts = field.remote_field.model._meta
        parent_field_chain.reverse()
        for field in parent_field_chain:
            path.extend(field.remote_field.get_path_info())
        return path

    def get_path_info(self, filtered_relation=None):
        opts = self.remote_field.model._meta
        object_id_field = opts.get_field(self.object_id_field_name)
        if object_id_field.model != opts.model:
            return self._get_path_info_with_parent(filtered_relation)
        else:
            target = opts.pk
            return [PathInfo(
                from_opts=self.model._meta,
                to_opts=opts,
                target_fields=(target,),
                join_field=self.remote_field,
                m2m=True,
                direct=False,
                filtered_relation=filtered_relation,
            )]

    def get_reverse_path_info(self, filtered_relation=None):
        """
        Generates a reverse path information for a model field.
        
        This function is used to create a PathInfo object that represents the reverse relationship between two Django model fields. The PathInfo object is used internally by Django to manage and traverse relationships between models.
        
        Parameters:
        filtered_relation (str, optional): A string representing a filtered relation. If provided, it will be used to filter the path information.
        
        Returns:
        list: A list containing a single PathInfo object. The PathInfo object contains information about
        """

        opts = self.model._meta
        from_opts = self.remote_field.model._meta
        return [PathInfo(
            from_opts=from_opts,
            to_opts=opts,
            target_fields=(opts.pk,),
            join_field=self,
            m2m=not self.unique,
            direct=False,
            filtered_relation=filtered_relation,
        )]

    def value_to_string(self, obj):
        qs = getattr(obj, self.name).all()
        return str([instance.pk for instance in qs])

    def contribute_to_class(self, cls, name, **kwargs):
        kwargs['private_only'] = True
        super().contribute_to_class(cls, name, **kwargs)
        self.model = cls
        # Disable the reverse relation for fields inherited by subclasses of a
        # model in multi-table inheritance. The reverse relation points to the
        # field of the base model.
        if self.mti_inherited:
            self.remote_field.related_name = '+'
            self.remote_field.related_query_name = None
        setattr(cls, self.name, ReverseGenericManyToOneDescriptor(self.remote_field))

        # Add get_RELATED_order() and set_RELATED_order() to the model this
        # field belongs to, if the model on the other end of this relation
        # is ordered with respect to its corresponding GenericForeignKey.
        if not cls._meta.abstract:

            def make_generic_foreign_order_accessors(related_model, model):
                if self._is_matching_generic_foreign_key(model._meta.order_with_respect_to):
                    make_foreign_order_accessors(model, related_model)

            lazy_related_operation(make_generic_foreign_order_accessors, self.model, self.remote_field.model)

    def set_attributes_from_rel(self):
        pass

    def get_internal_type(self):
        return "ManyToManyField"

    def get_content_type(self):
        """
        Return the content type associated with this field's model.
        """
        return ContentType.objects.get_for_model(self.model,
                                                 for_concrete_model=self.for_concrete_model)

    def get_extra_restriction(self, where_class, alias, remote_alias):
        """
        Generates a WHERE clause condition for filtering related objects based on content type.
        
        This method is used to create a condition for filtering related objects in a database query. It ensures that only objects of a specific content type are included in the query results.
        
        Parameters:
        where_class (object): The class used to build the WHERE clause condition.
        alias (str): The alias of the model being queried.
        remote_alias (str): The alias of the related model.
        
        Returns:
        where_class: A
        """

        field = self.remote_field.model._meta.get_field(self.content_type_field_name)
        contenttype_pk = self.get_content_type().pk
        cond = where_class()
        lookup = field.get_lookup('exact')(field.get_col(remote_alias), contenttype_pk)
        cond.add(lookup, 'AND')
        return cond

    def bulk_related_objects(self, objs, using=DEFAULT_DB_ALIAS):
        """
        Return all objects related to ``objs`` via this ``GenericRelation``.
        """
        return self.remote_field.model._base_manager.db_manager(using).filter(**{
            "%s__pk" % self.content_type_field_name: ContentType.objects.db_manager(using).get_for_model(
                self.model, for_concrete_model=self.for_concrete_model).pk,
            "%s__in" % self.object_id_field_name: [obj.pk for obj in objs]
        })


class ReverseGenericManyToOneDescriptor(ReverseManyToOneDescriptor):
    """
    Accessor to the related objects manager on the one-to-many relation created
    by GenericRelation.

    In the example::

        class Post(Model):
            comments = GenericRelation(Comment)

    ``post.comments`` is a ReverseGenericManyToOneDescriptor instance.
    """

    @cached_property
    def related_manager_cls(self):
        return create_generic_related_manager(
            self.rel.model._default_manager.__class__,
            self.rel,
        )


def create_generic_related_manager(superclass, rel):
    """
    Factory function to create a manager that subclasses another manager
    (generally the default manager of a given model) and adds behaviors
    specific to generic relations.
    """

    class GenericRelatedObjectManager(superclass):
        def __init__(self, instance=None):
            """
            Initialize the related object manager.
            
            Args:
            instance (Model): The instance of the model for which the related objects are being managed.
            
            Attributes:
            instance (Model): The instance of the model.
            model (Model): The model class for the related objects.
            content_type (ContentType): The content type object for the related model.
            content_type_field_name (str): The name of the content type field.
            object_id_field_name (str): The name of the object ID field.
            """

            super().__init__()

            self.instance = instance

            self.model = rel.model

            content_type = ContentType.objects.db_manager(instance._state.db).get_for_model(
                instance, for_concrete_model=rel.field.for_concrete_model)
            self.content_type = content_type
            self.content_type_field_name = rel.field.content_type_field_name
            self.object_id_field_name = rel.field.object_id_field_name
            self.prefetch_cache_name = rel.field.attname
            self.pk_val = instance.pk

            self.core_filters = {
                '%s__pk' % self.content_type_field_name: content_type.id,
                self.object_id_field_name: self.pk_val,
            }

        def __call__(self, *, manager):
            manager = getattr(self.model, manager)
            manager_class = create_generic_related_manager(manager.__class__, rel)
            return manager_class(instance=self.instance)
        do_not_call_in_templates = True

        def __str__(self):
            return repr(self)

        def _apply_rel_filters(self, queryset):
            """
            Filter the queryset for the instance this manager is bound to.
            """
            db = self._db or router.db_for_read(self.model, instance=self.instance)
            return queryset.using(db).filter(**self.core_filters)

        def _remove_prefetched_objects(self):
            try:
                self.instance._prefetched_objects_cache.pop(self.prefetch_cache_name)
            except (AttributeError, KeyError):
                pass  # nothing to clear from cache

        def get_queryset(self):
            try:
                return self.instance._prefetched_objects_cache[self.prefetch_cache_name]
            except (AttributeError, KeyError):
                queryset = super().get_queryset()
                return self._apply_rel_filters(queryset)

        def get_prefetch_queryset(self, instances, queryset=None):
            if queryset is None:
                queryset = super().get_queryset()

            queryset._add_hints(instance=instances[0])
            queryset = queryset.using(queryset._db or self._db)

            query = {
                '%s__pk' % self.content_type_field_name: self.content_type.id,
                '%s__in' % self.object_id_field_name: {obj.pk for obj in instances}
            }

            # We (possibly) need to convert object IDs to the type of the
            # instances' PK in order to match up instances:
            object_id_converter = instances[0]._meta.pk.to_python
            return (
                queryset.filter(**query),
                lambda relobj: object_id_converter(getattr(relobj, self.object_id_field_name)),
                lambda obj: obj.pk,
                False,
                self.prefetch_cache_name,
                False,
            )

        def add(self, *objs, bulk=True):
            """
            Add related objects to the object.
            
            This method adds related objects to the current object. It supports both bulk and individual object addition.
            
            Parameters:
            *objs (object): One or more objects to be added as related objects.
            bulk (bool, optional): If True, the method will use bulk update for efficiency. If False, each object will be saved individually. Default is True.
            
            Returns:
            None: This method does not return any value. It modifies the related objects in place.
            
            Raises
            """

            self._remove_prefetched_objects()
            db = router.db_for_write(self.model, instance=self.instance)

            def check_and_update_obj(obj):
                if not isinstance(obj, self.model):
                    raise TypeError("'%s' instance expected, got %r" % (
                        self.model._meta.object_name, obj
                    ))
                setattr(obj, self.content_type_field_name, self.content_type)
                setattr(obj, self.object_id_field_name, self.pk_val)

            if bulk:
                pks = []
                for obj in objs:
                    if obj._state.adding or obj._state.db != db:
                        raise ValueError(
                            "%r instance isn't saved. Use bulk=False or save "
                            "the object first." % obj
                        )
                    check_and_update_obj(obj)
                    pks.append(obj.pk)

                self.model._base_manager.using(db).filter(pk__in=pks).update(**{
                    self.content_type_field_name: self.content_type,
                    self.object_id_field_name: self.pk_val,
                })
            else:
                with transaction.atomic(using=db, savepoint=False):
                    for obj in objs:
                        check_and_update_obj(obj)
                        obj.save()
        add.alters_data = True

        def remove(self, *objs, bulk=True):
            if not objs:
                return
            self._clear(self.filter(pk__in=[o.pk for o in objs]), bulk)
        remove.alters_data = True

        def clear(self, *, bulk=True):
            self._clear(self, bulk)
        clear.alters_data = True

        def _clear(self, queryset, bulk):
            self._remove_prefetched_objects()
            db = router.db_for_write(self.model, instance=self.instance)
            queryset = queryset.using(db)
            if bulk:
                # `QuerySet.delete()` creates its own atomic block which
                # contains the `pre_delete` and `post_delete` signal handlers.
                queryset.delete()
            else:
                with transaction.atomic(using=db, savepoint=False):
                    for obj in queryset:
                        obj.delete()
        _clear.alters_data = True

        def set(self, objs, *, bulk=True, clear=False):
            """
            Sets the related objects for the given model instance.
            
            This method updates the related objects for the model instance. It can either clear the existing related objects and add the new ones, or only add new objects that are not already related.
            
            Parameters:
            objs (Iterable): The objects to be set as related to the model instance.
            bulk (bool, optional): If True, the objects will be added in bulk. Defaults to True.
            clear (bool, optional): If True, the existing related
            """

            # Force evaluation of `objs` in case it's a queryset whose value
            # could be affected by `manager.clear()`. Refs #19816.
            objs = tuple(objs)

            db = router.db_for_write(self.model, instance=self.instance)
            with transaction.atomic(using=db, savepoint=False):
                if clear:
                    self.clear()
                    self.add(*objs, bulk=bulk)
                else:
                    old_objs = set(self.using(db).all())
                    new_objs = []
                    for obj in objs:
                        if obj in old_objs:
                            old_objs.remove(obj)
                        else:
                            new_objs.append(obj)

                    self.remove(*old_objs)
                    self.add(*new_objs, bulk=bulk)
        set.alters_data = True

        def create(self, **kwargs):
            self._remove_prefetched_objects()
            kwargs[self.content_type_field_name] = self.content_type
            kwargs[self.object_id_field_name] = self.pk_val
            db = router.db_for_write(self.model, instance=self.instance)
            return super().using(db).create(**kwargs)
        create.alters_data = True

        def get_or_create(self, **kwargs):
            kwargs[self.content_type_field_name] = self.content_type
            kwargs[self.object_id_field_name] = self.pk_val
            db = router.db_for_write(self.model, instance=self.instance)
            return super().using(db).get_or_create(**kwargs)
        get_or_create.alters_data = True

        def update_or_create(self, **kwargs):
            """
            Update or create an instance of the model based on the provided keyword arguments. This method is designed to be used within the context of a Django model manager.
            
            Parameters:
            **kwargs (dict): Keyword arguments to be used for updating or creating the model instance. These should include the content type and object ID fields.
            
            Returns:
            tuple: A tuple containing the updated or created model instance and a boolean indicating whether a new instance was created (True) or an existing one was updated (False).
            
            Key
            """

            kwargs[self.content_type_field_name] = self.content_type
            kwargs[self.object_id_field_name] = self.pk_val
            db = router.db_for_write(self.model, instance=self.instance)
            return super().using(db).update_or_create(**kwargs)
        update_or_create.alters_data = True

    return GenericRelatedObjectManager
