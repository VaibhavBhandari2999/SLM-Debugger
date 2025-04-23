from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Check database backends for validation issues.
    
    This function checks the specified database backends for validation issues using the provided keyword arguments.
    
    Parameters:
    databases (list, optional): A list of database aliases to check. If None, all available databases are checked.
    **kwargs: Keyword arguments to pass to the validation checks.
    
    Returns:
    list: A list of validation issues found during the checks.
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
