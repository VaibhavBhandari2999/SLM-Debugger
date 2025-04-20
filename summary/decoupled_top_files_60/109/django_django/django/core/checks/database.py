from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Function to validate database backends.
    
    Args:
    databases (Optional[Dict[str, Database]]): A dictionary of database aliases and their corresponding database objects. If None, an empty list is returned.
    **kwargs: Additional keyword arguments to pass to the validation checks.
    
    Returns:
    List[ValidationIssue]: A list of validation issues found during the checks.
    
    This function iterates over the provided database aliases, retrieves the corresponding database connection, and performs validation checks using the provided keyword arguments. The results
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
