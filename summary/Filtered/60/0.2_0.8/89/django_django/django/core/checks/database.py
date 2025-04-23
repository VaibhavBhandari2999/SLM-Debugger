from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Function to validate database backends.
    
    Args:
    databases (list, optional): A list of database aliases to check. If None, all databases will be checked. Defaults to None.
    **kwargs: Additional keyword arguments to pass to the validation checks.
    
    Returns:
    list: A list of validation issues found during the checks.
    
    This function iterates over the specified database aliases and performs validation checks on each one. The results of these checks are aggregated into a single list of issues, which is then
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
