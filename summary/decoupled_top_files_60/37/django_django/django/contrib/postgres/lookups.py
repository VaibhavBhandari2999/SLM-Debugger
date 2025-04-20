from django.db.models import Lookup, Transform
from django.db.models.lookups import Exact, FieldGetDbPrepValueMixin

from .search import SearchVector, SearchVectorExact, SearchVectorField


class PostgresSimpleLookup(FieldGetDbPrepValueMixin, Lookup):
    def as_sql(self, qn, connection):
        """
        Generates a SQL fragment for a comparison query.
        
        This function processes the left-hand side (lhs) and right-hand side (rhs) of a comparison
        query, applying any necessary transformations based on the database connection. It then
        combines these processed sides with the comparison operator to form a complete SQL fragment.
        
        Parameters:
        qn (callable): A quoting function that is used to quote identifiers and literals.
        connection (object): A database connection object that provides information about the
        database being
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
        Processes the right-hand side (RHS) of a database query for a specific compiler and connection.
        
        This method extends the functionality of a superclass method to handle `None` values in a special way. If the RHS value is `None`, it treats it as a SQL `NULL` value. Otherwise, it returns the original processed RHS value.
        
        Parameters:
        compiler (object): The database compiler instance used for processing the query.
        connection (object): The database connection object used for executing the query
        """

        result = super().process_rhs(compiler, connection)
        # Treat None lookup values as null.
        return ("'null'", []) if result == ('%s', [None]) else result
