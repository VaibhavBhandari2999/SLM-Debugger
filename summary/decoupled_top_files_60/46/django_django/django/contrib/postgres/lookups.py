from django.db.models import Transform
from django.db.models.lookups import PostgresOperatorLookup

from .search import SearchVector, SearchVectorExact, SearchVectorField


class DataContains(PostgresOperatorLookup):
    lookup_name = 'contains'
    postgres_operator = '@>'


class ContainedBy(PostgresOperatorLookup):
    lookup_name = 'contained_by'
    postgres_operator = '<@'


class Overlap(PostgresOperatorLookup):
    lookup_name = 'overlap'
    postgres_operator = '&&'


class HasKey(PostgresOperatorLookup):
    lookup_name = 'has_key'
    postgres_operator = '?'
    prepare_rhs = False


class HasKeys(PostgresOperatorLookup):
    lookup_name = 'has_keys'
    postgres_operator = '?&'

    def get_prep_lookup(self):
        return [str(item) for item in self.rhs]


class HasAnyKeys(HasKeys):
    lookup_name = 'has_any_keys'
    postgres_operator = '?|'


class Unaccent(Transform):
    bilateral = True
    lookup_name = 'unaccent'
    function = 'UNACCENT'


class SearchLookup(SearchVectorExact):
    lookup_name = 'search'

    def process_lhs(self, qn, connection):
        """
        Processes the left-hand side of a search query.
        
        This method is responsible for ensuring that the left-hand side (lhs) of a search query is a `SearchVectorField`. If it is not, a `SearchVector` is created with the provided configuration. The method then processes the lhs using the provided query node (qn) and database connection (connection).
        
        Parameters:
        - qn (object): The query node representing the left-hand side of the query.
        - connection (object): The database connection
        """

        if not isinstance(self.lhs.output_field, SearchVectorField):
            config = getattr(self.rhs, 'config', None)
            self.lhs = SearchVector(self.lhs, config=config)
        lhs, lhs_params = super().process_lhs(qn, connection)
        return lhs, lhs_params


class TrigramSimilar(PostgresOperatorLookup):
    lookup_name = 'trigram_similar'
    postgres_operator = '%%'
