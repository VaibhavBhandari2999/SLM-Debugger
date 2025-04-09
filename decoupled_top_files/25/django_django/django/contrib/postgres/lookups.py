from django.db.models import Lookup, Transform
from django.db.models.lookups import Exact, FieldGetDbPrepValueMixin

from .search import SearchVector, SearchVectorExact, SearchVectorField


class PostgresSimpleLookup(FieldGetDbPrepValueMixin, Lookup):
    def as_sql(self, qn, connection):
        """
        Generates an SQL query string based on the given operands and operator.
        
        Args:
        qn (function): A quoting function that quotes identifiers and values.
        connection (object): An object representing the database connection.
        
        Returns:
        tuple: A tuple containing the generated SQL query string and a list of parameters.
        
        Process:
        1. Calls `process_lhs` to generate the left-hand side of the query and its parameters.
        2. Calls `process_rhs` to generate
        """

        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = tuple(lhs_params) + tuple(rhs_params)
        return '%s %s %s' % (lhs, self.operator, rhs), params


class DataContains(PostgresSimpleLookup):
    lookup_name = 'contains'
    operator = '@>'


class ContainedBy(PostgresSimpleLookup):
    lookup_name = 'contained_by'
    operator = '<@'


class Overlap(PostgresSimpleLookup):
    lookup_name = 'overlap'
    operator = '&&'


class HasKey(PostgresSimpleLookup):
    lookup_name = 'has_key'
    operator = '?'
    prepare_rhs = False


class HasKeys(PostgresSimpleLookup):
    lookup_name = 'has_keys'
    operator = '?&'

    def get_prep_lookup(self):
        return [str(item) for item in self.rhs]


class HasAnyKeys(HasKeys):
    lookup_name = 'has_any_keys'
    operator = '?|'


class Unaccent(Transform):
    bilateral = True
    lookup_name = 'unaccent'
    function = 'UNACCENT'


class SearchLookup(SearchVectorExact):
    lookup_name = 'search'

    def process_lhs(self, qn, connection):
        """
        Processes the left-hand side (LHS) of a search query.
        
        Args:
        qn: The query node object.
        connection: The database connection object.
        
        Returns:
        A tuple containing the processed LHS and its parameters.
        
        Notes:
        - If the LHS output field is not an instance of `SearchVectorField`, it is converted to one using `SearchVector`.
        - The processed LHS and its parameters are obtained by calling the superclass's `process_lhs`
        """

        if not isinstance(self.lhs.output_field, SearchVectorField):
            self.lhs = SearchVector(self.lhs)
        lhs, lhs_params = super().process_lhs(qn, connection)
        return lhs, lhs_params


class TrigramSimilar(PostgresSimpleLookup):
    lookup_name = 'trigram_similar'
    operator = '%%'


class JSONExact(Exact):
    can_use_none_as_rhs = True

    def process_rhs(self, compiler, connection):
        """
        Processes the right-hand side of a query.
        
        Args:
        compiler: The database compiler object.
        connection: The database connection object.
        
        Returns:
        A tuple containing the processed value and a list of parameters.
        
        Summary:
        This function processes the right-hand side of a query using the provided compiler and connection objects. It checks if the result is a tuple with '%s' and None, and if so, returns a special case where the first element is "'null'" and the second
        """

        result = super().process_rhs(compiler, connection)
        # Treat None lookup values as null.
        return ("'null'", []) if result == ('%s', [None]) else result
