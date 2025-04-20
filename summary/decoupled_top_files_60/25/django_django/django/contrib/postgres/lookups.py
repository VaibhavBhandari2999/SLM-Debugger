from django.db.models import Lookup, Transform
from django.db.models.lookups import Exact, FieldGetDbPrepValueMixin

from .search import SearchVector, SearchVectorExact, SearchVectorField


class PostgresSimpleLookup(FieldGetDbPrepValueMixin, Lookup):
    def as_sql(self, qn, connection):
        """
        Generates a SQL query fragment for a comparison operation.
        
        This function constructs a SQL query fragment based on the provided operands and operator. It processes the left-hand side (lhs) and right-hand side (rhs) of the comparison separately, then combines them into a single SQL fragment.
        
        Parameters:
        qn (callable): A quoting function that should be used to quote identifiers in the SQL fragment.
        connection (object): A database connection object that provides database-specific information.
        
        Returns:
        tuple: A
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
        Processes the right-hand side (RHS) of a query in a database.
        
        This method is an extension of a superclass method, designed to handle the right-hand side of a database query. It takes a `compiler` object and a `connection` object as parameters. The primary function is to modify the processing of the RHS based on the value being `None`. If the RHS value is `None`, it treats it as a SQL `NULL` value, returning a tuple with the string `'null
        """

        result = super().process_rhs(compiler, connection)
        # Treat None lookup values as null.
        return ("'null'", []) if result == ('%s', [None]) else result
