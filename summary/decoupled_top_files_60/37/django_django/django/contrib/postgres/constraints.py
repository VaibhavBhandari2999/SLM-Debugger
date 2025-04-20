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
        Must be either 'GIST' or 'SP-GiST'. Defaults to 'GIST'.
        condition (Q, optional): A condition that must be
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
            expression = expression.resolve_expression(query=query)
            sql, params = expression.as_sql(compiler, connection)
            expressions.append('%s WITH %s' % (sql % params, operator))
        return expressions

    def _get_condition_sql(self, compiler, schema_editor, query):
        """
        Generates the SQL condition for a database query.
        
        This function is used to generate the SQL condition for a database query based on a given condition. It is typically used in the context of a database ORM (Object-Relational Mapping) to dynamically build SQL queries.
        
        Parameters:
        compiler (Compiler): The compiler object responsible for generating SQL.
        schema_editor (SchemaEditor): The schema editor object used to quote values.
        query (Query): The query object containing the condition to be translated into SQL
        """

        if self.condition is None:
            return None
        where = query.build_where(self.condition)
        sql, params = where.as_sql(compiler, schema_editor.connection)
        return sql % tuple(schema_editor.quote_value(p) for p in params)

    def constraint_sql(self, model, schema_editor):
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
        """
        Generates an SQL statement to add a constraint to an existing table.
        
        This function is used to dynamically create an SQL ALTER TABLE statement that adds a constraint to a specified table in a database. The generated SQL statement is intended to be executed by a database schema editor.
        
        Parameters:
        model (django.db.models.Model): The Django model class that corresponds to the table being modified.
        schema_editor (django.db.migrations.operations.base.SchemaEditor): An instance of a schema editor that provides methods to interact with
        """

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
