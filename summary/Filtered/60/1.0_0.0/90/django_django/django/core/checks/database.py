from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Check database backends for validation issues.
    
    This function checks the specified database backends for any validation issues based on the provided keyword arguments.
    
    Parameters:
    databases (list, optional): A list of database aliases to check. If None, all available databases will be checked. Defaults to None.
    **kwargs: Additional keyword arguments to pass to the validation check method of each database connection.
    
    Returns:
    list: A list of validation issues found in the specified database backends. Each issue is a dictionary
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
