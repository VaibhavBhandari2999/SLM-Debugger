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
        """
        Generate a SQL expression for Oracle database to compute a hash of a given string.
        
        This method is used to generate a SQL expression that computes a hash of a string using Oracle's UTL_I18N and RAWTOHEX functions. The hash function used can be specified via the `function` keyword argument.
        
        Parameters:
        compiler (object): The SQL compiler object used to generate the SQL.
        connection (object): The database connection object.
        extra_context (dict): Additional context for the
        """

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
        return super().as_sql(
            compiler, connection, function='CHAR',
            template='%(function)s(%(expressions)s USING utf16)',
            **extra_context
        )

    def as_oracle(self, compiler, connection, **extra_context):
        """
        Generate an Oracle-compatible SQL function call.
        
        This method is used to generate a SQL function call that is compatible with Oracle databases. The function takes a SQLCompiler object and a database connection object as inputs. It returns a string representing the SQL function call.
        
        Parameters:
        compiler (SQLCompiler): The SQLCompiler object used for compiling the SQL query.
        connection (Connection): The database connection object.
        extra_context (dict, optional): Additional context to be passed to the SQL template.
        
        Returns:
        """

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
        # Use CONCAT_WS with an empty separator so that NULLs are ignored.
        return super().as_sql(
            compiler, connection, function='CONCAT_WS',
            template="%(function)s('', %(expressions)s)",
            **extra_context
        )

    def coalesce(self):
        """
        Coalesce the source expressions to handle null values.
        
        This method creates a copy of the current expression and sets its source expressions to be coalesced. If either side of the coalesced expression is null, the result will be null. Otherwise, the non-null value will be returned. The coalesced expressions are wrapped with a Coalesce function.
        
        Parameters:
        None
        
        Returns:
        A new expression with the source expressions coalesced.
        """

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
        if len(expressions) < 2:
            raise ValueError('Concat must take at least two expressions')
        paired = self._paired(expressions)
        super().__init__(paired, **extra)

    def _paired(self, expressions):
        """
        Generate a nested ConcatPair from a list of expressions.
        
        This function takes a list of expressions and recursively pairs them using ConcatPair,
        wrapping them in successive concat functions.
        
        Parameters:
        expressions (list): A list of expressions to be paired.
        
        Returns:
        ConcatPair: A nested ConcatPair object representing the paired expressions.
        
        Example:
        Given the list [a, b, c, d], the function will return:
        ConcatPair(a, ConcatPair(b, ConcatPair(c, d
        """

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
        if not hasattr(number, 'resolve_expression') and number is not None and number < 0:
            raise ValueError("'number' must be greater or equal to 0.")
        super().__init__(expression, number, **extra)

    def as_oracle(self, compiler, connection, **extra_context):
        """
        Generate an Oracle-specific SQL expression for padding a string.
        
        This function is designed to be used with a database compiler and connection
        to generate a SQL expression that pads a string to a specified length using
        the same string as the padding character.
        
        Parameters:
        compiler (BaseDatabaseCompiler): The database compiler instance.
        connection (Connection): The database connection object.
        extra_context (dict): Additional context for the SQL generation.
        
        Returns:
        str: The generated SQL expression as a string.
        
        Key Parameters
        """

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
        Generate an Oracle-specific SQL query for LISTAGG.
        
        This function generates a SQL query for the LISTAGG function in Oracle databases, which is used to concatenate a group of values. Since Oracle's REVERSE function does not support multi-byte strings, a special subquery is used to reverse the string and then aggregate the characters.
        
        Parameters:
        compiler (sql.compiler.SQLCompiler): The SQL compiler instance.
        connection (connections.base.DatabaseWrapper): The database connection object.
        extra_context (dict):
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
ame = 'upper'
