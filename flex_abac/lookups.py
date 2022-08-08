from django.db.models import Lookup, Field


@Field.register_lookup
class NotEqual(Lookup):
    """
    Checks whether a field is different from a value. Used to allow using exclusion when we are actually using filtering.

    Example:

    .. code-block:: python

        queryset.filter(value__fbne=10)

    """

    lookup_name = 'fbne'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params

@Field.register_lookup
class NotSimilar(Lookup):
    """
    Checks whether a field is different from a string value, using regular expressions. Corresponds to the
    ``SIMILAR TO`` operator in Postgres.
    More information at https://www.postgresql.org/docs/current/functions-matching.html#FUNCTIONS-SIMILARTO-REGEXP.

    Example:

    .. code-block:: python

        queryset.filter(country_name__fbnotsimilar='%(an|al)%')

    This will cause the operation to return records having a country_name that contains the letters `an` or `al`.

    """

    lookup_name = 'fbnotsimilar'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'NOT %s SIMILAR TO %s' % (lhs, rhs), params