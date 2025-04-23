from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Function to validate database backends.
    
    This function checks the specified database backends for any validation issues.
    
    Parameters:
    databases (list, optional): A list of database aliases to check. If None, no databases will be checked.
    **kwargs: Additional keyword arguments to pass to the validation check method of the database connection.
    
    Returns:
    list: A list of validation issues found. Each issue is a dictionary with details about the problem.
    
    Example:
    >>> check_database_backends(['default', '
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
