from sympy.testing.pytest import raises
from sympy.parsing.sym_expr import SymPyExpression
from sympy.external import import_module

lfortran = import_module('lfortran')

if lfortran:
    from sympy.codegen.ast import (Variable, IntBaseType, FloatBaseType, String,
                                   Return, FunctionDefinition, Assignment,
                                   Declaration, CodeBlock)
    from sympy.core import Integer, Float, Add
    from sympy import Symbol


    expr1 = SymPyExpression()
    expr2 = SymPyExpression()
    src = """\
    integer :: a, b, c, d
    real :: p, q, r, s
    """


    def test_sym_expr():
        """
        Tests the SymPyExpression class with a source code string containing a simple arithmetic expression.
        
        This function checks the functionality of the SymPyExpression class by parsing a source code string that includes a declaration of variables and an arithmetic expression. It then verifies that the parsed expressions match the expected declarations and assignments.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Define the source code string `src` with initial variable declarations.
        2. Append an arithmetic expression to the source code string `src
        """

        src1 = (
            src +
            """\
            d = a + b -c
            """
        )
        expr3 = SymPyExpression(src,'f')
        expr4 = SymPyExpression(src1,'f')
        ls1 = expr3.return_expr()
        ls2 = expr4.return_expr()
        for i in range(0, 7):
            assert isinstance(ls1[i], Declaration)
            assert isinstance(ls2[i], Declaration)
        assert isinstance(ls2[8], Assignment)
        assert ls1[0] == Declaration(
            Variable(
                Symbol('a'),
                type = IntBaseType(String('integer')),
                value = Integer(0)
            )
        )
        assert ls1[1] == Declaration(
            Variable(
                Symbol('b'),
                type = IntBaseType(String('integer')),
                value = Integer(0)
            )
        )
        assert ls1[2] == Declaration(
            Variable(
                Symbol('c'),
                type = IntBaseType(String('integer')),
                value = Integer(0)
            )
        )
        assert ls1[3] == Declaration(
            Variable(
                Symbol('d'),
                type = IntBaseType(String('integer')),
                value = Integer(0)
            )
        )
        assert ls1[4] == Declaration(
            Variable(
                Symbol('p'),
                type = FloatBaseType(String('real')),
                value = Float(0.0)
            )
        )
        assert ls1[5] == Declaration(
            Variable(
                Symbol('q'),
                type = FloatBaseType(String('real')),
                value = Float(0.0)
            )
        )
        assert ls1[6] == Declaration(
            Variable(
                Symbol('r'),
                type = FloatBaseType(String('real')),
                value = Float(0.0)
            )
        )
        assert ls1[7] == Declaration(
            Variable(
                Symbol('s'),
                type = FloatBaseType(String('real')),
                value = Float(0.0)
            )
        )
        assert ls2[8] == Assignment(
            Variable(Symbol('d')),
            Symbol('a') + Symbol('b') - Symbol('c')
        )

    def test_assignment():
        src1 = (
            src +
            """\
            a = b
            c = d
            p = q
            r = s
            """
        )
        expr1.convert_to_expr(src1, 'f')
        ls1 = expr1.return_expr()
        for iter in range(0, 12):
            if iter < 8:
                assert isinstance(ls1[iter], Declaration)
            else:
                assert isinstance(ls1[iter], Assignment)
        assert ls1[8] == Assignment(
            Variable(Symbol('a')),
            Variable(Symbol('b'))
        )
        assert ls1[9] == Assignment(
            Variable(Symbol('c')),
            Variable(Symbol('d'))
        )
        assert ls1[10] == Assignment(
            Variable(Symbol('p')),
            Variable(Symbol('q'))
        )
        assert ls1[11] == Assignment(
            Variable(Symbol('r')),
            Variable(Symbol('s'))
        )


    def test_binop_add():
        src1 = (
            src +
            """\
            c = a + b
            d = a + c
            s = p + q + r
            """
        )
        expr1.convert_to_expr(src1, 'f')
        ls1 = expr1.return_expr()
        for iter in range(8, 11):
            assert isinstance(ls1[iter], Assignment)
        assert ls1[8] == Assignment(
            Variable(Symbol('c')),
            Symbol('a') + Symbol('b')
        )
        assert ls1[9] == Assignment(
            Variable(Symbol('d')),
            Symbol('a') + Symbol('c')
        )
        assert ls1[10] == Assignment(
            Variable(Symbol('s')),
            Symbol('p') + Symbol('q') + Symbol('r')
        )


    def test_binop_sub():
        src1 = (
            src +
            """\
            c = a - b
            d = a - c
            s = p - q - r
            """
        )
        expr1.convert_to_expr(src1, 'f')
        ls1 = expr1.return_expr()
        for iter in range(8, 11):
            assert isinstance(ls1[iter], Assignment)
        assert ls1[8] == Assignment(
            Variable(Symbol('c')),
            Symbol('a') - Symbol('b')
        )
        assert ls1[9] == Assignment(
            Variable(Symbol('d')),
            Symbol('a') - Symbol('c')
        )
        assert ls1[10] == Assignment(
            Variable(Symbol('s')),
            Symbol('p') - Symbol('q') - Symbol('r')
        )


    def test_binop_mul():
        """
        Test the binary multiplication operation in the expression converter.
        
        This function tests the conversion of binary multiplication operations in the expression converter. It takes a source code string with specified variables and operations, converts it to an expression, and checks the resulting assignments.
        
        Parameters:
        None
        
        Returns:
        None
        
        Example:
        Given the source code:
        src = (
        src +
        """

        src1 = (
            src +
            """\
            c = a * b
            d = a * c
            s = p * q * r
            """
        )
        expr1.convert_to_expr(src1, 'f')
        ls1 = expr1.return_expr()
        for iter in range(8, 11):
            assert isinstance(ls1[iter], Assignment)
        assert ls1[8] == Assignment(
            Variable(Symbol('c')),
            Symbol('a') * Symbol('b')
        )
        assert ls1[9] == Assignment(
            Variable(Symbol('d')),
            Symbol('a') * Symbol('c')
        )
        assert ls1[10] == Assignment(
            Variable(Symbol('s')),
            Symbol('p') * Symbol('q') * Symbol('r')
        )


    def test_binop_div():
        src1 = (
            src +
            """\
            c = a / b
            d = a / c
            s = p / q
            r = q / p
            """
        )
        expr1.convert_to_expr(src1, 'f')
        ls1 = expr1.return_expr()
        for iter in range(8, 12):
            assert isinstance(ls1[iter], Assignment)
        assert ls1[8] == Assignment(
            Variable(Symbol('c')),
            Symbol('a') / Symbol('b')
        )
        assert ls1[9] == Assignment(
            Variable(Symbol('d')),
            Symbol('a') / Symbol('c')
        )
        assert ls1[10] == Assignment(
            Variable(Symbol('s')),
            Symbol('p') / Symbol('q')
        )
        assert ls1[11] == Assignment(
            Variable(Symbol('r')),
            Symbol('q') / Symbol('p')
        )

    def test_mul_binop():
        src1 = (
            src +
            """\
            d = a + b - c
            c = a * b + d
            s = p * q / r
            r = p * s + q / p
            """
        )
        expr1.convert_to_expr(src1, 'f')
        ls1 = expr1.return_expr()
        for iter in range(8, 12):
            assert isinstance(ls1[iter], Assignment)
        assert ls1[8] == Assignment(
            Variable(Symbol('d')),
            Symbol('a') + Symbol('b') - Symbol('c')
        )
        assert ls1[9] == Assignment(
            Variable(Symbol('c')),
            Symbol('a') * Symbol('b') + Symbol('d')
        )
        assert ls1[10] == Assignment(
            Variable(Symbol('s')),
            Symbol('p') * Symbol('q') / Symbol('r')
        )
        assert ls1[11] == Assignment(
            Variable(Symbol('r')),
            Symbol('p') * Symbol('s') + Symbol('q') / Symbol('p')
        )


    def test_function():
        src1 = """\
        integer function f(a,b)
        integer :: x, y
        f = x + y
        end function
        """
        expr1.convert_to_expr(src1, 'f')
        for iter in expr1.return_expr():
            assert isinstance(iter, FunctionDefinition)
            assert iter == FunctionDefinition(
                IntBaseType(String('integer')),
                name=String('f'),
                parameters=(
                    Variable(Symbol('a')),
                    Variable(Symbol('b'))
                ),
                body=CodeBlock(
                    Declaration(
                        Variable(
                            Symbol('a'),
                            type=IntBaseType(String('integer')),
                            value=Integer(0)
                        )
                    ),
                    Declaration(
                        Variable(
                            Symbol('b'),
                            type=IntBaseType(String('integer')),
                            value=Integer(0)
                        )
                    ),
                    Declaration(
                        Variable(
                            Symbol('f'),
                            type=IntBaseType(String('integer')),
                            value=Integer(0)
                        )
                    ),
                    Declaration(
                        Variable(
                            Symbol('x'),
                            type=IntBaseType(String('integer')),
                            value=Integer(0)
                        )
                    ),
                    Declaration(
                        Variable(
                            Symbol('y'),
                            type=IntBaseType(String('integer')),
                            value=Integer(0)
                        )
                    ),
                    Assignment(
                        Variable(Symbol('f')),
                        Add(Symbol('x'), Symbol('y'))
                    ),
                    Return(Variable(Symbol('f')))
                )
            )


    def test_var():
        expr1.convert_to_expr(src, 'f')
        ls = expr1.return_expr()
        for iter in expr1.return_expr():
            assert isinstance(iter, Declaration)
        assert ls[0] == Declaration(
            Variable(
                Symbol('a'),
                type = IntBaseType(String('integer')),
                value = Integer(0)
            )
        )
        assert ls[1] == Declaration(
            Variable(
                Symbol('b'),
                type = IntBaseType(String('integer')),
                value = Integer(0)
            )
        )
        assert ls[2] == Declaration(
            Variable(
                Symbol('c'),
                type = IntBaseType(String('integer')),
                value = Integer(0)
            )
        )
        assert ls[3] == Declaration(
            Variable(
                Symbol('d'),
                type = IntBaseType(String('integer')),
                value = Integer(0)
            )
        )
        assert ls[4] == Declaration(
            Variable(
                Symbol('p'),
                type = FloatBaseType(String('real')),
                value = Float(0.0)
            )
        )
        assert ls[5] == Declaration(
            Variable(
                Symbol('q'),
                type = FloatBaseType(String('real')),
                value = Float(0.0)
            )
        )
        assert ls[6] == Declaration(
            Variable(
                Symbol('r'),
                type = FloatBaseType(String('real')),
                value = Float(0.0)
            )
        )
        assert ls[7] == Declaration(
            Variable(
                Symbol('s'),
                type = FloatBaseType(String('real')),
                value = Float(0.0)
            )
        )

else:
    def test_raise():
        from sympy.parsing.fortran.fortran_parser import ASR2PyVisitor
        raises(ImportError, lambda: ASR2PyVisitor())
        raises(ImportError, lambda: SymPyExpression(' ', mode = 'f'))
mport ASR2PyVisitor
        raises(ImportError, lambda: ASR2PyVisitor())
        raises(ImportError, lambda: SymPyExpression(' ', mode = 'f'))
