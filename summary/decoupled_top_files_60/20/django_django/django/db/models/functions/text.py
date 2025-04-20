from django.db.models.expressions import Func, Value
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce
from django.db.models.lookups import Transform
from django.db.utils import NotSupportedError


class BytesToCharFieldConversionMixin:
    """
    Convert CharField results from bytes to str.

    MySQL returns long data types (bytes) instead of chars when it can't
    determine the length of the result string. For example:
        LPAD(column1, CHAR_LENGTH(column2), ' ')
    returns the LONGTEXT (bytes) instead of VARCHAR.
    """
    def convert_value(self, value, expression, connection):
        """
        Converts a value based on the database's capabilities and the output field type.
        
        This method is used to convert a value from the database to a Python object, taking into account the database's features and the output field type. If the database supports converting bytes to strings and the output field is a CharField, the method will decode the bytes to a string. Otherwise, it will use the superclass's method to perform the conversion.
        
        Parameters:
        value (Any): The value to be converted.
        """

        if connection.features.db_functions_convert_bytes_to_str:
            if self.output_field.get_internal_type() == 'CharField' and isinstance(value, bytes):
                return value.decode()
        return super().convert_value(value, expression, connection)


class MySQLSHA2Mixin:
    def as_mysql(self, compiler, connection, **extra_content):
        return super().as_sql(
            compiler,
            connection,
            template='SHA2(%%(expressions)s, %s)' % self.function[3:],
            **extra_content,
        )


class OracleHashMixin:
    def as_oracle(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler,
            connection,
            template=(
                "LOWER(RAWTOHEX(STANDARD_HASH(UTL_I18N.STRING_TO_RAW("
                "%(expressions)s, 'AL32UTF8'), '%(function)s')))"
            ),
            **extra_context,
        )


class PostgreSQLSHAMixin:
    def as_postgresql(self, compiler, connection, **extra_content):
        return super().as_sql(
            compiler,
            connection,
            template="ENCODE(DIGEST(%(expressions)s, '%(function)s'), 'hex')",
            function=self.function.lower(),
            **extra_content,
        )


class Chr(Transform):
    function = 'CHR'
    lookup_name = 'chr'

    def as_mysql(self, compiler, connection, **extra_context):
        """
        Generates a MySQL-specific SQL expression for the given compiler and connection.
        
        This method is used to create a SQL expression that is compatible with MySQL. It utilizes the `CHAR` function to convert the provided expressions into a specific character set (utf16).
        
        Parameters:
        compiler (object): The SQL compiler object used to generate the SQL.
        connection (object): The database connection object.
        extra_context (dict, optional): Additional context for the SQL generation (default is an empty dictionary).
        
        Returns
        """

        return super().as_sql(
            compiler, connection, function='CHAR',
            template='%(function)s(%(expressions)s USING utf16)',
            **extra_context
        )

    def as_oracle(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler, connection,
            template='%(function)s(%(expressions)s USING NCHAR_CS)',
            **extra_context
        )

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function='CHAR', **extra_context)


class ConcatPair(Func):
    """
    Concatenate two arguments together. This is used by `Concat` because not
    all backend databases support more than two arguments.
    """
    function = 'CONCAT'

    def as_sqlite(self, compiler, connection, **extra_context):
        coalesced = self.coalesce()
        return super(ConcatPair, coalesced).as_sql(
            compiler, connection, template='%(expressions)s', arg_joiner=' || ',
            **extra_context
        )

    def as_mysql(self, compiler, connection, **extra_context):
        """
        Generates a MySQL-specific SQL expression for concatenating strings.
        
        This function is used to create a SQL expression that concatenates multiple string expressions in a MySQL database. It leverages the `CONCAT_WS` function, which concatenates strings with a specified separator. In this case, an empty separator is used to ignore NULL values.
        
        Parameters:
        compiler (object): The SQL compiler object used to generate SQL.
        connection (object): The database connection object.
        extra_context (dict): Additional context
        """

        # Use CONCAT_WS with an empty separator so that NULLs are ignored.
        return super().as_sql(
            compiler, connection, function='CONCAT_WS',
            template="%(function)s('', %(expressions)s)",
            **extra_context
        )

    def coalesce(self):
        # null on either side results in null for expression, wrap with coalesce
        c = self.copy()
        c.set_source_expressions([
            Coalesce(expression, Value('')) for expression in c.get_source_expressions()
        ])
        return c


class Concat(Func):
    """
    Concatenate text fields together. Backends that result in an entire
    null expression when any arguments are null will wrap each argument in
    coalesce functions to ensure a non-null result.
    """
    function = None
    template = "%(expressions)s"

    def __init__(self, *expressions, **extra):
        """
        Initialize a Concat object.
        
        This function initializes a Concat object by combining multiple expressions.
        
        Parameters:
        *expressions: Variable length argument list of expressions to be concatenated.
        **extra: Additional keyword arguments to be passed to the superclass.
        
        Raises:
        ValueError: If fewer than two expressions are provided.
        
        Example:
        >>> concat = Concat('Hello', ' ', 'World')
        >>> str(concat)
        'Hello World'
        """

        if len(expressions) < 2:
            raise ValueError('Concat must take at least two expressions')
        paired = self._paired(expressions)
        super().__init__(paired, **extra)

    def _paired(self, expressions):
        # wrap pairs of expressions in successive concat functions
        # exp = [a, b, c, d]
        # -> ConcatPair(a, ConcatPair(b, ConcatPair(c, d))))
        if len(expressions) == 2:
            return ConcatPair(*expressions)
        return ConcatPair(expressions[0], self._paired(expressions[1:]))


class Left(Func):
    function = 'LEFT'
    arity = 2

    def __init__(self, expression, length, **extra):
        """
        expression: the name of a field, or an expression returning a string
        length: the number of characters to return from the start of the string
        """
        if not hasattr(length, 'resolve_expression'):
            if length < 1:
                raise ValueError("'length' must be greater than 0.")
        super().__init__(expression, length, **extra)

    def get_substr(self):
        return Substr(self.source_expressions[0], Value(1), self.source_expressions[1])

    def as_oracle(self, compiler, connection, **extra_context):
        return self.get_substr().as_oracle(compiler, connection, **extra_context)

    def as_sqlite(self, compiler, connection, **extra_context):
        return self.get_substr().as_sqlite(compiler, connection, **extra_context)


class Length(Transform):
    """Return the number of characters in the expression."""
    function = 'LENGTH'
    lookup_name = 'length'
    output_field = IntegerField()

    def as_mysql(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function='CHAR_LENGTH', **extra_context)


class Lower(Transform):
    function = 'LOWER'
    lookup_name = 'lower'


class LPad(BytesToCharFieldConversionMixin, Func):
    function = 'LPAD'

    def __init__(self, expression, length, fill_text=Value(' '), **extra):
        if not hasattr(length, 'resolve_expression') and length is not None and length < 0:
            raise ValueError("'length' must be greater or equal to 0.")
        super().__init__(expression, length, fill_text, **extra)


class LTrim(Transform):
    function = 'LTRIM'
    lookup_name = 'ltrim'


class MD5(OracleHashMixin, Transform):
    function = 'MD5'
    lookup_name = 'md5'


class Ord(Transform):
    function = 'ASCII'
    lookup_name = 'ord'
    output_field = IntegerField()

    def as_mysql(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function='ORD', **extra_context)

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function='UNICODE', **extra_context)


class Repeat(BytesToCharFieldConversionMixin, Func):
    function = 'REPEAT'

    def __init__(self, expression, number, **extra):
        """
        Initialize a new instance of the class.
        
        Args:
        expression (str): The expression to be evaluated.
        number (int, optional): The number associated with the expression. Must be greater or equal to 0. Defaults to None.
        **extra (dict): Additional keyword arguments to be passed to the superclass.
        
        Raises:
        ValueError: If 'number' is provided and is less than 0.
        
        Returns:
        None: This method does not return any value.
        """

        if not hasattr(number, 'resolve_expression') and number is not None and number < 0:
            raise ValueError("'number' must be greater or equal to 0.")
        super().__init__(expression, number, **extra)

    def as_oracle(self, compiler, connection, **extra_context):
        expression, number = self.source_expressions
        length = None if number is None else Length(expression) * number
        rpad = RPad(expression, length, expression)
        return rpad.as_sql(compiler, connection, **extra_context)


class Replace(Func):
    function = 'REPLACE'

    def __init__(self, expression, text, replacement=Value(''), **extra):
        super().__init__(expression, text, replacement, **extra)


class Reverse(Transform):
    function = 'REVERSE'
    lookup_name = 'reverse'

    def as_oracle(self, compiler, connection, **extra_context):
        """
        Generate a SQL query for Oracle to reverse a string.
        
        This function is designed to handle the reversal of strings in Oracle databases, where the standard REVERSE function is not suitable for multi-byte strings. Instead, it constructs a custom SQL query using a subquery to reverse the string character by character.
        
        Parameters:
        compiler (Compiler): The SQL compiler instance used to generate the SQL query.
        connection (Connection): The database connection object.
        extra_context (dict): Additional context for the SQL query,
        """

        # REVERSE in Oracle is undocumented and doesn't support multi-byte
        # strings. Use a special subquery instead.
        return super().as_sql(
            compiler, connection,
            template=(
                '(SELECT LISTAGG(s) WITHIN GROUP (ORDER BY n DESC) FROM '
                '(SELECT LEVEL n, SUBSTR(%(expressions)s, LEVEL, 1) s '
                'FROM DUAL CONNECT BY LEVEL <= LENGTH(%(expressions)s)) '
                'GROUP BY %(expressions)s)'
            ),
            **extra_context
        )


class Right(Left):
    function = 'RIGHT'

    def get_substr(self):
        return Substr(self.source_expressions[0], self.source_expressions[1] * Value(-1))


class RPad(LPad):
    function = 'RPAD'


class RTrim(Transform):
    function = 'RTRIM'
    lookup_name = 'rtrim'


class SHA1(OracleHashMixin, PostgreSQLSHAMixin, Transform):
    function = 'SHA1'
    lookup_name = 'sha1'


class SHA224(MySQLSHA2Mixin, PostgreSQLSHAMixin, Transform):
    function = 'SHA224'
    lookup_name = 'sha224'

    def as_oracle(self, compiler, connection, **extra_context):
        raise NotSupportedError('SHA224 is not supported on Oracle.')


class SHA256(MySQLSHA2Mixin, OracleHashMixin, PostgreSQLSHAMixin, Transform):
    function = 'SHA256'
    lookup_name = 'sha256'


class SHA384(MySQLSHA2Mixin, OracleHashMixin, PostgreSQLSHAMixin, Transform):
    function = 'SHA384'
    lookup_name = 'sha384'


class SHA512(MySQLSHA2Mixin, OracleHashMixin, PostgreSQLSHAMixin, Transform):
    function = 'SHA512'
    lookup_name = 'sha512'


class StrIndex(Func):
    """
    Return a positive integer corresponding to the 1-indexed position of the
    first occurrence of a substring inside another string, or 0 if the
    substring is not found.
    """
    function = 'INSTR'
    arity = 2
    output_field = IntegerField()

    def as_postgresql(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function='STRPOS', **extra_context)


class Substr(Func):
    function = 'SUBSTRING'

    def __init__(self, expression, pos, length=None, **extra):
        """
        expression: the name of a field, or an expression returning a string
        pos: an integer > 0, or an expression returning an integer
        length: an optional number of characters to return
        """
        if not hasattr(pos, 'resolve_expression'):
            if pos < 1:
                raise ValueError("'pos' must be greater than 0")
        expressions = [expression, pos]
        if length is not None:
            expressions.append(length)
        super().__init__(*expressions, **extra)

    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function='SUBSTR', **extra_context)

    def as_oracle(self, compiler, connection, **extra_context):
        return super().as_sql(compiler, connection, function='SUBSTR', **extra_context)


class Trim(Transform):
    function = 'TRIM'
    lookup_name = 'trim'


class Upper(Transform):
    function = 'UPPER'
    lookup_name = 'upper'
