from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Function to validate database backends.
    
    Args:
    databases (Optional[List[str]]): A list of database aliases to check. If None, all databases will be checked.
    **kwargs: Additional keyword arguments to pass to the validation check.
    
    Returns:
    List[ValidationIssue]: A list of validation issues found in the specified database backends.
    
    This function iterates over the provided database aliases and performs validation checks on each one. If no specific databases are provided, it checks all available databases. The
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
