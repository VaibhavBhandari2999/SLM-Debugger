from django.db.backends.ddl_references import Statement, Table
from django.db.models import F, Q
from django.db.models.constraints import BaseConstraint
from django.db.models.sql import Query

__all__ = ['ExclusionConstraint']


class ExclusionConstraint(BaseConstraint):
    template = 'CONSTRAINT %(name)s EXCLUDE USING %(index_type)s (%(expressions)s)%(where)s'

    def __init__(self, *, name, expressions, index_type=None, condition=None):
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
        """
        Generate SQL expressions for a query.
        
        This function is used to generate SQL expressions for a given query. It iterates over a list of expressions and their corresponding operators. Each expression is resolved and its SQL representation is obtained using the provided compiler and connection. The function returns a list of formatted SQL expressions.
        
        Parameters:
        compiler (object): The compiler object used to generate SQL.
        connection (object): The database connection object.
        query (object): The query object containing the expressions to be resolved.
        """

        expressions = []
        for expression, operator in self.expressions:
            if isinstance(expression, str):
                expression = F(expression)
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
        
        This function creates a SQL constraint for a Django model based on the provided query and compiler. The constraint is formatted according to the specified template.
        
        Parameters:
        model (django.db.models.Model): The Django model for which the constraint is being generated.
        schema_editor (django.db.backends.base.schema.BaseSchemaEditor): The schema editor used to execute the constraint.
        
        Returns:
        str: A string containing the SQL constraint.
        
        Key Components:
        - `express
        """

        query = Query(model, alias_cols=False)
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
        path, args, kwargs = super().deconstruct()
        kwargs['expressions'] = self.expressions
        if self.condition is not None:
            kwargs['condition'] = self.condition
        if self.index_type.lower() != 'gist':
            kwargs['index_type'] = self.index_type
        return path, args, kwargs

    def __eq__(self, other):
        """
        Compare two Index objects for equality.
        
        This method checks if two Index objects are equal by comparing their attributes:
        - `name`: The name of the index.
        - `index_type`: The type of the index.
        - `expressions`: The expressions defining the index.
        - `condition`: The condition associated with the index.
        
        Parameters:
        other (Index): The other Index object to compare with.
        
        Returns:
        bool: True if both objects have the same `name`, `index_type`, `express
        """

        if isinstance(other, self.__class__):
            return (
                self.name == other.name and
                self.index_type == other.index_type and
                self.expressions == other.expressions and
                self.condition == other.condition
            )
        return super().__eq__(other)

    def __repr__(self):
        return '<%s: index_type=%s, expressions=%s%s>' % (
            self.__class__.__qualname__,
            self.index_type,
            self.expressions,
            '' if self.condition is None else ', condition=%s' % self.condition,
        )
ex_type'] = self.index_type
        return path, args, kwargs

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.name == other.name and
                self.index_type == other.index_type and
                self.expressions == other.expressions and
                self.condition == other.condition
            )
        return super().__eq__(other)

    def __repr__(self):
        return '<%s: index_type=%s, expressions=%s%s>' % (
            self.__class__.__qualname__,
            self.index_type,
            self.expressions,
            '' if self.condition is None else ', condition=%s' % self.condition,
        )
