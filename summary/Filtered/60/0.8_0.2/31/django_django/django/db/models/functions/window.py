from django.db.models.expressions import Func
from django.db.models.fields import FloatField, IntegerField

__all__ = [
    'CumeDist', 'DenseRank', 'FirstValue', 'Lag', 'LastValue', 'Lead',
    'NthValue', 'Ntile', 'PercentRank', 'Rank', 'RowNumber',
]


class CumeDist(Func):
    function = 'CUME_DIST'
    output_field = FloatField()
    window_compatible = True


class DenseRank(Func):
    function = 'DENSE_RANK'
    output_field = IntegerField()
    window_compatible = True


class FirstValue(Func):
    arity = 1
    function = 'FIRST_VALUE'
    window_compatible = True


class LagLeadFunction(Func):
    window_compatible = True

    def __init__(self, expression, offset=1, default=None, **extra):
        """
        Initialize a new instance of the class.
        
        Args:
        expression (str): A non-null source expression required for the instance.
        offset (int): A positive integer required for the offset.
        default (optional): An optional default value to be used.
        **extra: Additional keyword arguments to be passed to the superclass.
        
        Raises:
        ValueError: If `expression` is None or `offset` is not a positive integer.
        """

        if expression is None:
            raise ValueError(
                '%s requires a non-null source expression.' %
                self.__class__.__name__
            )
        if offset is None or offset <= 0:
            raise ValueError(
                '%s requires a positive integer for the offset.' %
                self.__class__.__name__
            )
        args = (expression, offset)
        if default is not None:
            args += (default,)
        super().__init__(*args, **extra)

    def _resolve_output_field(self):
        sources = self.get_source_expressions()
        return sources[0].output_field


class Lag(LagLeadFunction):
    function = 'LAG'


class LastValue(Func):
    arity = 1
    function = 'LAST_VALUE'
    window_compatible = True


class Lead(LagLeadFunction):
    function = 'LEAD'


class NthValue(Func):
    function = 'NTH_VALUE'
    window_compatible = True

    def __init__(self, expression, nth=1, **extra):
        """
        Initialize a new instance of the class.
        
        This method sets up a new object with the specified expression and nth value.
        
        Parameters:
        expression (str): The source expression required for the object.
        nth (int): A positive integer indicating the nth occurrence to be processed. Defaults to 1.
        **extra: Additional keyword arguments to be passed to the superclass.
        
        Raises:
        ValueError: If the expression is None or if nth is not a positive integer.
        
        Returns:
        None: This method does
        """

        if expression is None:
            raise ValueError('%s requires a non-null source expression.' % self.__class__.__name__)
        if nth is None or nth <= 0:
            raise ValueError('%s requires a positive integer as for nth.' % self.__class__.__name__)
        super().__init__(expression, nth, **extra)

    def _resolve_output_field(self):
        sources = self.get_source_expressions()
        return sources[0].output_field


class Ntile(Func):
    function = 'NTILE'
    output_field = IntegerField()
    window_compatible = True

    def __init__(self, num_buckets=1, **extra):
        """
        Initialize a new instance of the class.
        
        Args:
        num_buckets (int, optional): The number of buckets to use. Must be greater than 0. Defaults to 1.
        **extra: Additional keyword arguments to pass to the superclass.
        
        Raises:
        ValueError: If num_buckets is less than or equal to 0.
        
        Returns:
        None: This method does not return any value.
        """

        if num_buckets <= 0:
            raise ValueError('num_buckets must be greater than 0.')
        super().__init__(num_buckets, **extra)


class PercentRank(Func):
    function = 'PERCENT_RANK'
    output_field = FloatField()
    window_compatible = True


class Rank(Func):
    function = 'RANK'
    output_field = IntegerField()
    window_compatible = True


class RowNumber(Func):
    function = 'ROW_NUMBER'
    output_field = IntegerField()
    window_compatible = True
