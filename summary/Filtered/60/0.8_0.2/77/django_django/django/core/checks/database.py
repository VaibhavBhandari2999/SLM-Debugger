from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Check database backends for validation issues.
    
    This function validates the database backends specified in the `databases` dictionary. It returns a list of validation issues found.
    
    Parameters:
    databases (dict, optional): A dictionary of database aliases and their corresponding database configurations. If None, an empty list is returned. Defaults to None.
    **kwargs: Additional keyword arguments to pass to the validation checks.
    
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
