from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Function to validate database backends.
    
    Parameters:
    databases (list, optional): A list of database aliases to validate. If None, no validation is performed and an empty list is returned.
    **kwargs: Additional keyword arguments to pass to the validation check method of each database connection.
    
    Returns:
    list: A list of validation issues found during the check. Each issue is a dictionary containing details about the validation failure.
    
    This function iterates over a list of database aliases, retrieves the corresponding database connection
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
