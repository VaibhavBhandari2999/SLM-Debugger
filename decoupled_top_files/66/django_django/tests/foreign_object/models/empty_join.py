"""
This Python file contains custom Django model fields and relations designed to handle specific querying requirements. It introduces two custom `ForeignObject` subclasses: `StartsWithRelation` and `BrokenContainsRelation`. These classes extend Django's ORM capabilities by allowing for more flexible relationship definitions and query operations.

#### Classes Defined:
1. **CustomForeignObjectRel**: A custom `ForeignObjectRel` class that mimics the behavior of a `Field` to enable bidirectional `ReverseManyToOneDescriptor`.
2. **StartsWithRelation**: A custom `ForeignObject` that uses the `StartsWith` lookup for joining queries, effectively creating a many-to-many relationship with reverse descriptors.
3. **BrokenContainsRelation**: A subclass of `StartsWithRelation` that intentionally fails to
"""
from django.db import models
from django.db.models.fields.related import ReverseManyToOneDescriptor
from django.db.models.lookups import StartsWith
from django.db.models.query_utils import PathInfo


class CustomForeignObjectRel(models.ForeignObjectRel):
    """
    Define some extra Field methods so this Rel acts more like a Field, which
    lets us use ReverseManyToOneDescriptor in both directions.
    """
    @property
    def foreign_related_fields(self):
        return tuple(lhs_field for lhs_field, rhs_field in self.field.related_fields)

    def get_attname(self):
        return self.name


class StartsWithRelation(models.ForeignObject):
    """
    A ForeignObject that uses StartsWith operator in its joins instead of
    the default equality operator. This is logically a many-to-many relation
    and creates a ReverseManyToOneDescriptor in both directions.
    """
    auto_created = False

    many_to_many = False
    many_to_one = True
    one_to_many = False
    one_to_one = False

    rel_class = CustomForeignObjectRel

    def __init__(self, *args, **kwargs):
        kwargs['on_delete'] = models.DO_NOTHING
        super().__init__(*args, **kwargs)

    @property
    def field(self):
        """
        Makes ReverseManyToOneDescriptor work in both directions.
        """
        return self.remote_field

    def get_extra_restriction(self, where_class, alias, related_alias):
        """
        Generates a database query restriction using the `StartsWith` lookup.
        
        Args:
        where_class (object): The class used to construct the WHERE clause of a SQL query.
        alias (str): The table alias for the model being queried.
        related_alias (str): The table alias for the related model.
        
        Returns:
        object: A `StartsWith` lookup instance that can be used to filter query results based on the start of a string field value.
        
        This method constructs a
        """

        to_field = self.remote_field.model._meta.get_field(self.to_fields[0])
        from_field = self.model._meta.get_field(self.from_fields[0])
        return StartsWith(to_field.get_col(alias), from_field.get_col(related_alias))

    def get_joining_columns(self, reverse_join=False):
        return ()

    def get_path_info(self, filtered_relation=None):
        """
        Retrieve path information for a relationship between two models.
        
        Args:
        filtered_relation (Optional[FilteredRelation]): An optional filter applied to the relation.
        
        Returns:
        List[PathInfo]: A list containing a single `PathInfo` object that describes the path between the current model and the related model.
        
        This function constructs and returns a `PathInfo` object representing the relationship between the local model (`self.model`) and the remote model (`self.remote_field.model`). The `PathInfo`
        """

        to_opts = self.remote_field.model._meta
        from_opts = self.model._meta
        return [PathInfo(
            from_opts=from_opts,
            to_opts=to_opts,
            target_fields=(to_opts.pk,),
            join_field=self,
            m2m=False,
            direct=False,
            filtered_relation=filtered_relation,
        )]

    def get_reverse_path_info(self, filtered_relation=None):
        """
        Generates a reverse path information object for a given model relationship.
        
        Args:
        filtered_relation (Optional[Q]): A filter query to apply to the related model.
        
        Returns:
        PathInfo: An object containing information about the reverse relationship between two models.
        
        Important Functions:
        - `self.model._meta`: Accesses metadata of the current model.
        - `self.remote_field.model._meta`: Accesses metadata of the related model.
        - `PathInfo`: Creates an instance
        """

        to_opts = self.model._meta
        from_opts = self.remote_field.model._meta
        return [PathInfo(
            from_opts=from_opts,
            to_opts=to_opts,
            target_fields=(to_opts.pk,),
            join_field=self.remote_field,
            m2m=False,
            direct=False,
            filtered_relation=filtered_relation,
        )]

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)
        setattr(cls, self.name, ReverseManyToOneDescriptor(self))


class BrokenContainsRelation(StartsWithRelation):
    """
    This model is designed to yield no join conditions and
    raise an exception in ``Join.as_sql()``.
    """
    def get_extra_restriction(self, where_class, alias, related_alias):
        return None


class SlugPage(models.Model):
    slug = models.CharField(max_length=20, unique=True)
    descendants = StartsWithRelation(
        'self',
        from_fields=['slug'],
        to_fields=['slug'],
        related_name='ascendants',
    )
    containers = BrokenContainsRelation(
        'self',
        from_fields=['slug'],
        to_fields=['slug'],
    )

    class Meta:
        ordering = ['slug']

    def __str__(self):
        return 'SlugPage %s' % self.slug
