from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Validate database backends.
    
    This function checks the given database backends for any issues based on the provided validation parameters.
    
    Parameters:
    databases (list, optional): A list of database aliases to check. If None, all available databases are checked.
    **kwargs: Additional keyword arguments to pass to the validation check method of each database connection.
    
    Returns:
    list: A list of validation issues found in the database backends. Each issue is a dictionary with details about the problem.
    
    Example:
    >>>
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
