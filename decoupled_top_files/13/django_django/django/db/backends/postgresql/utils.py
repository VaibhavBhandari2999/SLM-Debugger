from django.utils.timezone import utc


def utc_tzinfo_factory(offset):
    """
    utc_tzinfo_factory(offset) -> tzinfo
    
    Creates a timezone information factory for UTC.
    
    Args:
    offset (int): The time offset from UTC. If non-zero, an assertion error is raised.
    
    Returns:
    tzinfo: A timezone information object representing UTC.
    
    Raises:
    AssertionError: If the offset is not zero, indicating that the database connection is not set to UTC.
    """

    if offset != 0:
        raise AssertionError("database connection isn't set to UTC")
    return utc
