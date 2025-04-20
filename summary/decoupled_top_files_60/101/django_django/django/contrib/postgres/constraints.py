import warnings

from django.contrib.postgres.indexes import OpClass
from django.core.exceptions import ValidationError
from django.db import DEFAULT_DB_ALIAS, NotSupportedError
from django.db.backends.ddl_references import Expressions, Statement, Table
from django.db.models import BaseConstraint, Deferrable, F, Q
from django.db.models.expressions import Exists, ExpressionList
from django.db.models.indexes import IndexExpression
from django.db.models.lookups import PostgresOperatorLookup
from django.db.models.sql import Query
from django.utils.deprecation import RemovedInDjango50Warning

__all__ = ["ExclusionConstraint"]


class ExclusionConstraintExpression(IndexExpression):
    template = "%(expressions)s WITH %(operator)s"


class ExclusionConstraint(BaseConstraint):
    template = (
        "CONSTRAINT %(name)s EXCLUDE USING %(index_type)s "
        "(%(expressions)s)%(include)s%(where)s%(deferrable)s"
    )

    def __init__(
        self,
        *,
        name,
        expressions,
        index_type=None,
        condition=None,
        deferrable=None,
        include=None,
        opclasses=(),
        violation_error_message=None,
    ):
        if index_type and index_type.lower() not in {"gist", "spgist"}:
            raise ValueError(
                "Exclusion constraints only support GiST or SP-GiST indexes."
            )
        if not expressions:
            raise ValueError(
                "At least one expression is required to define an exclusion "
                "constraint."
            )
        if not all(
            isinstance(expr, (list, tuple)) and len(expr) == 2 for expr in expressions
        ):
            raise ValueError("The expressions must be a list of 2-tuples.")
        if not isinstance(condition, (type(None), Q)):
            raise ValueError("ExclusionConstraint.condition must be a Q instance.")
        if condition and deferrable:
            raise ValueError("ExclusionConstraint with conditions cannot be deferred.")
        if not isinstance(deferrable, (type(None), Deferrable)):
            raise ValueError(
                "ExclusionConstraint.deferrable must be a Deferrable instance."
            )
        if not isinstance(include, (type(None), list, tuple)):
            raise ValueError("ExclusionConstraint.include must be a list or tuple.")
        if not isinstance(opclasses, (list, tuple)):
            raise ValueError("ExclusionConstraint.opclasses must be a list or tuple.")
        if opclasses and len(expressions) != len(opclasses):
            raise ValueError(
                "ExclusionConstraint.expressions and "
                "ExclusionConstraint.opclasses must have the same number of "
                "elements."
            )
        self.expressions = expressions
        self.index_type = index_type or "GIST"
        self.condition = condition
        self.deferrable = deferrable
        self.include = tuple(include) if include else ()
        self.opclasses = opclasses
        if self.opclasses:
            warnings.warn(
                "The opclasses argument is deprecated in favor of using "
                "django.contrib.postgres.indexes.OpClass in "
                "ExclusionConstraint.expressions.",
                category=RemovedInDjango50Warning,
                stacklevel=2,
            )
        super().__init__(name=name, violation_error_message=violation_error_message)

    def _get_expressions(self, schema_editor, query):
        """
        Generates a list of expressions for an exclusion constraint.
        
        This function processes a list of expressions and operators to create a list of `ExclusionConstraintExpression` objects. Each expression can be a string or a Django `F` expression. The function also sets wrapper classes for the expressions based on the database connection.
        
        Parameters:
        schema_editor (SchemaEditor): The schema editor object used to set wrapper classes for the expressions.
        query (Query): The query object containing the expressions and operators.
        
        Returns:
        """

        expressions = []
        for idx, (expression, operator) in enumerate(self.expressions):
            if isinstance(expression, str):
                expression = F(expression)
            try:
                expression = OpClass(expression, self.opclasses[idx])
            except IndexError:
                pass
            expression = ExclusionConstraintExpression(expression, operator=operator)
            expression.set_wrapper_classes(schema_editor.connection)
            expressions.append(expression)
        return ExpressionList(*expressions).resolve_expression(query)

    def _get_condition_sql(self, compiler, schema_editor, query):
        if self.condition is None:
            return None
        where = query.build_where(self.condition)
        sql, params = where.as_sql(compiler, schema_editor.connection)
        return sql % tuple(schema_editor.quote_value(p) for p in params)

    def constraint_sql(self, model, schema_editor):
        """
        Generates a SQL constraint for a Django model.
        
        This function creates a SQL constraint for a Django model based on the provided parameters. It compiles the constraint using the given schema editor and query compiler.
        
        Parameters:
        model (django.db.models.Model): The Django model for which the constraint is being created.
        schema_editor (django.db.backends.base.schema.BaseSchemaEditor): The schema editor used to create the constraint.
        
        Returns:
        Statement: A Statement object containing the SQL constraint and related parameters.
        
        Key
        """

        query = Query(model, alias_cols=False)
        compiler = query.get_compiler(connection=schema_editor.connection)
        expressions = self._get_expressions(schema_editor, query)
        table = model._meta.db_table
        condition = self._get_condition_sql(compiler, schema_editor, query)
        include = [
            model._meta.get_field(field_name).column for field_name in self.include
        ]
        return Statement(
            self.template,
            table=Table(table, schema_editor.quote_name),
            name=schema_editor.quote_name(self.name),
            index_type=self.index_type,
            expressions=Expressions(
                table, expressions, compiler, schema_editor.quote_value
            ),
            where=" WHERE (%s)" % condition if condition else "",
            include=schema_editor._index_include_sql(model, include),
            deferrable=schema_editor._deferrable_constraint_sql(self.deferrable),
        )

    def create_sql(self, model, schema_editor):
        self.check_supported(schema_editor)
        return Statement(
            "ALTER TABLE %(table)s ADD %(constraint)s",
            table=Table(model._meta.db_table, schema_editor.quote_name),
            constraint=self.constraint_sql(model, schema_editor),
        )

    def remove_sql(self, model, schema_editor):
        """
        Removes a specific constraint from a model.
        
        This function is used to delete a constraint from a model using the schema editor.
        
        Parameters:
        model (django.db.models.base.ModelBase): The model from which the constraint will be removed.
        schema_editor (django.db.backends.base.schema.BaseSchemaEditor): The schema editor object that provides the necessary SQL commands.
        
        Returns:
        list: A list of SQL statements required to remove the constraint.
        
        Note:
        This function is typically used in the context of database
        """

        return schema_editor._delete_constraint_sql(
            schema_editor.sql_delete_check,
            model,
            schema_editor.quote_name(self.name),
        )

    def check_supported(self, schema_editor):
        if (
            self.include
            and self.index_type.lower() == "spgist"
            and not schema_editor.connection.features.supports_covering_spgist_indexes
        ):
            raise NotSupportedError(
                "Covering exclusion constraints using an SP-GiST index "
                "require PostgreSQL 14+."
            )

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs["expressions"] = self.expressions
        if self.condition is not None:
            kwargs["condition"] = self.condition
        if self.index_type.lower() != "gist":
            kwargs["index_type"] = self.index_type
        if self.deferrable:
            kwargs["deferrable"] = self.deferrable
        if self.include:
            kwargs["include"] = self.include
        if self.opclasses:
            kwargs["opclasses"] = self.opclasses
        return path, args, kwargs

    def __eq__(self, other):
        """
        Compares two Index objects for equality.
        
        This method checks if two Index objects are equal by comparing their attributes:
        - `name`: The name of the index.
        - `index_type`: The type of the index.
        - `expressions`: The expressions used in the index.
        - `condition`: The condition applied to the index.
        - `deferrable`: Whether the index is deferrable.
        - `include`: Whether the index includes certain elements.
        - `opclasses`: The operator classes associated
        """

        if isinstance(other, self.__class__):
            return (
                self.name == other.name
                and self.index_type == other.index_type
                and self.expressions == other.expressions
                and self.condition == other.condition
                and self.deferrable == other.deferrable
                and self.include == other.include
                and self.opclasses == other.opclasses
                and self.violation_error_message == other.violation_error_message
            )
        return super().__eq__(other)

    def __repr__(self):
        return "<%s: index_type=%s expressions=%s name=%s%s%s%s%s>" % (
            self.__class__.__qualname__,
            repr(self.index_type),
            repr(self.expressions),
            repr(self.name),
            "" if self.condition is None else " condition=%s" % self.condition,
            "" if self.deferrable is None else " deferrable=%r" % self.deferrable,
            "" if not self.include else " include=%s" % repr(self.include),
            "" if not self.opclasses else " opclasses=%s" % repr(self.opclasses),
        )

    def validate(self, model, instance, exclude=None, using=DEFAULT_DB_ALIAS):
        """
        Validate a model instance against a set of PostgreSQL expressions.
        
        This function checks if a given model instance violates any of the specified PostgreSQL expressions. It uses a queryset to filter the instances that match the expressions and raises a `ValidationError` if any match is found.
        
        Parameters:
        model (Model): The Django model class to validate against.
        instance (Model instance): The instance of the model to validate.
        exclude (list, optional): A list of field names to exclude from the validation. Defaults to
        """

        queryset = model._default_manager.using(using)
        replacement_map = instance._get_field_value_map(
            meta=model._meta, exclude=exclude
        )
        lookups = []
        for idx, (expression, operator) in enumerate(self.expressions):
            if isinstance(expression, str):
                expression = F(expression)
            if isinstance(expression, F):
                if exclude and expression.name in exclude:
                    return
                rhs_expression = replacement_map.get(expression.name, expression)
            else:
                rhs_expression = expression.replace_references(replacement_map)
                if exclude:
                    for expr in rhs_expression.flatten():
                        if isinstance(expr, F) and expr.name in exclude:
                            return
            # Remove OpClass because it only has sense during the constraint
            # creation.
            if isinstance(expression, OpClass):
                expression = expression.get_source_expressions()[0]
            if isinstance(rhs_expression, OpClass):
                rhs_expression = rhs_expression.get_source_expressions()[0]
            lookup = PostgresOperatorLookup(lhs=expression, rhs=rhs_expression)
            lookup.postgres_operator = operator
            lookups.append(lookup)
        queryset = queryset.filter(*lookups)
        model_class_pk = instance._get_pk_val(model._meta)
        if not instance._state.adding and model_class_pk is not None:
            queryset = queryset.exclude(pk=model_class_pk)
        if not self.condition:
            if queryset.exists():
                raise ValidationError(self.get_violation_error_message())
        else:
            if (self.condition & Exists(queryset.filter(self.condition))).check(
                replacement_map, using=using
            ):
                raise ValidationError(self.get_violation_error_message())
