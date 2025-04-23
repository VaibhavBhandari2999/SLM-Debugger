from django.db.models import Transform
from django.db.models.lookups import PostgresOperatorLookup
from django.db.models.sql.query import Query

from .search import SearchVector, SearchVectorExact, SearchVectorField


class DataContains(PostgresOperatorLookup):
    lookup_name = "contains"
    postgres_operator = "@>"


class ContainedBy(PostgresOperatorLookup):
    lookup_name = "contained_by"
    postgres_operator = "<@"


class Overlap(PostgresOperatorLookup):
    lookup_name = "overlap"
    postgres_operator = "&&"

    def get_prep_lookup(self):
        """
        Generates a prepared lookup for a database query.
        
        This method is used to prepare a lookup expression for a database query. If the right-hand side (rhs) of the lookup is a Query object, it is converted to an ArraySubquery. The method then calls the `get_prep_lookup` method of the superclass to further prepare the lookup.
        
        Parameters:
        self (object): The instance of the class containing the lookup.
        
        Returns:
        object: The prepared lookup expression, which is suitable for use
        """

        from .expressions import ArraySubquery

        if isinstance(self.rhs, Query):
            self.rhs = ArraySubquery(self.rhs)
        return super().get_prep_lookup()


class HasKey(PostgresOperatorLookup):
    lookup_name = "has_key"
    postgres_operator = "?"
    prepare_rhs = False


class HasKeys(PostgresOperatorLookup):
    lookup_name = "has_keys"
    postgres_operator = "?&"

    def get_prep_lookup(self):
        return [str(item) for item in self.rhs]


class HasAnyKeys(HasKeys):
    lookup_name = "has_any_keys"
    postgres_operator = "?|"


class Unaccent(Transform):
    bilateral = True
    lookup_name = "unaccent"
    function = "UNACCENT"


class SearchLookup(SearchVectorExact):
    lookup_name = "search"

    def process_lhs(self, qn, connection):
        """
        Processes the left-hand side of a search query.
        
        This method is responsible for ensuring that the left-hand side of a search query is a `SearchVectorField`. If it is not, it wraps the field with a `SearchVector` object, using the configuration from the right-hand side if available. The method then processes the left-hand side using the provided query node and connection.
        
        Parameters:
        - qn (object): The query node used to process the left-hand side.
        - connection (object):
        """

        if not isinstance(self.lhs.output_field, SearchVectorField):
            config = getattr(self.rhs, "config", None)
            self.lhs = SearchVector(self.lhs, config=config)
        lhs, lhs_params = super().process_lhs(qn, connection)
        return lhs, lhs_params


class TrigramSimilar(PostgresOperatorLookup):
    lookup_name = "trigram_similar"
    postgres_operator = "%%"


class TrigramWordSimilar(PostgresOperatorLookup):
    lookup_name = "trigram_word_similar"
    postgres_operator = "%%>"


class TrigramStrictWordSimilar(PostgresOperatorLookup):
    lookup_name = "trigram_strict_word_similar"
    postgres_operator = "%%>>"
