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
        Function to prepare a lookup for a database query.
        
        This method is used to prepare a lookup expression for a database query. It checks if the right-hand side (rhs) of the lookup is a Query object. If it is, it converts it into an ArraySubquery. The function then calls the `get_prep_lookup` method of the superclass to further prepare the lookup.
        
        Parameters:
        self (object): The current instance of the class, which should have a `rhs` attribute and a superclass
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
s_operator = "%%>>"
