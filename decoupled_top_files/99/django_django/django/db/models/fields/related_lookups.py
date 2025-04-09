"""
This Python file contains definitions for custom Django ORM lookups and related utilities. It introduces several classes and functions designed to handle complex multi-column lookups and related filtering operations in Django models.

#### Main Classes:
- **MultiColSource**: Represents a source of data that involves multiple columns. It provides methods for initializing, relabeling, and resolving expressions.
- **RelatedIn**: A custom `In` lookup that supports multi-column comparisons and normalization of values.
- **RelatedLookupMixin**: A mixin class that provides common functionality for handling single-column relations, including normalization and preparation of lookup values.
- **RelatedExact, RelatedLessThan, RelatedGreaterThan, RelatedGreaterThanOrEqual, RelatedLessThanOrEqual, RelatedIsNull**: Custom lookup classes that extend the
"""
import warnings

from django.db.models.lookups import (
    Exact,
    GreaterThan,
    GreaterThanOrEqual,
    In,
    IsNull,
    LessThan,
    LessThanOrEqual,
)
from django.utils.deprecation import RemovedInDjango50Warning


class MultiColSource:
    contains_aggregate = False

    def __init__(self, alias, targets, sources, field):
        """
        Initialize a new instance of the class.
        
        Args:
        alias (str): The alias for the object.
        targets (list): The target objects.
        sources (list): The source objects.
        field (str): The field to be processed.
        
        Attributes:
        targets (list): The target objects.
        sources (list): The source objects.
        field (str): The field to be processed.
        alias (str): The alias for the object.
        output_field (str):
        """

        self.targets, self.sources, self.field, self.alias = (
            targets,
            sources,
            field,
            alias,
        )
        self.output_field = self.field

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.alias, self.field)

    def relabeled_clone(self, relabels):
        """
        Relabels the alias of a data source or target and returns a cloned instance.
        
        Args:
        relabels (dict): A dictionary mapping original aliases to new aliases.
        
        Returns:
        object: A cloned instance of the current class with the alias relabeled according to the provided mapping.
        
        Note:
        - The function uses the `get` method of the `relabels` dictionary to retrieve the new alias for the current instance's alias.
        - If the current instance's alias
        """

        return self.__class__(
            relabels.get(self.alias, self.alias), self.targets, self.sources, self.field
        )

    def get_lookup(self, lookup):
        return self.output_field.get_lookup(lookup)

    def resolve_expression(self, *args, **kwargs):
        return self


def get_normalized_value(value, lhs):
    """
    Normalize a given value or model instance for use in a related filter.
    
    Args:
    value: The value or model instance to normalize.
    lhs: The left-hand side of the filter expression.
    
    Returns:
    A normalized value or tuple of values suitable for use in a related filter.
    
    Raises:
    ValueError: If an unsaved model instance is passed to a related filter.
    RemovedInDjango50Warning: If an unsaved model instance is passed to a related filter (
    """

    from django.db.models import Model

    if isinstance(value, Model):
        if value.pk is None:
            # When the deprecation ends, replace with:
            # raise ValueError(
            #     "Model instances passed to related filters must be saved."
            # )
            warnings.warn(
                "Passing unsaved model instances to related filters is deprecated.",
                RemovedInDjango50Warning,
            )
        value_list = []
        sources = lhs.output_field.path_infos[-1].target_fields
        for source in sources:
            while not isinstance(value, source.model) and source.remote_field:
                source = source.remote_field.model._meta.get_field(
                    source.remote_field.field_name
                )
            try:
                value_list.append(getattr(value, source.attname))
            except AttributeError:
                # A case like Restaurant.objects.filter(place=restaurant_instance),
                # where place is a OneToOneField and the primary key of Restaurant.
                return (value.pk,)
        return tuple(value_list)
    if not isinstance(value, tuple):
        return (value,)
    return value


class RelatedIn(In):
    def get_prep_lookup(self):
        """
        Generates a prepared lookup value for database query.
        
        This method processes the right-hand side (``rhs``) of a lookup expression
        to ensure it is in a suitable format for database queries. It handles
        different scenarios based on the type of the left-hand side (``lhs``) and
        whether the ``rhs`` is a direct value or a queryset.
        
        Parameters:
        None
        
        Returns:
        The prepared lookup value.
        
        Important Functions:
        - `get
        """

        if not isinstance(self.lhs, MultiColSource):
            if self.rhs_is_direct_value():
                # If we get here, we are dealing with single-column relations.
                self.rhs = [get_normalized_value(val, self.lhs)[0] for val in self.rhs]
                # We need to run the related field's get_prep_value(). Consider
                # case ForeignKey to IntegerField given value 'abc'. The
                # ForeignKey itself doesn't have validation for non-integers,
                # so we must run validation using the target field.
                if hasattr(self.lhs.output_field, "path_infos"):
                    # Run the target field's get_prep_value. We can safely
                    # assume there is only one as we don't get to the direct
                    # value branch otherwise.
                    target_field = self.lhs.output_field.path_infos[-1].target_fields[
                        -1
                    ]
                    self.rhs = [target_field.get_prep_value(v) for v in self.rhs]
            elif not getattr(self.rhs, "has_select_fields", True) and not getattr(
                self.lhs.field.target_field, "primary_key", False
            ):
                self.rhs.clear_select_clause()
                if (
                    getattr(self.lhs.output_field, "primary_key", False)
                    and self.lhs.output_field.model == self.rhs.model
                ):
                    # A case like
                    # Restaurant.objects.filter(place__in=restaurant_qs), where
                    # place is a OneToOneField and the primary key of
                    # Restaurant.
                    target_field = self.lhs.field.name
                else:
                    target_field = self.lhs.field.target_field.name
                self.rhs.add_fields([target_field], True)
        return super().get_prep_lookup()

    def as_sql(self, compiler, connection):
        """
        Generates SQL for a multicolumn lookup.
        
        Args:
        compiler: The SQL compiler instance.
        connection: The database connection.
        
        Returns:
        The generated SQL query.
        
        Summary:
        This function generates SQL for a multicolumn lookup. It handles both cases where the right-hand side (rhs) is a direct value and when it's a subquery. For direct values, it creates a WhereNode with AND and OR connectors, and for subqueries, it uses SubqueryConstraint.
        """

        if isinstance(self.lhs, MultiColSource):
            # For multicolumn lookups we need to build a multicolumn where clause.
            # This clause is either a SubqueryConstraint (for values that need
            # to be compiled to SQL) or an OR-combined list of
            # (col1 = val1 AND col2 = val2 AND ...) clauses.
            from django.db.models.sql.where import (
                AND,
                OR,
                SubqueryConstraint,
                WhereNode,
            )

            root_constraint = WhereNode(connector=OR)
            if self.rhs_is_direct_value():
                values = [get_normalized_value(value, self.lhs) for value in self.rhs]
                for value in values:
                    value_constraint = WhereNode()
                    for source, target, val in zip(
                        self.lhs.sources, self.lhs.targets, value
                    ):
                        lookup_class = target.get_lookup("exact")
                        lookup = lookup_class(
                            target.get_col(self.lhs.alias, source), val
                        )
                        value_constraint.add(lookup, AND)
                    root_constraint.add(value_constraint, OR)
            else:
                root_constraint.add(
                    SubqueryConstraint(
                        self.lhs.alias,
                        [target.column for target in self.lhs.targets],
                        [source.name for source in self.lhs.sources],
                        self.rhs,
                    ),
                    AND,
                )
            return root_constraint.as_sql(compiler, connection)
        return super().as_sql(compiler, connection)


class RelatedLookupMixin:
    def get_prep_lookup(self):
        """
        Generates a prepared lookup value for a database query.
        
        This method handles single-column relations by normalizing the right-hand side (rhs) value
        and ensuring that the related field's `get_prep_value()` method is called to validate and prepare
        the value for storage or comparison. It returns the prepared lookup value after performing these
        operations.
        
        Args:
        self: The instance of the class containing the lhs (left-hand side) and rhs (right-hand side)
        values
        """

        if not isinstance(self.lhs, MultiColSource) and not hasattr(
            self.rhs, "resolve_expression"
        ):
            # If we get here, we are dealing with single-column relations.
            self.rhs = get_normalized_value(self.rhs, self.lhs)[0]
            # We need to run the related field's get_prep_value(). Consider case
            # ForeignKey to IntegerField given value 'abc'. The ForeignKey itself
            # doesn't have validation for non-integers, so we must run validation
            # using the target field.
            if self.prepare_rhs and hasattr(self.lhs.output_field, "path_infos"):
                # Get the target field. We can safely assume there is only one
                # as we don't get to the direct value branch otherwise.
                target_field = self.lhs.output_field.path_infos[-1].target_fields[-1]
                self.rhs = target_field.get_prep_value(self.rhs)

        return super().get_prep_lookup()

    def as_sql(self, compiler, connection):
        """
        Generates an SQL query for a database operation.
        
        This function is responsible for converting a Django ORM query into its corresponding SQL representation. It handles cases where the left-hand side (lhs) of a comparison is a `MultiColSource`, which represents multiple columns being compared simultaneously. The function normalizes the right-hand side (rhs) value and constructs a `WhereNode` object that contains multiple individual lookups, each comparing one column from the `MultiColSource` with the normalized value. These
        """

        if isinstance(self.lhs, MultiColSource):
            assert self.rhs_is_direct_value()
            self.rhs = get_normalized_value(self.rhs, self.lhs)
            from django.db.models.sql.where import AND, WhereNode

            root_constraint = WhereNode()
            for target, source, val in zip(
                self.lhs.targets, self.lhs.sources, self.rhs
            ):
                lookup_class = target.get_lookup(self.lookup_name)
                root_constraint.add(
                    lookup_class(target.get_col(self.lhs.alias, source), val), AND
                )
            return root_constraint.as_sql(compiler, connection)
        return super().as_sql(compiler, connection)


class RelatedExact(RelatedLookupMixin, Exact):
    pass


class RelatedLessThan(RelatedLookupMixin, LessThan):
    pass


class RelatedGreaterThan(RelatedLookupMixin, GreaterThan):
    pass


class RelatedGreaterThanOrEqual(RelatedLookupMixin, GreaterThanOrEqual):
    pass


class RelatedLessThanOrEqual(RelatedLookupMixin, LessThanOrEqual):
    pass


class RelatedIsNull(RelatedLookupMixin, IsNull):
    pass
