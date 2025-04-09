"""
This Python file contains definitions for various database lookups and transformations used in Django ORM. It includes:

- **Lookup Class**: Base class for defining custom database lookups. It handles the initialization, processing, and compilation of lookup expressions.
- **Transform Class**: Base class for defining custom database transformations. It provides methods for applying bilateral transforms and handling expressions.
- **BuiltinLookup Class**: Implements common lookup operations such as `exact`, `iexact`, `gt`, `gte`, `lt`, `lte`, etc.
- **PatternLookup Class**: Handles pattern-based lookups like `contains`, `icontains`, `startswith`, `istartswith`, `endswith`, `iendswith`.
- **YearLookup Class**: Provides year-based look
"""
import itertools
import math
import warnings
from copy import copy

from django.core.exceptions import EmptyResultSet
from django.db.models.expressions import Case, Exists, Func, Value, When
from django.db.models.fields import (
    CharField, DateTimeField, Field, IntegerField, UUIDField,
)
from django.db.models.query_utils import RegisterLookupMixin
from django.utils.datastructures import OrderedSet
from django.utils.deprecation import RemovedInDjango40Warning
from django.utils.functional import cached_property


class Lookup:
    lookup_name = None
    prepare_rhs = True
    can_use_none_as_rhs = False

    def __init__(self, lhs, rhs):
        """
        Initializes a new instance of the class with the given left-hand side (lhs) and right-hand side (rhs) expressions.
        
        Args:
        lhs (object): The left-hand side expression.
        rhs (object): The right-hand side expression.
        
        Attributes:
        lhs (object): The left-hand side expression.
        rhs (object): The right-hand side expression after preprocessing.
        bilateral_transforms (list): A list of bilateral transformations applied to the lhs.
        
        Raises:
        NotImplementedError
        """

        self.lhs, self.rhs = lhs, rhs
        self.rhs = self.get_prep_lookup()
        if hasattr(self.lhs, 'get_bilateral_transforms'):
            bilateral_transforms = self.lhs.get_bilateral_transforms()
        else:
            bilateral_transforms = []
        if bilateral_transforms:
            # Warn the user as soon as possible if they are trying to apply
            # a bilateral transformation on a nested QuerySet: that won't work.
            from django.db.models.sql.query import (  # avoid circular import
                Query,
            )
            if isinstance(rhs, Query):
                raise NotImplementedError("Bilateral transformations on nested querysets are not implemented.")
        self.bilateral_transforms = bilateral_transforms

    def apply_bilateral_transforms(self, value):
        """
        Apply a series of bilateral transforms to the input value.
        
        Args:
        value (Any): The input value to be transformed.
        
        Returns:
        Any: The transformed value after applying all specified bilateral transforms.
        
        This function iterates over a list of bilateral transforms (`self.bilateral_transforms`) and applies each one to the input `value`. Each transform is expected to modify the input value in some way. The final transformed value is returned.
        """

        for transform in self.bilateral_transforms:
            value = transform(value)
        return value

    def batch_process_rhs(self, compiler, connection, rhs=None):
        """
        Generates SQL queries for batch processing of right-hand side (rhs) values.
        
        This function processes a list of rhs values using bilateral transforms if applicable,
        or directly prepares the database lookups otherwise. It returns a tuple containing
        the compiled SQL queries and their corresponding parameters.
        
        Args:
        compiler (Compiler): The query compiler instance used for compiling expressions.
        connection (Connection): The database connection object.
        rhs (Optional[List]): The list of right-hand side values to process.
        """

        if rhs is None:
            rhs = self.rhs
        if self.bilateral_transforms:
            sqls, sqls_params = [], []
            for p in rhs:
                value = Value(p, output_field=self.lhs.output_field)
                value = self.apply_bilateral_transforms(value)
                value = value.resolve_expression(compiler.query)
                sql, sql_params = compiler.compile(value)
                sqls.append(sql)
                sqls_params.extend(sql_params)
        else:
            _, params = self.get_db_prep_lookup(rhs, connection)
            sqls, sqls_params = ['%s'] * len(params), params
        return sqls, sqls_params

    def get_source_expressions(self):
        """
        Retrieve the source expressions for the assignment.
        
        Args:
        None
        
        Returns:
        list: A list of expressions that are the sources of the assignment.
        - If the right-hand side (rhs) is a direct value, only the left-hand side (lhs) is returned.
        - Otherwise, both the lhs and rhs are returned.
        
        Methods Used:
        - `rhs_is_direct_value`: Determines whether the right-hand side is a direct value or not.
        """

        if self.rhs_is_direct_value():
            return [self.lhs]
        return [self.lhs, self.rhs]

    def set_source_expressions(self, new_exprs):
        """
        Sets the source expressions for the current object.
        
        Args:
        new_exprs (list): A list of expressions to be assigned as the new source expressions.
        
        Summary:
        This method updates the source expressions for the current object. If there is only one expression in the list, it assigns it to `self.lhs`. Otherwise, it assigns the first expression to `self.lhs` and the second expression to `self.rhs`.
        
        Returns:
        None
        """

        if len(new_exprs) == 1:
            self.lhs = new_exprs[0]
        else:
            self.lhs, self.rhs = new_exprs

    def get_prep_lookup(self):
        """
        Generates a prepared lookup value for database queries.
        
        This method handles the preparation of the right-hand side (rhs) of a lookup expression. It checks if the rhs is an expression that can be resolved, and if so, returns it directly. If the prepare_rhs flag is set and the lhs field has a get_prep_value method, it uses that method to prepare the rhs value. Otherwise, it returns the rhs value as is.
        
        Args:
        self: The instance of the class containing
        """

        if hasattr(self.rhs, 'resolve_expression'):
            return self.rhs
        if self.prepare_rhs and hasattr(self.lhs.output_field, 'get_prep_value'):
            return self.lhs.output_field.get_prep_value(self.rhs)
        return self.rhs

    def get_db_prep_lookup(self, value, connection):
        return ('%s', [value])

    def process_lhs(self, compiler, connection, lhs=None):
        """
        Generates a processed left-hand side (LHS) expression for database queries.
        
        Args:
        compiler (Compiler): The compiler object responsible for compiling expressions.
        connection (Connection): The database connection object.
        lhs (Optional[Expression]): The left-hand side expression to be processed. If not provided, the `self.lhs` attribute is used.
        
        Returns:
        str: The compiled LHS expression as a string.
        
        Notes:
        - If `lhs` is an instance of
        """

        lhs = lhs or self.lhs
        if hasattr(lhs, 'resolve_expression'):
            lhs = lhs.resolve_expression(compiler.query)
        return compiler.compile(lhs)

    def process_rhs(self, compiler, connection):
        """
        Processes the right-hand side (rhs) of a database lookup.
        
        This method handles the transformation and compilation of the rhs value
        based on the bilateral transforms applied to the lookup. It ensures that
        the value is properly prepared for database lookup by applying any
        necessary transformations and compiling the resulting expression.
        
        Args:
        compiler: The SQL compiler instance used for compiling expressions.
        connection: The database connection object.
        
        Returns:
        The compiled SQL representation of the rhs value or the
        """

        value = self.rhs
        if self.bilateral_transforms:
            if self.rhs_is_direct_value():
                # Do not call get_db_prep_lookup here as the value will be
                # transformed before being used for lookup
                value = Value(value, output_field=self.lhs.output_field)
            value = self.apply_bilateral_transforms(value)
            value = value.resolve_expression(compiler.query)
        if hasattr(value, 'as_sql'):
            return compiler.compile(value)
        else:
            return self.get_db_prep_lookup(value, connection)

    def rhs_is_direct_value(self):
        return not hasattr(self.rhs, 'as_sql')

    def relabeled_clone(self, relabels):
        """
        Relabels the nodes of the expression tree by applying the given relabeling dictionary to the left-hand side (LHS) and optionally the right-hand side (RHS) of the expression.
        
        Args:
        relabels (dict): A dictionary mapping old node labels to new ones.
        
        Returns:
        Expr: A new expression with relabeled nodes.
        
        Attributes:
        lhs (Expr): The left-hand side of the expression.
        rhs (Expr): The right-hand side of
        """

        new = copy(self)
        new.lhs = new.lhs.relabeled_clone(relabels)
        if hasattr(new.rhs, 'relabeled_clone'):
            new.rhs = new.rhs.relabeled_clone(relabels)
        return new

    def get_group_by_cols(self, alias=None):
        """
        Get the columns used for grouping.
        
        This method retrieves the columns used for grouping from the left-hand side (lhs) of the operation. If the right-hand side (rhs) is also a grouping operation, its columns are extended to the result. The method returns a list of columns that are used for grouping.
        
        Args:
        alias (str, optional): An alias for the resulting grouped columns. Defaults to None.
        
        Returns:
        list: A list of column names used for grouping.
        """

        cols = self.lhs.get_group_by_cols()
        if hasattr(self.rhs, 'get_group_by_cols'):
            cols.extend(self.rhs.get_group_by_cols())
        return cols

    def as_sql(self, compiler, connection):
        raise NotImplementedError

    def as_oracle(self, compiler, connection):
        """
        Wraps an EXISTS() expression in a CASE WHEN statement if necessary to ensure compatibility with Oracle's SQL syntax. The function takes an instance of a compiler and a connection object as inputs. It processes the left-hand side (lhs) and right-hand side (rhs) expressions, checking if they are instances of `Exists`. If so, it wraps them in a `Case` statement with a `When` clause that returns `True` when the `Exists` condition is met, and `False`
        """

        # Oracle doesn't allow EXISTS() to be compared to another expression
        # unless it's wrapped in a CASE WHEN.
        wrapped = False
        exprs = []
        for expr in (self.lhs, self.rhs):
            if isinstance(expr, Exists):
                expr = Case(When(expr, then=True), default=False)
                wrapped = True
            exprs.append(expr)
        lookup = type(self)(*exprs) if wrapped else self
        return lookup.as_sql(compiler, connection)

    @cached_property
    def contains_aggregate(self):
        return self.lhs.contains_aggregate or getattr(self.rhs, 'contains_aggregate', False)

    @cached_property
    def contains_over_clause(self):
        return self.lhs.contains_over_clause or getattr(self.rhs, 'contains_over_clause', False)

    @property
    def is_summary(self):
        return self.lhs.is_summary or getattr(self.rhs, 'is_summary', False)


class Transform(RegisterLookupMixin, Func):
    """
    RegisterLookupMixin() is first so that get_lookup() and get_transform()
    first examine self and then check output_field.
    """
    bilateral = False
    arity = 1

    @property
    def lhs(self):
        return self.get_source_expressions()[0]

    def get_bilateral_transforms(self):
        """
        Retrieve bilateral transforms.
        
        This method retrieves bilateral transforms from the left-hand side (lhs) object
        if available. If not, an empty list is returned. If the current object has a
        bilateral transform enabled (`self.bilateral`), it appends its class to the
        list of bilateral transforms.
        
        Args:
        None
        
        Returns:
        List[Type]: A list of classes representing bilateral transforms.
        """

        if hasattr(self.lhs, 'get_bilateral_transforms'):
            bilateral_transforms = self.lhs.get_bilateral_transforms()
        else:
            bilateral_transforms = []
        if self.bilateral:
            bilateral_transforms.append(self.__class__)
        return bilateral_transforms


class BuiltinLookup(Lookup):
    def process_lhs(self, compiler, connection, lhs=None):
        """
        Processes the left-hand side of a lookup expression.
        
        Args:
        compiler (Compiler): The SQL compiler instance.
        connection (Connection): The database connection object.
        lhs (Field, optional): The left-hand side field of the lookup. Defaults to None.
        
        Returns:
        tuple: A tuple containing the processed SQL representation of the left-hand side and a list of parameters.
        
        This method processes the left-hand side of a lookup expression by first calling the superclass's `process_lhs` method
        """

        lhs_sql, params = super().process_lhs(compiler, connection, lhs)
        field_internal_type = self.lhs.output_field.get_internal_type()
        db_type = self.lhs.output_field.db_type(connection=connection)
        lhs_sql = connection.ops.field_cast_sql(
            db_type, field_internal_type) % lhs_sql
        lhs_sql = connection.ops.lookup_cast(self.lookup_name, field_internal_type) % lhs_sql
        return lhs_sql, list(params)

    def as_sql(self, compiler, connection):
        """
        Generates an SQL query for a comparison operation.
        
        Args:
        compiler: The SQL compiler object used to generate the query.
        connection: The database connection object.
        
        Returns:
        A tuple containing the generated SQL query and a list of parameters.
        
        Process:
        1. Calls `process_lhs` method to generate the left-hand side of the comparison.
        2. Calls `process_rhs` method to generate the right-hand side of the comparison.
        3. Extends
        """

        lhs_sql, params = self.process_lhs(compiler, connection)
        rhs_sql, rhs_params = self.process_rhs(compiler, connection)
        params.extend(rhs_params)
        rhs_sql = self.get_rhs_op(connection, rhs_sql)
        return '%s %s' % (lhs_sql, rhs_sql), params

    def get_rhs_op(self, connection, rhs):
        return connection.operators[self.lookup_name] % rhs


class FieldGetDbPrepValueMixin:
    """
    Some lookups require Field.get_db_prep_value() to be called on their
    inputs.
    """
    get_db_prep_lookup_value_is_iterable = False

    def get_db_prep_lookup(self, value, connection):
        """
        Generates a database preparation lookup for a given value.
        
        This function is designed to handle relational fields by utilizing the `target_field` attribute of the output field. It prepares the value for database operations using the appropriate `get_db_prep_value` method from either the target field or the original output field.
        
        Args:
        value: The value to be prepared for database operations.
        connection: The database connection object.
        
        Returns:
        A tuple containing a SQL fragment and a list of prepared values
        """

        # For relational fields, use the 'target_field' attribute of the
        # output_field.
        field = getattr(self.lhs.output_field, 'target_field', None)
        get_db_prep_value = getattr(field, 'get_db_prep_value', None) or self.lhs.output_field.get_db_prep_value
        return (
            '%s',
            [get_db_prep_value(v, connection, prepared=True) for v in value]
            if self.get_db_prep_lookup_value_is_iterable else
            [get_db_prep_value(value, connection, prepared=True)]
        )


class FieldGetDbPrepValueIterableMixin(FieldGetDbPrepValueMixin):
    """
    Some lookups require Field.get_db_prep_value() to be called on each value
    in an iterable.
    """
    get_db_prep_lookup_value_is_iterable = True

    def get_prep_lookup(self):
        """
        Generates a prepared lookup value for database queries.
        
        This function processes the right-hand side (rhs) of a lookup expression,
        preparing it for use in database queries. It handles expressions and
        prepares values using the `get_prep_value` method of the field's output
        type.
        
        Args:
        self: The instance of the class containing the lookup expression.
        
        Returns:
        A prepared lookup value or a list of prepared values, depending on
        the input type.
        """

        if hasattr(self.rhs, 'resolve_expression'):
            return self.rhs
        prepared_values = []
        for rhs_value in self.rhs:
            if hasattr(rhs_value, 'resolve_expression'):
                # An expression will be handled by the database but can coexist
                # alongside real values.
                pass
            elif self.prepare_rhs and hasattr(self.lhs.output_field, 'get_prep_value'):
                rhs_value = self.lhs.output_field.get_prep_value(rhs_value)
            prepared_values.append(rhs_value)
        return prepared_values

    def process_rhs(self, compiler, connection):
        """
        Processes the right-hand side (rhs) of a query.
        
        This method handles the processing of the right-hand side of a query
        based on whether the rhs is a direct value or not. If the rhs is a
        direct value, it uses `batch_process_rhs` to prepare and transform
        those values. Otherwise, it delegates the processing to the superclass's
        `process_rhs` method.
        
        Args:
        compiler: The database query compiler instance.
        connection: The
        """

        if self.rhs_is_direct_value():
            # rhs should be an iterable of values. Use batch_process_rhs()
            # to prepare/transform those values.
            return self.batch_process_rhs(compiler, connection)
        else:
            return super().process_rhs(compiler, connection)

    def resolve_expression_parameter(self, compiler, connection, sql, param):
        """
        Resolves an expression parameter for SQL compilation.
        
        This function takes a parameter and resolves its expression using the
        provided compiler and query. It then compiles the resolved parameter into
        SQL and returns the resulting SQL string along with any additional parameters
        required for execution.
        
        Args:
        compiler (Compiler): The compiler instance used for SQL compilation.
        connection (Connection): The database connection object.
        sql (str): The initial SQL string.
        param: The parameter to be resolved
        """

        params = [param]
        if hasattr(param, 'resolve_expression'):
            param = param.resolve_expression(compiler.query)
        if hasattr(param, 'as_sql'):
            sql, params = compiler.compile(param)
        return sql, params

    def batch_process_rhs(self, compiler, connection, rhs=None):
        """
        Batch processes the right-hand side (rhs) of a query using the provided compiler and connection.
        
        Args:
        compiler: The database compiler instance used for SQL compilation.
        connection: The database connection object.
        rhs: The right-hand side expression or expressions to be processed.
        
        Returns:
        A tuple containing the compiled SQL query and a flattened tuple of parameters.
        
        Summary:
        This method first calls the superclass's `batch_process_rhs` method to process the rhs. It then iterates
        """

        pre_processed = super().batch_process_rhs(compiler, connection, rhs)
        # The params list may contain expressions which compile to a
        # sql/param pair. Zip them to get sql and param pairs that refer to the
        # same argument and attempt to replace them with the result of
        # compiling the param step.
        sql, params = zip(*(
            self.resolve_expression_parameter(compiler, connection, sql, param)
            for sql, param in zip(*pre_processed)
        ))
        params = itertools.chain.from_iterable(params)
        return sql, tuple(params)


class PostgresOperatorLookup(FieldGetDbPrepValueMixin, Lookup):
    """Lookup defined by operators on PostgreSQL."""
    postgres_operator = None

    def as_postgresql(self, compiler, connection):
        """
        Generates a PostgreSQL query based on the given compiler and connection.
        
        Args:
        compiler: The compiler object used to process the left-hand side of the query.
        connection: The database connection object used to process the right-hand side of the query.
        
        Returns:
        A tuple containing the generated PostgreSQL query string and a list of parameters.
        
        Process:
        1. Processes the left-hand side of the query using the provided compiler and connection.
        2. Processes the right-hand side
        """

        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = tuple(lhs_params) + tuple(rhs_params)
        return '%s %s %s' % (lhs, self.postgres_operator, rhs), params


@Field.register_lookup
class Exact(FieldGetDbPrepValueMixin, BuiltinLookup):
    lookup_name = 'exact'

    def process_rhs(self, compiler, connection):
        """
        Processes the right-hand side (rhs) of a query.
        
        Args:
        compiler: The SQL compiler instance.
        connection: The database connection object.
        
        Returns:
        The processed rhs value.
        
        Notes:
        - If the rhs is an instance of `django.db.models.sql.query.Query`, checks if it has a limit of one.
        - If the limit is one and no select fields are specified, clears the select clause and adds 'pk' as a field.
        - If the
        """

        from django.db.models.sql.query import Query
        if isinstance(self.rhs, Query):
            if self.rhs.has_limit_one():
                if not self.rhs.has_select_fields:
                    self.rhs.clear_select_clause()
                    self.rhs.add_fields(['pk'])
            else:
                raise ValueError(
                    'The QuerySet value for an exact lookup must be limited to '
                    'one result using slicing.'
                )
        return super().process_rhs(compiler, connection)

    def as_sql(self, compiler, connection):
        """
        Generates SQL for the given query part.
        
        Args:
        compiler (sql.compiler.SQLCompiler): The SQL compiler instance.
        connection (django.db.backends.base.base.BaseDatabaseWrapper): The database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL and parameters.
        
        Summary:
        This function generates SQL for a given query part. It checks if the right-hand side (rhs) is a boolean value and the left-hand side (lhs) is a conditional expression that supports being
        """

        # Avoid comparison against direct rhs if lhs is a boolean value. That
        # turns "boolfield__exact=True" into "WHERE boolean_field" instead of
        # "WHERE boolean_field = True" when allowed.
        if (
            isinstance(self.rhs, bool) and
            getattr(self.lhs, 'conditional', False) and
            connection.ops.conditional_expression_supported_in_where_clause(self.lhs)
        ):
            lhs_sql, params = self.process_lhs(compiler, connection)
            template = '%s' if self.rhs else 'NOT %s'
            return template % lhs_sql, params
        return super().as_sql(compiler, connection)


@Field.register_lookup
class IExact(BuiltinLookup):
    lookup_name = 'iexact'
    prepare_rhs = False

    def process_rhs(self, qn, connection):
        """
        Processes the right-hand side (rhs) of a query.
        
        Args:
        qn: The quoted name of the field.
        connection: The database connection object.
        
        Returns:
        A tuple containing the processed rhs and parameters.
        
        This method extends the functionality of the base class by modifying the parameters before returning them. If parameters are present, the first parameter is prepared for an iexact query using the `prep_for_iexact_query` method from the connection's operations.
        """

        rhs, params = super().process_rhs(qn, connection)
        if params:
            params[0] = connection.ops.prep_for_iexact_query(params[0])
        return rhs, params


@Field.register_lookup
class GreaterThan(FieldGetDbPrepValueMixin, BuiltinLookup):
    lookup_name = 'gt'


@Field.register_lookup
class GreaterThanOrEqual(FieldGetDbPrepValueMixin, BuiltinLookup):
    lookup_name = 'gte'


@Field.register_lookup
class LessThan(FieldGetDbPrepValueMixin, BuiltinLookup):
    lookup_name = 'lt'


@Field.register_lookup
class LessThanOrEqual(FieldGetDbPrepValueMixin, BuiltinLookup):
    lookup_name = 'lte'


class IntegerFieldFloatRounding:
    """
    Allow floats to work as query values for IntegerField. Without this, the
    decimal portion of the float would always be discarded.
    """
    def get_prep_lookup(self):
        """
        Ceil the right-hand side (rhs) value if it is a float, then prepare the lookup using the superclass's implementation of get_prep_lookup.
        
        Args:
        None
        
        Returns:
        The prepared lookup value after potentially ceilling the rhs.
        
        Important Functions:
        - math.ceil: Used to round up the rhs value if it is a float.
        - super().get_prep_lookup: Calls the superclass's implementation of get_prep_lookup to prepare the lookup.
        
        Notes:
        This
        """

        if isinstance(self.rhs, float):
            self.rhs = math.ceil(self.rhs)
        return super().get_prep_lookup()


@IntegerField.register_lookup
class IntegerGreaterThanOrEqual(IntegerFieldFloatRounding, GreaterThanOrEqual):
    pass


@IntegerField.register_lookup
class IntegerLessThan(IntegerFieldFloatRounding, LessThan):
    pass


@Field.register_lookup
class In(FieldGetDbPrepValueIterableMixin, BuiltinLookup):
    lookup_name = 'in'

    def process_rhs(self, compiler, connection):
        """
        Processes the right-hand side (rhs) of a query.
        
        Args:
        compiler (BaseDatabaseCompiler): The database compiler instance.
        connection (Connection): The database connection object.
        
        Returns:
        tuple: A tuple containing the processed SQL placeholder and parameters.
        
        Raises:
        ValueError: If the subquery involves multiple databases.
        EmptyResultSet: If the right-hand side is empty after removing None values.
        
        Summary:
        This function processes the right-hand side of a query by checking if
        """

        db_rhs = getattr(self.rhs, '_db', None)
        if db_rhs is not None and db_rhs != connection.alias:
            raise ValueError(
                "Subqueries aren't allowed across different databases. Force "
                "the inner query to be evaluated using `list(inner_query)`."
            )

        if self.rhs_is_direct_value():
            # Remove None from the list as NULL is never equal to anything.
            try:
                rhs = OrderedSet(self.rhs)
                rhs.discard(None)
            except TypeError:  # Unhashable items in self.rhs
                rhs = [r for r in self.rhs if r is not None]

            if not rhs:
                raise EmptyResultSet

            # rhs should be an iterable; use batch_process_rhs() to
            # prepare/transform those values.
            sqls, sqls_params = self.batch_process_rhs(compiler, connection, rhs)
            placeholder = '(' + ', '.join(sqls) + ')'
            return (placeholder, sqls_params)
        else:
            if not getattr(self.rhs, 'has_select_fields', True):
                self.rhs.clear_select_clause()
                self.rhs.add_fields(['pk'])
            return super().process_rhs(compiler, connection)

    def get_rhs_op(self, connection, rhs):
        return 'IN %s' % rhs

    def as_sql(self, compiler, connection):
        """
        Generates SQL for the given query parameter.
        
        Args:
        compiler: The SQL compiler instance.
        connection: The database connection object.
        
        Returns:
        The generated SQL string.
        
        This method checks if the right-hand side (rhs) of the query is a direct value and if the maximum allowed size for IN list is defined in the connection's operations. If the length of the rhs exceeds this maximum size, it splits the parameter list using `split_parameter_list_as_sql`. Otherwise, it
        """

        max_in_list_size = connection.ops.max_in_list_size()
        if self.rhs_is_direct_value() and max_in_list_size and len(self.rhs) > max_in_list_size:
            return self.split_parameter_list_as_sql(compiler, connection)
        return super().as_sql(compiler, connection)

    def split_parameter_list_as_sql(self, compiler, connection):
        """
        Splits a parameter list into smaller chunks to handle large 'IN' clauses.
        
        Args:
        compiler (compiler object): The SQL compiler instance.
        connection (connection object): The database connection object.
        
        Returns:
        tuple: A tuple containing the modified SQL query and the updated parameters.
        
        Important Functions:
        - `process_lhs`: Processes the left-hand side of the query.
        - `batch_process_rhs`: Processes the right-hand side of the query in batches.
        - `max
        """

        # This is a special case for databases which limit the number of
        # elements which can appear in an 'IN' clause.
        max_in_list_size = connection.ops.max_in_list_size()
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.batch_process_rhs(compiler, connection)
        in_clause_elements = ['(']
        params = []
        for offset in range(0, len(rhs_params), max_in_list_size):
            if offset > 0:
                in_clause_elements.append(' OR ')
            in_clause_elements.append('%s IN (' % lhs)
            params.extend(lhs_params)
            sqls = rhs[offset: offset + max_in_list_size]
            sqls_params = rhs_params[offset: offset + max_in_list_size]
            param_group = ', '.join(sqls)
            in_clause_elements.append(param_group)
            in_clause_elements.append(')')
            params.extend(sqls_params)
        in_clause_elements.append(')')
        return ''.join(in_clause_elements), params


class PatternLookup(BuiltinLookup):
    param_pattern = '%%%s%%'
    prepare_rhs = False

    def get_rhs_op(self, connection, rhs):
        """
        Generates an SQL-like right-hand side operation for a given connection and right-hand side value.
        
        Args:
        connection: The database connection object.
        rhs: The right-hand side value to be formatted into an SQL pattern.
        
        Returns:
        A formatted string representing the SQL pattern for the right-hand side value.
        
        Notes:
        - If `rhs` has an `as_sql` method or if bilateral transforms are applied, the function formats the right-hand side value using the specified pattern operation
        """

        # Assume we are in startswith. We need to produce SQL like:
        #     col LIKE %s, ['thevalue%']
        # For python values we can (and should) do that directly in Python,
        # but if the value is for example reference to other column, then
        # we need to add the % pattern match to the lookup by something like
        #     col LIKE othercol || '%%'
        # So, for Python values we don't need any special pattern, but for
        # SQL reference values or SQL transformations we need the correct
        # pattern added.
        if hasattr(self.rhs, 'as_sql') or self.bilateral_transforms:
            pattern = connection.pattern_ops[self.lookup_name].format(connection.pattern_esc)
            return pattern.format(rhs)
        else:
            return super().get_rhs_op(connection, rhs)

    def process_rhs(self, qn, connection):
        """
        Processes the right-hand side (rhs) of a query.
        
        Args:
        qn: The name of the query node.
        connection: The database connection object.
        
        Returns:
        A tuple containing the processed rhs and parameters.
        
        Summary:
        This method processes the rhs of a query by calling the superclass's
        `process_rhs` method. If the rhs is a direct value, parameters are present,
        and there are no bilateral transforms, it prepares the first parameter for
        """

        rhs, params = super().process_rhs(qn, connection)
        if self.rhs_is_direct_value() and params and not self.bilateral_transforms:
            params[0] = self.param_pattern % connection.ops.prep_for_like_query(params[0])
        return rhs, params


@Field.register_lookup
class Contains(PatternLookup):
    lookup_name = 'contains'


@Field.register_lookup
class IContains(Contains):
    lookup_name = 'icontains'


@Field.register_lookup
class StartsWith(PatternLookup):
    lookup_name = 'startswith'
    param_pattern = '%s%%'


@Field.register_lookup
class IStartsWith(StartsWith):
    lookup_name = 'istartswith'


@Field.register_lookup
class EndsWith(PatternLookup):
    lookup_name = 'endswith'
    param_pattern = '%%%s'


@Field.register_lookup
class IEndsWith(EndsWith):
    lookup_name = 'iendswith'


@Field.register_lookup
class Range(FieldGetDbPrepValueIterableMixin, BuiltinLookup):
    lookup_name = 'range'

    def get_rhs_op(self, connection, rhs):
        return "BETWEEN %s AND %s" % (rhs[0], rhs[1])


@Field.register_lookup
class IsNull(BuiltinLookup):
    lookup_name = 'isnull'
    prepare_rhs = False

    def as_sql(self, compiler, connection):
        """
        Generates SQL for an isnull lookup.
        
        Args:
        compiler (Compiler): The compiler object used to compile the left-hand side of the lookup.
        connection (Connection): The database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL query and parameters.
        
        Raises:
        RemovedInDjango40Warning: If a non-boolean value is used for the rhs parameter.
        
        Summary:
        This function generates SQL for an isnull lookup by compiling the left-hand
        """

        if not isinstance(self.rhs, bool):
            # When the deprecation ends, replace with:
            # raise ValueError(
            #     'The QuerySet value for an isnull lookup must be True or '
            #     'False.'
            # )
            warnings.warn(
                'Using a non-boolean value for an isnull lookup is '
                'deprecated, use True or False instead.',
                RemovedInDjango40Warning,
            )
        sql, params = compiler.compile(self.lhs)
        if self.rhs:
            return "%s IS NULL" % sql, params
        else:
            return "%s IS NOT NULL" % sql, params


@Field.register_lookup
class Regex(BuiltinLookup):
    lookup_name = 'regex'
    prepare_rhs = False

    def as_sql(self, compiler, connection):
        """
        Generates SQL for a regex lookup.
        
        This function processes the left-hand side (lhs) and right-hand side (rhs) of a
        regex lookup using the provided compiler and connection. If the lookup name is
        not found in the connection's operators, it falls back to a generic regex
        operation. The resulting SQL template is then formatted with the processed lhs
        and rhs, and combined with any parameters generated during processing.
        
        Args:
        compiler: The SQL compiler instance
        """

        if self.lookup_name in connection.operators:
            return super().as_sql(compiler, connection)
        else:
            lhs, lhs_params = self.process_lhs(compiler, connection)
            rhs, rhs_params = self.process_rhs(compiler, connection)
            sql_template = connection.ops.regex_lookup(self.lookup_name)
            return sql_template % (lhs, rhs), lhs_params + rhs_params


@Field.register_lookup
class IRegex(Regex):
    lookup_name = 'iregex'


class YearLookup(Lookup):
    def year_lookup_bounds(self, connection, year):
        """
        Looks up the lower and upper bounds for a given year in the database.
        
        Args:
        connection (DatabaseWrapper): The database connection object.
        year (int): The year to look up bounds for.
        
        Returns:
        tuple: A tuple containing the lower and upper bounds for the specified year.
        
        Notes:
        - The function determines whether the output field is a `DateTimeField` or a `DateField`.
        - Depending on the type of the output field, it calls either `
        """

        output_field = self.lhs.lhs.output_field
        if isinstance(output_field, DateTimeField):
            bounds = connection.ops.year_lookup_bounds_for_datetime_field(year)
        else:
            bounds = connection.ops.year_lookup_bounds_for_date_field(year)
        return bounds

    def as_sql(self, compiler, connection):
        """
        Generates SQL for the 'year' lookup.
        
        This method handles the generation of SQL for filtering based on the year
        of a date or datetime field. It takes into account whether the right-hand
        side (rhs) of the comparison is a direct value or an expression, and
        processes the left-hand side (lhs) accordingly. If the rhs is a direct
        value, it avoids the `extract` operation to optimize the query and allows
        the use of indexes
        """

        # Avoid the extract operation if the rhs is a direct value to allow
        # indexes to be used.
        if self.rhs_is_direct_value():
            # Skip the extract part by directly using the originating field,
            # that is self.lhs.lhs.
            lhs_sql, params = self.process_lhs(compiler, connection, self.lhs.lhs)
            rhs_sql, _ = self.process_rhs(compiler, connection)
            rhs_sql = self.get_direct_rhs_sql(connection, rhs_sql)
            start, finish = self.year_lookup_bounds(connection, self.rhs)
            params.extend(self.get_bound_params(start, finish))
            return '%s %s' % (lhs_sql, rhs_sql), params
        return super().as_sql(compiler, connection)

    def get_direct_rhs_sql(self, connection, rhs):
        return connection.operators[self.lookup_name] % rhs

    def get_bound_params(self, start, finish):
        """
        Generates boundary parameters for a date range.
        
        This method should be overridden by subclasses of YearLookup to provide specific logic for determining the start and finish parameters for a date range query.
        
        Args:
        start (datetime.date): The start date of the range.
        finish (datetime.date): The end date of the range.
        
        Raises:
        NotImplementedError: If the method is not overridden in a subclass.
        """

        raise NotImplementedError(
            'subclasses of YearLookup must provide a get_bound_params() method'
        )


class YearExact(YearLookup, Exact):
    def get_direct_rhs_sql(self, connection, rhs):
        return 'BETWEEN %s AND %s'

    def get_bound_params(self, start, finish):
        return (start, finish)


class YearGt(YearLookup, GreaterThan):
    def get_bound_params(self, start, finish):
        return (finish,)


class YearGte(YearLookup, GreaterThanOrEqual):
    def get_bound_params(self, start, finish):
        return (start,)


class YearLt(YearLookup, LessThan):
    def get_bound_params(self, start, finish):
        return (start,)


class YearLte(YearLookup, LessThanOrEqual):
    def get_bound_params(self, start, finish):
        return (finish,)


class UUIDTextMixin:
    """
    Strip hyphens from a value when filtering a UUIDField on backends without
    a native datatype for UUID.
    """
    def process_rhs(self, qn, connection):
        """
        Processes the right-hand side (RHS) of a query expression.
        
        Args:
        qn: The quoting function for the database backend.
        connection: The database connection object.
        
        Returns:
        A tuple containing the processed RHS and parameters.
        
        Notes:
        - If the database does not support native UUID fields, this function replaces hyphens ('-') with an empty string using the `Replace` function from Django's `models.functions`.
        - If the RHS is a direct value
        """

        if not connection.features.has_native_uuid_field:
            from django.db.models.functions import Replace
            if self.rhs_is_direct_value():
                self.rhs = Value(self.rhs)
            self.rhs = Replace(self.rhs, Value('-'), Value(''), output_field=CharField())
        rhs, params = super().process_rhs(qn, connection)
        return rhs, params


@UUIDField.register_lookup
class UUIDIExact(UUIDTextMixin, IExact):
    pass


@UUIDField.register_lookup
class UUIDContains(UUIDTextMixin, Contains):
    pass


@UUIDField.register_lookup
class UUIDIContains(UUIDTextMixin, IContains):
    pass


@UUIDField.register_lookup
class UUIDStartsWith(UUIDTextMixin, StartsWith):
    pass


@UUIDField.register_lookup
class UUIDIStartsWith(UUIDTextMixin, IStartsWith):
    pass


@UUIDField.register_lookup
class UUIDEndsWith(UUIDTextMixin, EndsWith):
    pass


@UUIDField.register_lookup
class UUIDIEndsWith(UUIDTextMixin, IEndsWith):
    pass
