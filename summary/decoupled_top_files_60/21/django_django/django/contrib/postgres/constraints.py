from django.db.backends.ddl_references import Statement, Table
from django.db.models import F, Q
from django.db.models.constraints import BaseConstraint
from django.db.models.sql import Query

__all__ = ['ExclusionConstraint']


class ExclusionConstraint(BaseConstraint):
    template = 'CONSTRAINT %(name)s EXCLUDE USING %(index_type)s (%(expressions)s)%(where)s'

    def __init__(self, *, name, expressions, index_type=None, condition=None):
        """
        Initialize an ExclusionConstraint object.
        
        Args:
        name (str): The name of the exclusion constraint.
        expressions (list): A list of 2-tuples defining the expressions for the
        constraint. Each tuple should contain two elements.
        index_type (str, optional): The type of index to use for the constraint.
        Must be either 'gist' or 'spgist'. Defaults to 'GIST'.
        condition (Q, optional): A condition to apply to the constraint.
        """

        if index_type and index_type.lower() not in {'gist', 'spgist'}:
            raise ValueError(
                'Exclusion constraints only support GiST or SP-GiST indexes.'
            )
        if not expressions:
            raise ValueError(
                'At least one expression is required to define an exclusion '
                'constraint.'
            )
        if not all(
            isinstance(expr, (list, tuple)) and len(expr) == 2
            for expr in expressions
        ):
            raise ValueError('The expressions must be a list of 2-tuples.')
        if not isinstance(condition, (type(None), Q)):
            raise ValueError(
                'ExclusionConstraint.condition must be a Q instance.'
            )
        self.expressions = expressions
        self.index_type = index_type or 'GIST'
        self.condition = condition
        super().__init__(name=name)

    def _get_expression_sql(self, compiler, connection, query):
        expressions = []
        for expression, operator in self.expressions:
            if isinstance(expression, str):
                expression = F(expression)
            if isinstance(expression, F):
                expression = expression.resolve_expression(query=query, simple_col=True)
            else:
                expression = expression.resolve_expression(query=query)
            sql, params = expression.as_sql(compiler, connection)
            expressions.append('%s WITH %s' % (sql % params, operator))
        return expressions

    def _get_condition_sql(self, compiler, schema_editor, query):
        if self.condition is None:
            return None
        where = query.build_where(self.condition)
        sql, params = where.as_sql(compiler, schema_editor.connection)
        return sql % tuple(schema_editor.quote_value(p) for p in params)

    def constraint_sql(self, model, schema_editor):
        """
        Generates a SQL constraint for a Django model.
        
        This function constructs a SQL constraint for a Django model based on the provided query and compiler. The constraint is formatted according to the specified template.
        
        Parameters:
        model (django.db.models.Model): The Django model for which the constraint is being generated.
        schema_editor (django.db.backends.base.schema.BaseSchemaEditor): The schema editor used to execute the constraint.
        
        Returns:
        str: A string containing the SQL constraint.
        
        Key Components:
        - `express
        """

        query = Query(model)
        compiler = query.get_compiler(connection=schema_editor.connection)
        expressions = self._get_expression_sql(compiler, schema_editor.connection, query)
        condition = self._get_condition_sql(compiler, schema_editor, query)
        return self.template % {
            'name': schema_editor.quote_name(self.name),
            'index_type': self.index_type,
            'expressions': ', '.join(expressions),
            'where': ' WHERE (%s)' % condition if condition else '',
        }

    def create_sql(self, model, schema_editor):
        return Statement(
            'ALTER TABLE %(table)s ADD %(constraint)s',
            table=Table(model._meta.db_table, schema_editor.quote_name),
            constraint=self.constraint_sql(model, schema_editor),
        )

    def remove_sql(self, model, schema_editor):
        return schema_editor._delete_constraint_sql(
            schema_editor.sql_delete_check,
            model,
            schema_editor.quote_name(self.name),
        )

    def deconstruct(self):
        """
        Deconstructs the current object into its component parts for serialization or migration purposes.
        
        This method is used to break down the object into a path, arguments, and keyword arguments that can be used to reconstruct the object later.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the path to the object's class, a list of positional arguments, and a dictionary of keyword arguments. The keyword arguments include 'expressions', 'condition', and 'index_type' if they are set.
        
        Key
        """

        path, args, kwargs = super().deconstruct()
        kwargs['expressions'] = self.expressions
        if self.condition is not None:
            kwargs['condition'] = self.condition
        if self.index_type.lower() != 'gist':
            kwargs['index_type'] = self.index_type
        return path, args, kwargs

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.name == other.name and
            self.index_type == other.index_type and
            self.expressions == other.expressions and
            self.condition == other.condition
        )

    def __repr__(self):
        return '<%s: index_type=%s, expressions=%s%s>' % (
            self.__class__.__qualname__,
            self.index_type,
            self.expressions,
            '' if self.condition is None else ', condition=%s' % self.condition,
        )

        )
