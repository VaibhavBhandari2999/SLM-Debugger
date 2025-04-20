from django.utils.timezone import utc


def utc_tzinfo_factory(offset):
    """
    Generate a timezone information factory for UTC.
    
    This function is used to create a timezone information factory that always returns UTC (Coordinated Universal Time). If the provided offset is not 0, an AssertionError is raised, indicating that the database connection is not set to UTC.
    
    Parameters:
    offset (int): The timezone offset in hours from UTC. Should be 0 for UTC.
    
    Returns:
    function: A timezone information factory that returns UTC timezone information.
    
    Raises:
    AssertionError: If the offset is not 0
    """

    if offset != 0:
        raise AssertionError("database connection isn't set to UTC")
    return utc
