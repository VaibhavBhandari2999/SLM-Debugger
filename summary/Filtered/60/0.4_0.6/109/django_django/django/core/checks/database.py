from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Function to validate database backends.
    
    Parameters:
    databases (list, optional): A list of database aliases to validate. If None, returns an empty list.
    **kwargs: Additional keyword arguments to pass to the validation check method of each database connection.
    
    Returns:
    list: A list of validation issues found during the checks.
    
    This function iterates over the provided database aliases, retrieves the corresponding database connection, and performs validation checks using the provided keyword arguments. The results of these checks are aggregated and
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
