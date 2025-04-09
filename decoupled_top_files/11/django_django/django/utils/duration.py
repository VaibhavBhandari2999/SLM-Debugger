import datetime


def _get_duration_components(duration):
    """
    Extracts and returns the duration components from a given timedelta object.
    
    Args:
    duration (timedelta): A timedelta object representing a time duration.
    
    Returns:
    tuple: A tuple containing the following components of the duration:
    - days (int): The number of days.
    - hours (int): The number of hours.
    - minutes (int): The number of minutes.
    - seconds (int): The number of seconds.
    - microseconds (int): The number of microseconds
    """

    days = duration.days
    seconds = duration.seconds
    microseconds = duration.microseconds

    minutes = seconds // 60
    seconds = seconds % 60

    hours = minutes // 60
    minutes = minutes % 60

    return days, hours, minutes, seconds, microseconds


def duration_string(duration):
    """Version of str(timedelta) which is not English specific."""
    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)

    string = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    if days:
        string = '{} '.format(days) + string
    if microseconds:
        string += '.{:06d}'.format(microseconds)

    return string


def duration_iso_string(duration):
    """
    Converts a datetime.timedelta object to an ISO 8601 duration string.
    
    Args:
    duration (datetime.timedelta): The duration to be converted.
    
    Returns:
    str: The ISO 8601 duration string representing the input duration.
    
    Raises:
    None
    
    Notes:
    - The function handles both positive and negative durations.
    - It extracts components from the duration such as days, hours, minutes, seconds, and microseconds.
    - The resulting string includes the
    """

    if duration < datetime.timedelta(0):
        sign = '-'
        duration *= -1
    else:
        sign = ''

    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)
    ms = '.{:06d}'.format(microseconds) if microseconds else ""
    return '{}P{}DT{:02d}H{:02d}M{:02d}{}S'.format(sign, days, hours, minutes, seconds, ms)


def duration_microseconds(delta):
    return (24 * 60 * 60 * delta.days + delta.seconds) * 1000000 + delta.microseconds
