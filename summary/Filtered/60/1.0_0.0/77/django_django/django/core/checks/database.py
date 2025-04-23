from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Function to validate database backends.
    
    Args:
    databases (Optional[List[str]]): A list of database aliases to check. If None, no databases are checked.
    **kwargs: Additional keyword arguments to pass to the validation check.
    
    Returns:
    List[BaseDatabaseValidationIssue]: A list of validation issues found in the specified databases.
    
    This function iterates over the provided database aliases, retrieves the connection for each alias, and performs validation checks using the specified keyword arguments. The results of these checks
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
