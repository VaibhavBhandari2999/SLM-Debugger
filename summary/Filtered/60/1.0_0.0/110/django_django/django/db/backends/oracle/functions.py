from django.db.models import DecimalField, DurationField, Func


class IntervalToSeconds(Func):
    function = ""
    template = """
    EXTRACT(day from %(expressions)s) * 86400 +
    EXTRACT(hour from %(expressions)s) * 3600 +
    EXTRACT(minute from %(expressions)s) * 60 +
    EXTRACT(second from %(expressions)s)
    """

    def __init__(self, expression, *, output_field=None, **extra):
        super().__init__(
            expression, output_field=output_field or DecimalField(), **extra
        )


class SecondsToInterval(Func):
    function = "NUMTODSINTERVAL"
    template = "%(function)s(%(expressions)s, 'SECOND')"

    def __init__(self, expression, *, output_field=None, **extra):
        """
        Initialize a DurationExpression object.
        
        Args:
        expression (str): The expression to be evaluated, representing a duration.
        output_field (Field, optional): The output field type. Defaults to DurationField if not specified.
        **extra: Additional keyword arguments to be passed to the superclass.
        
        This method initializes a DurationExpression object with the provided expression and sets the output field to DurationField if no output_field is specified. Any additional keyword arguments are passed to the superclass.
        """

        super().__init__(
            expression, output_field=output_field or DurationField(), **extra
        )
