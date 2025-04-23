from django.db import connections

from . import Tags, register


@register(Tags.database)
def check_database_backends(databases=None, **kwargs):
    """
    Function to validate database backends.
    
    Args:
    databases (Optional[List[str]]): A list of database aliases to validate. If None, all databases will be validated.
    **kwargs: Additional keyword arguments to pass to the validation check function.
    
    Returns:
    List[ValidationIssue]: A list of validation issues found during the check.
    
    This function iterates over the specified database aliases and performs validation checks on each. If no specific database aliases are provided, it will validate all available databases. The validation
    """

    if databases is None:
        return []
    issues = []
    for alias in databases:
        conn = connections[alias]
        issues.extend(conn.validation.check(**kwargs))
    return issues
