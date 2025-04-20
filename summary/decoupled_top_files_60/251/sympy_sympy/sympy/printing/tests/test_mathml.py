from sympy import diff, Integral, Limit, sin, Symbol, Integer, Rational, cos, \
    tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh, E, I, oo, \
    pi, GoldenRatio, EulerGamma, Sum, Eq, Ne, Ge, Lt, Float, Matrix
from sympy.printing.mathml import mathml, MathMLContentPrinter, MathMLPresentationPrinter, \
    MathMLPrinter

from sympy.utilities.pytest import raises

x = Symbol('x')
y = Symbol('y')
mp = MathMLContentPrinter()
mpp = MathMLPresentationPrinter()

def test_mathml_printer():
    m = MathMLPrinter()
    assert m.doprint(1+x) == mp.doprint(1+x)


def test_content_printmethod():
    assert mp.doprint(1 + x) == '<apply><plus/><ci>x</ci><cn>1</cn></apply>'


def test_content_mathml_core():
    """
    Test content MathML generation for basic expressions.
    
    This function checks the MathML representation of various basic mathematical expressions.
    
    Parameters:
    None
    
    Returns:
    None
    """

    mml_1 = mp._print(1 + x)
    assert mml_1.nodeName == 'apply'
    nodes = mml_1.childNodes
    assert len(nodes) == 3
    assert nodes[0].nodeName == 'plus'
    assert nodes[0].hasChildNodes() is False
    assert nodes[0].nodeValue is None
    assert nodes[1].nodeName in ['cn', 'ci']
    if nodes[1].nodeName == 'cn':
        assert nodes[1].childNodes[0].nodeValue == '1'
        assert nodes[2].childNodes[0].nodeValue == 'x'
    else:
        assert nodes[1].childNodes[0].nodeValue == 'x'
        assert nodes[2].childNodes[0].nodeValue == '1'

    mml_2 = mp._print(x**2)
    assert mml_2.nodeName == 'apply'
    nodes = mml_2.childNodes
    assert nodes[1].childNodes[0].nodeValue == 'x'
    assert nodes[2].childNodes[0].nodeValue == '2'

    mml_3 = mp._print(2*x)
    assert mml_3.nodeName == 'apply'
    nodes = mml_3.childNodes
    assert nodes[0].nodeName == 'times'
    assert nodes[1].childNodes[0].nodeValue == '2'
    assert nodes[2].childNodes[0].nodeValue == 'x'

    mml = mp._print(Float(1.0, 2)*x)
    assert mml.nodeName == 'apply'
    nodes = mml.childNodes
    assert nodes[0].nodeName == 'times'
    assert nodes[1].childNodes[0].nodeValue == '1.0'
    assert nodes[2].childNodes[0].nodeValue == 'x'


def test_content_mathml_functions():
    mml_1 = mp._print(sin(x))
    assert mml_1.nodeName == 'apply'
    assert mml_1.childNodes[0].nodeName == 'sin'
    assert mml_1.childNodes[1].nodeName == 'ci'

    mml_2 = mp._print(diff(sin(x), x, evaluate=False))
    assert mml_2.nodeName == 'apply'
    assert mml_2.childNodes[0].nodeName == 'diff'
    assert mml_2.childNodes[1].nodeName == 'bvar'
    assert mml_2.childNodes[1].childNodes[
        0].nodeName == 'ci'  # below bvar there's <ci>x/ci>

    mml_3 = mp._print(diff(cos(x*y), x, evaluate=False))
    assert mml_3.nodeName == 'apply'
    assert mml_3.childNodes[0].nodeName == 'partialdiff'
    assert mml_3.childNodes[1].nodeName == 'bvar'
    assert mml_3.childNodes[1].childNodes[
        0].nodeName == 'ci'  # below bvar there's <ci>x/ci>


def test_content_mathml_limits():
    # XXX No unevaluated limits
    lim_fun = sin(x)/x
    mml_1 = mp._print(Limit(lim_fun, x, 0))
    assert mml_1.childNodes[0].nodeName == 'limit'
    assert mml_1.childNodes[1].nodeName == 'bvar'
    assert mml_1.childNodes[2].nodeName == 'lowlimit'
    assert mml_1.childNodes[3].toxml() == mp._print(lim_fun).toxml()


def test_content_mathml_integrals():
    integrand = x
    mml_1 = mp._print(Integral(integrand, (x, 0, 1)))
    assert mml_1.childNodes[0].nodeName == 'int'
    assert mml_1.childNodes[1].nodeName == 'bvar'
    assert mml_1.childNodes[2].nodeName == 'lowlimit'
    assert mml_1.childNodes[3].nodeName == 'uplimit'
    assert mml_1.childNodes[4].toxml() == mp._print(integrand).toxml()

def test_content_mathml_matrices():
    A = Matrix([1, 2, 3])
    B = Matrix([[0, 5, 4], [2, 3, 1], [9, 7, 9]])
    mll_1 = mp._print(A)
    assert mll_1.childNodes[0].nodeName == 'matrixrow'
    assert mll_1.childNodes[0].childNodes[0].nodeName == 'cn'
    assert mll_1.childNodes[0].childNodes[0].childNodes[0].nodeValue == '1'
    assert mll_1.childNodes[1].nodeName == 'matrixrow'
    assert mll_1.childNodes[1].childNodes[0].nodeName == 'cn'
    assert mll_1.childNodes[1].childNodes[0].childNodes[0].nodeValue == '2'
    assert mll_1.childNodes[2].nodeName == 'matrixrow'
    assert mll_1.childNodes[2].childNodes[0].nodeName == 'cn'
    assert mll_1.childNodes[2].childNodes[0].childNodes[0].nodeValue == '3'
    mll_2 = mp._print(B)
    assert mll_2.childNodes[0].nodeName == 'matrixrow'
    assert mll_2.childNodes[0].childNodes[0].nodeName == 'cn'
    assert mll_2.childNodes[0].childNodes[0].childNodes[0].nodeValue == '0'
    assert mll_2.childNodes[0].childNodes[1].nodeName == 'cn'
    assert mll_2.childNodes[0].childNodes[1].childNodes[0].nodeValue == '5'
    assert mll_2.childNodes[0].childNodes[2].nodeName == 'cn'
    assert mll_2.childNodes[0].childNodes[2].childNodes[0].nodeValue == '4'
    assert mll_2.childNodes[1].nodeName == 'matrixrow'
    assert mll_2.childNodes[1].childNodes[0].nodeName == 'cn'
    assert mll_2.childNodes[1].childNodes[0].childNodes[0].nodeValue == '2'
    assert mll_2.childNodes[1].childNodes[1].nodeName == 'cn'
    assert mll_2.childNodes[1].childNodes[1].childNodes[0].nodeValue == '3'
    assert mll_2.childNodes[1].childNodes[2].nodeName == 'cn'
    assert mll_2.childNodes[1].childNodes[2].childNodes[0].nodeValue == '1'
    assert mll_2.childNodes[2].nodeName == 'matrixrow'
    assert mll_2.childNodes[2].childNodes[0].nodeName == 'cn'
    assert mll_2.childNodes[2].childNodes[0].childNodes[0].nodeValue == '9'
    assert mll_2.childNodes[2].childNodes[1].nodeName == 'cn'
    assert mll_2.childNodes[2].childNodes[1].childNodes[0].nodeValue == '7'
    assert mll_2.childNodes[2].childNodes[2].nodeName == 'cn'
    assert mll_2.childNodes[2].childNodes[2].childNodes[0].nodeValue == '9'

def test_content_mathml_sums():
    summand = x
    mml_1 = mp._print(Sum(summand, (x, 1, 10)))
    assert mml_1.childNodes[0].nodeName == 'sum'
    assert mml_1.childNodes[1].nodeName == 'bvar'
    assert mml_1.childNodes[2].nodeName == 'lowlimit'
    assert mml_1.childNodes[3].nodeName == 'uplimit'
    assert mml_1.childNodes[4].toxml() == mp._print(summand).toxml()


def test_content_mathml_tuples():
    mml_1 = mp._print([2])
    assert mml_1.nodeName == 'list'
    assert mml_1.childNodes[0].nodeName == 'cn'
    assert len(mml_1.childNodes) == 1

    mml_2 = mp._print([2, Integer(1)])
    assert mml_2.nodeName == 'list'
    assert mml_2.childNodes[0].nodeName == 'cn'
    assert mml_2.childNodes[1].nodeName == 'cn'
    assert len(mml_2.childNodes) == 2


def test_content_mathml_add():
    mml = mp._print(x**5 - x**4 + x)
    assert mml.childNodes[0].nodeName == 'plus'
    assert mml.childNodes[1].childNodes[0].nodeName == 'minus'
    assert mml.childNodes[1].childNodes[1].nodeName == 'apply'


def test_content_mathml_Rational():
    mml_1 = mp._print(Rational(1, 1))
    """should just return a number"""
    assert mml_1.nodeName == 'cn'

    mml_2 = mp._print(Rational(2, 5))
    assert mml_2.childNodes[0].nodeName == 'divide'


def test_content_mathml_constants():
    """
    Test content MathML representation of mathematical constants.
    
    This function checks the MathML representation of several important mathematical constants and symbols:
    - Imaginary unit (I)
    - Exponential base (E)
    - Positive infinity (oo)
    - Pi (π)
    - Golden ratio (GoldenRatio)
    - Euler-Mascheroni constant (EulerGamma)
    
    Parameters:
    None
    
    Returns:
    None
    
    Asserts:
    - The MathML representation of the imaginary unit is 'imaginaryi'
    - The MathML representation of
    """

    mml = mp._print(I)
    assert mml.nodeName == 'imaginaryi'

    mml = mp._print(E)
    assert mml.nodeName == 'exponentiale'

    mml = mp._print(oo)
    assert mml.nodeName == 'infinity'

    mml = mp._print(pi)
    assert mml.nodeName == 'pi'

    assert mathml(GoldenRatio) == '<cn>&#966;</cn>'

    mml = mathml(EulerGamma)
    assert mml == '<eulergamma/>'


def test_content_mathml_trig():
    mml = mp._print(sin(x))
    assert mml.childNodes[0].nodeName == 'sin'

    mml = mp._print(cos(x))
    assert mml.childNodes[0].nodeName == 'cos'

    mml = mp._print(tan(x))
    assert mml.childNodes[0].nodeName == 'tan'

    mml = mp._print(asin(x))
    assert mml.childNodes[0].nodeName == 'arcsin'

    mml = mp._print(acos(x))
    assert mml.childNodes[0].nodeName == 'arccos'

    mml = mp._print(atan(x))
    assert mml.childNodes[0].nodeName == 'arctan'

    mml = mp._print(sinh(x))
    assert mml.childNodes[0].nodeName == 'sinh'

    mml = mp._print(cosh(x))
    assert mml.childNodes[0].nodeName == 'cosh'

    mml = mp._print(tanh(x))
    assert mml.childNodes[0].nodeName == 'tanh'

    mml = mp._print(asinh(x))
    assert mml.childNodes[0].nodeName == 'arcsinh'

    mml = mp._print(atanh(x))
    assert mml.childNodes[0].nodeName == 'arctanh'

    mml = mp._print(acosh(x))
    assert mml.childNodes[0].nodeName == 'arccosh'


def test_content_mathml_relational():
    mml_1 = mp._print(Eq(x, 1))
    assert mml_1.nodeName == 'apply'
    assert mml_1.childNodes[0].nodeName == 'eq'
    assert mml_1.childNodes[1].nodeName == 'ci'
    assert mml_1.childNodes[1].childNodes[0].nodeValue == 'x'
    assert mml_1.childNodes[2].nodeName == 'cn'
    assert mml_1.childNodes[2].childNodes[0].nodeValue == '1'

    mml_2 = mp._print(Ne(1, x))
    assert mml_2.nodeName == 'apply'
    assert mml_2.childNodes[0].nodeName == 'neq'
    assert mml_2.childNodes[1].nodeName == 'cn'
    assert mml_2.childNodes[1].childNodes[0].nodeValue == '1'
    assert mml_2.childNodes[2].nodeName == 'ci'
    assert mml_2.childNodes[2].childNodes[0].nodeValue == 'x'

    mml_3 = mp._print(Ge(1, x))
    assert mml_3.nodeName == 'apply'
    assert mml_3.childNodes[0].nodeName == 'geq'
    assert mml_3.childNodes[1].nodeName == 'cn'
    assert mml_3.childNodes[1].childNodes[0].nodeValue == '1'
    assert mml_3.childNodes[2].nodeName == 'ci'
    assert mml_3.childNodes[2].childNodes[0].nodeValue == 'x'

    mml_4 = mp._print(Lt(1, x))
    assert mml_4.nodeName == 'apply'
    assert mml_4.childNodes[0].nodeName == 'lt'
    assert mml_4.childNodes[1].nodeName == 'cn'
    assert mml_4.childNodes[1].childNodes[0].nodeValue == '1'
    assert mml_4.childNodes[2].nodeName == 'ci'
    assert mml_4.childNodes[2].childNodes[0].nodeValue == 'x'


def test_content_symbol():
    mml = mp._print(Symbol("x"))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeValue == 'x'
    del mml

    mml = mp._print(Symbol("x^2"))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeName == 'mml:msup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    del mml

    mml = mp._print(Symbol("x__2"))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeName == 'mml:msup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    del mml

    mml = mp._print(Symbol("x_2"))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeName == 'mml:msub'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    del mml

    mml = mp._print(Symbol("x^3_2"))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeName == 'mml:msubsup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    assert mml.childNodes[0].childNodes[2].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[2].childNodes[0].nodeValue == '3'
    del mml

    mml = mp._print(Symbol("x__3_2"))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeName == 'mml:msubsup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    assert mml.childNodes[0].childNodes[2].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[2].childNodes[0].nodeValue == '3'
    del mml

    mml = mp._print(Symbol("x_2_a"))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeName == 'mml:msub'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mml:mrow'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].childNodes[
        0].nodeValue == '2'
    assert mml.childNodes[0].childNodes[1].childNodes[1].nodeName == 'mml:mo'
    assert mml.childNodes[0].childNodes[1].childNodes[1].childNodes[
        0].nodeValue == ' '
    assert mml.childNodes[0].childNodes[1].childNodes[2].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[2].childNodes[
        0].nodeValue == 'a'
    del mml

    mml = mp._print(Symbol("x^2^a"))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeName == 'mml:msup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mml:mrow'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].childNodes[
        0].nodeValue == '2'
    assert mml.childNodes[0].childNodes[1].childNodes[1].nodeName == 'mml:mo'
    assert mml.childNodes[0].childNodes[1].childNodes[1].childNodes[
        0].nodeValue == ' '
    assert mml.childNodes[0].childNodes[1].childNodes[2].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[2].childNodes[
        0].nodeValue == 'a'
    del mml

    mml = mp._print(Symbol("x__2__a"))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeName == 'mml:msup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mml:mrow'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].childNodes[
        0].nodeValue == '2'
    assert mml.childNodes[0].childNodes[1].childNodes[1].nodeName == 'mml:mo'
    assert mml.childNodes[0].childNodes[1].childNodes[1].childNodes[
        0].nodeValue == ' '
    assert mml.childNodes[0].childNodes[1].childNodes[2].nodeName == 'mml:mi'
    assert mml.childNodes[0].childNodes[1].childNodes[2].childNodes[
        0].nodeValue == 'a'
    del mml


def test_content_mathml_greek():
    mml = mp._print(Symbol('alpha'))
    assert mml.nodeName == 'ci'
    assert mml.childNodes[0].nodeValue == u'\N{GREEK SMALL LETTER ALPHA}'

    assert mp.doprint(Symbol('alpha')) == '<ci>&#945;</ci>'
    assert mp.doprint(Symbol('beta')) == '<ci>&#946;</ci>'
    assert mp.doprint(Symbol('gamma')) == '<ci>&#947;</ci>'
    assert mp.doprint(Symbol('delta')) == '<ci>&#948;</ci>'
    assert mp.doprint(Symbol('epsilon')) == '<ci>&#949;</ci>'
    assert mp.doprint(Symbol('zeta')) == '<ci>&#950;</ci>'
    assert mp.doprint(Symbol('eta')) == '<ci>&#951;</ci>'
    assert mp.doprint(Symbol('theta')) == '<ci>&#952;</ci>'
    assert mp.doprint(Symbol('iota')) == '<ci>&#953;</ci>'
    assert mp.doprint(Symbol('kappa')) == '<ci>&#954;</ci>'
    assert mp.doprint(Symbol('lambda')) == '<ci>&#955;</ci>'
    assert mp.doprint(Symbol('mu')) == '<ci>&#956;</ci>'
    assert mp.doprint(Symbol('nu')) == '<ci>&#957;</ci>'
    assert mp.doprint(Symbol('xi')) == '<ci>&#958;</ci>'
    assert mp.doprint(Symbol('omicron')) == '<ci>&#959;</ci>'
    assert mp.doprint(Symbol('pi')) == '<ci>&#960;</ci>'
    assert mp.doprint(Symbol('rho')) == '<ci>&#961;</ci>'
    assert mp.doprint(Symbol('varsigma')) == '<ci>&#962;</ci>', mp.doprint(Symbol('varsigma'))
    assert mp.doprint(Symbol('sigma')) == '<ci>&#963;</ci>'
    assert mp.doprint(Symbol('tau')) == '<ci>&#964;</ci>'
    assert mp.doprint(Symbol('upsilon')) == '<ci>&#965;</ci>'
    assert mp.doprint(Symbol('phi')) == '<ci>&#966;</ci>'
    assert mp.doprint(Symbol('chi')) == '<ci>&#967;</ci>'
    assert mp.doprint(Symbol('psi')) == '<ci>&#968;</ci>'
    assert mp.doprint(Symbol('omega')) == '<ci>&#969;</ci>'

    assert mp.doprint(Symbol('Alpha')) == '<ci>&#913;</ci>'
    assert mp.doprint(Symbol('Beta')) == '<ci>&#914;</ci>'
    assert mp.doprint(Symbol('Gamma')) == '<ci>&#915;</ci>'
    assert mp.doprint(Symbol('Delta')) == '<ci>&#916;</ci>'
    assert mp.doprint(Symbol('Epsilon')) == '<ci>&#917;</ci>'
    assert mp.doprint(Symbol('Zeta')) == '<ci>&#918;</ci>'
    assert mp.doprint(Symbol('Eta')) == '<ci>&#919;</ci>'
    assert mp.doprint(Symbol('Theta')) == '<ci>&#920;</ci>'
    assert mp.doprint(Symbol('Iota')) == '<ci>&#921;</ci>'
    assert mp.doprint(Symbol('Kappa')) == '<ci>&#922;</ci>'
    assert mp.doprint(Symbol('Lambda')) == '<ci>&#923;</ci>'
    assert mp.doprint(Symbol('Mu')) == '<ci>&#924;</ci>'
    assert mp.doprint(Symbol('Nu')) == '<ci>&#925;</ci>'
    assert mp.doprint(Symbol('Xi')) == '<ci>&#926;</ci>'
    assert mp.doprint(Symbol('Omicron')) == '<ci>&#927;</ci>'
    assert mp.doprint(Symbol('Pi')) == '<ci>&#928;</ci>'
    assert mp.doprint(Symbol('Rho')) == '<ci>&#929;</ci>'
    assert mp.doprint(Symbol('Sigma')) == '<ci>&#931;</ci>'
    assert mp.doprint(Symbol('Tau')) == '<ci>&#932;</ci>'
    assert mp.doprint(Symbol('Upsilon')) == '<ci>&#933;</ci>'
    assert mp.doprint(Symbol('Phi')) == '<ci>&#934;</ci>'
    assert mp.doprint(Symbol('Chi')) == '<ci>&#935;</ci>'
    assert mp.doprint(Symbol('Psi')) == '<ci>&#936;</ci>'
    assert mp.doprint(Symbol('Omega')) == '<ci>&#937;</ci>'


def test_content_mathml_order():
    """
    Test the order of terms in MathML output for a given expression.
    
    This function checks the order of terms in the MathML representation of a polynomial expression
    when printed using the MathMLContentPrinter with different order specifications.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses the `MathMLContentPrinter` to generate MathML from a polynomial expression.
    - Two different order specifications ('lex' and 'rev-lex') are tested.
    - The function
    """

    expr = x**3 + x**2*y + 3*x*y**3 + y**4

    mp = MathMLContentPrinter({'order': 'lex'})
    mml = mp._print(expr)

    assert mml.childNodes[1].childNodes[0].nodeName == 'power'
    assert mml.childNodes[1].childNodes[1].childNodes[0].data == 'x'
    assert mml.childNodes[1].childNodes[2].childNodes[0].data == '3'

    assert mml.childNodes[4].childNodes[0].nodeName == 'power'
    assert mml.childNodes[4].childNodes[1].childNodes[0].data == 'y'
    assert mml.childNodes[4].childNodes[2].childNodes[0].data == '4'

    mp = MathMLContentPrinter({'order': 'rev-lex'})
    mml = mp._print(expr)

    assert mml.childNodes[1].childNodes[0].nodeName == 'power'
    assert mml.childNodes[1].childNodes[1].childNodes[0].data == 'y'
    assert mml.childNodes[1].childNodes[2].childNodes[0].data == '4'

    assert mml.childNodes[4].childNodes[0].nodeName == 'power'
    assert mml.childNodes[4].childNodes[1].childNodes[0].data == 'x'
    assert mml.childNodes[4].childNodes[2].childNodes[0].data == '3'


def test_content_settings():
    raises(TypeError, lambda: mathml(Symbol("x"), method="garbage"))


def test_presentation_printmethod():
    assert mpp.doprint(1 + x) == '<mrow><mi>x</mi><mo>+</mo><mn>1</mn></mrow>'
    assert mpp.doprint(x**2) == '<msup><mi>x</mi><mn>2</mn></msup>'
    assert mpp.doprint(2*x) == '<mrow><mn>2</mn><mo>&InvisibleTimes;</mo><mi>x</mi></mrow>'


def test_presentation_mathml_core():
    """
    Test the MathML representation of basic mathematical expressions.
    
    This function checks the MathML representation of various basic mathematical expressions, including addition, exponentiation, and multiplication. It ensures that the MathML nodes are correctly structured and contain the expected values.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Assertions:
    - The MathML representation of `1 + x` is correct.
    - The MathML representation of `x**2` is correct.
    - The MathML representation of `2*x` is correct
    """

    mml_1 = mpp._print(1 + x)
    assert mml_1.nodeName == 'mrow'
    nodes = mml_1.childNodes
    assert len(nodes) == 3
    assert nodes[0].nodeName in ['mi', 'mn']
    assert nodes[1].nodeName == 'mo'
    if nodes[0].nodeName == 'mn':
        assert nodes[0].childNodes[0].nodeValue == '1'
        assert nodes[2].childNodes[0].nodeValue == 'x'
    else:
        assert nodes[0].childNodes[0].nodeValue == 'x'
        assert nodes[2].childNodes[0].nodeValue == '1'

    mml_2 = mpp._print(x**2)
    assert mml_2.nodeName == 'msup'
    nodes = mml_2.childNodes
    assert nodes[0].childNodes[0].nodeValue == 'x'
    assert nodes[1].childNodes[0].nodeValue == '2'

    mml_3 = mpp._print(2*x)
    assert mml_3.nodeName == 'mrow'
    nodes = mml_3.childNodes
    assert nodes[0].childNodes[0].nodeValue == '2'
    assert nodes[1].childNodes[0].nodeValue == '&InvisibleTimes;'
    assert nodes[2].childNodes[0].nodeValue == 'x'

    mml = mpp._print(Float(1.0, 2)*x)
    assert mml.nodeName == 'mrow'
    nodes = mml.childNodes
    assert nodes[0].childNodes[0].nodeValue == '1.0'
    assert nodes[1].childNodes[0].nodeValue == '&InvisibleTimes;'
    assert nodes[2].childNodes[0].nodeValue == 'x'


def test_presentation_mathml_functions():
    """
    Test the MathML printing functions for symbolic mathematics.
    
    This function checks the MathML representation of symbolic expressions and their derivatives.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The MathML representation of `sin(x)` should have the correct structure.
    - The MathML representation of the derivative of `sin(x)` with respect to `x` should have the correct structure.
    - The MathML representation of the derivative of `cos(x*y)` with respect to `x`
    """

    mml_1 = mpp._print(sin(x))
    assert mml_1.childNodes[0].childNodes[0
        ].nodeValue == 'sin'
    assert mml_1.childNodes[1].childNodes[0
        ].childNodes[0].nodeValue == 'x'

    mml_2 = mpp._print(diff(sin(x), x, evaluate=False))
    assert mml_2.nodeName == 'mfrac'
    assert mml_2.childNodes[0].childNodes[0
        ].childNodes[0].nodeValue == '&dd;'
    assert mml_2.childNodes[0].childNodes[1
        ].nodeName == 'mfenced'
    assert mml_2.childNodes[1].childNodes[
        0].childNodes[0].nodeValue == '&dd;'

    mml_3 = mpp._print(diff(cos(x*y), x, evaluate=False))
    assert mml_3.nodeName == 'mfrac'
    assert mml_3.childNodes[0].childNodes[0
        ].childNodes[0].nodeValue == '&#x2202;'
    assert mml_2.childNodes[0].childNodes[1
        ].nodeName == 'mfenced'
    assert mml_3.childNodes[1].childNodes[
        0].childNodes[0].nodeValue == '&#x2202;'


def test_presentation_mathml_limits():
    lim_fun = sin(x)/x
    mml_1 = mpp._print(Limit(lim_fun, x, 0))
    assert mml_1.childNodes[0].nodeName == 'munder'
    assert mml_1.childNodes[0].childNodes[0
        ].childNodes[0].nodeValue == 'lim'
    assert mml_1.childNodes[0].childNodes[1
        ].childNodes[0].childNodes[0
        ].nodeValue == 'x'
    assert mml_1.childNodes[0].childNodes[1
        ].childNodes[1].childNodes[0
        ].nodeValue == '&#x2192;'
    assert mml_1.childNodes[0].childNodes[1
        ].childNodes[2].childNodes[0
        ].nodeValue == '0'


def test_presentation_mathml_integrals():
    integrand = x
    mml_1 = mpp._print(Integral(integrand, (x, 0, 1)))
    assert mml_1.childNodes[0].nodeName == 'msubsup'
    assert len(mml_1.childNodes[0].childNodes) == 3
    assert mml_1.childNodes[0].childNodes[0
        ].childNodes[0].nodeValue == '&int;'
    assert mml_1.childNodes[0].childNodes[1
        ].childNodes[0].nodeValue == '0'
    assert mml_1.childNodes[0].childNodes[2
        ].childNodes[0].nodeValue == '1'


def test_presentation_mathml_matrices():
    A = Matrix([1, 2, 3])
    B = Matrix([[0, 5, 4], [2, 3, 1], [9, 7, 9]])
    mll_1 = mpp._print(A)
    assert mll_1.childNodes[0].nodeName == 'mtable'
    assert mll_1.childNodes[0].childNodes[0].nodeName == 'mtr'
    assert len(mll_1.childNodes[0].childNodes) == 3
    assert mll_1.childNodes[0].childNodes[0].childNodes[0].nodeName == 'mtd'
    assert len(mll_1.childNodes[0].childNodes[0].childNodes) == 1
    assert mll_1.childNodes[0].childNodes[0].childNodes[0
        ].childNodes[0].childNodes[0].nodeValue == '1'
    assert mll_1.childNodes[0].childNodes[1].childNodes[0
        ].childNodes[0].childNodes[0].nodeValue == '2'
    assert mll_1.childNodes[0].childNodes[2].childNodes[0
        ].childNodes[0].childNodes[0].nodeValue == '3'
    mll_2 = mpp._print(B)
    assert mll_2.childNodes[0].nodeName == 'mtable'
    assert mll_2.childNodes[0].childNodes[0].nodeName == 'mtr'
    assert len(mll_2.childNodes[0].childNodes) == 3
    assert mll_2.childNodes[0].childNodes[0].childNodes[0].nodeName == 'mtd'
    assert len(mll_2.childNodes[0].childNodes[0].childNodes) == 3
    assert mll_2.childNodes[0].childNodes[0].childNodes[0
        ].childNodes[0].childNodes[0].nodeValue == '0'
    assert mll_2.childNodes[0].childNodes[0].childNodes[1
        ].childNodes[0].childNodes[0].nodeValue == '5'
    assert mll_2.childNodes[0].childNodes[0].childNodes[2
        ].childNodes[0].childNodes[0].nodeValue == '4'
    assert mll_2.childNodes[0].childNodes[1].childNodes[0
        ].childNodes[0].childNodes[0].nodeValue == '2'
    assert mll_2.childNodes[0].childNodes[1].childNodes[1
        ].childNodes[0].childNodes[0].nodeValue == '3'
    assert mll_2.childNodes[0].childNodes[1].childNodes[2
        ].childNodes[0].childNodes[0].nodeValue == '1'
    assert mll_2.childNodes[0].childNodes[2].childNodes[0
        ].childNodes[0].childNodes[0].nodeValue == '9'
    assert mll_2.childNodes[0].childNodes[2].childNodes[1
        ].childNodes[0].childNodes[0].nodeValue == '7'
    assert mll_2.childNodes[0].childNodes[2].childNodes[2
        ].childNodes[0].childNodes[0].nodeValue == '9'


def test_presentation_mathml_sums():
    summand = x
    mml_1 = mpp._print(Sum(summand, (x, 1, 10)))
    assert mml_1.childNodes[0].nodeName == 'munderover'
    assert len(mml_1.childNodes[0].childNodes) == 3
    assert mml_1.childNodes[0].childNodes[0].childNodes[0
        ].nodeValue == '&#x2211;'
    assert len(mml_1.childNodes[0].childNodes[1].childNodes) == 3
    assert mml_1.childNodes[0].childNodes[2].childNodes[0
        ].nodeValue == '10'
    assert mml_1.childNodes[1].childNodes[0].nodeValue == 'x'


def test_presentation_mathml_add():
    """
    Test the mathematical expression rendering for a polynomial using MathML.
    
    This function checks the rendering of a polynomial expression `x**5 - x**4 + x`
    into MathML format. It verifies that the MathML output contains the correct
    number of nodes and that each node correctly represents the corresponding
    term in the polynomial.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The MathML output should contain 5 nodes.
    - The first node should represent `x^5
    """

    mml = mpp._print(x**5 - x**4 + x)
    assert len(mml.childNodes) == 5
    assert mml.childNodes[0].childNodes[0].childNodes[0
        ].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].childNodes[0
        ].nodeValue == '5'
    assert mml.childNodes[1].childNodes[0].nodeValue == '-'
    assert mml.childNodes[2].childNodes[0].childNodes[0
        ].nodeValue == 'x'
    assert mml.childNodes[2].childNodes[1].childNodes[0
        ].nodeValue == '4'
    assert mml.childNodes[3].childNodes[0].nodeValue == '+'
    assert mml.childNodes[4].childNodes[0].nodeValue == 'x'


def test_presentation_mathml_Rational():
    mml_1 = mpp._print(Rational(1, 1))
    assert mml_1.nodeName == 'mn'

    mml_2 = mpp._print(Rational(2, 5))
    assert mml_2.nodeName == 'mfrac'
    assert mml_2.childNodes[0].childNodes[0].nodeValue == '2'
    assert mml_2.childNodes[1].childNodes[0].nodeValue == '5'


def test_presentation_mathml_constants():
    mml = mpp._print(I)
    assert mml.childNodes[0].nodeValue == '&ImaginaryI;'

    mml = mpp._print(E)
    assert mml.childNodes[0].nodeValue == '&ExponentialE;'

    mml = mpp._print(oo)
    assert mml.childNodes[0].nodeValue == '&#x221E;'

    mml = mpp._print(pi)
    assert mml.childNodes[0].nodeValue == '&pi;'

    assert mathml(GoldenRatio, printer='presentation') == '<mi>&#966;</mi>'


def test_presentation_mathml_trig():
    mml = mpp._print(sin(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'sin'

    mml = mpp._print(cos(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'cos'

    mml = mpp._print(tan(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'tan'

    mml = mpp._print(asin(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'arcsin'

    mml = mpp._print(acos(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'arccos'

    mml = mpp._print(atan(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'arctan'

    mml = mpp._print(sinh(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'sinh'

    mml = mpp._print(cosh(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'cosh'

    mml = mpp._print(tanh(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'tanh'

    mml = mpp._print(asinh(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'arcsinh'

    mml = mpp._print(atanh(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'arctanh'

    mml = mpp._print(acosh(x))
    assert mml.childNodes[0].childNodes[0].nodeValue == 'arccosh'


def test_presentation_mathml_relational():
    """
    Generate MathML representation of relational expressions.
    
    This function takes symbolic expressions and generates their MathML
    representation for relational operations.
    
    Parameters:
    expr (Equality, Inequality, etc.): The symbolic expression to be converted to MathML.
    
    Returns:
    mml (Element): The MathML representation of the expression.
    """

    mml_1 = mpp._print(Eq(x, 1))
    assert len(mml_1.childNodes) == 3
    assert mml_1.childNodes[0].nodeName == 'mi'
    assert mml_1.childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml_1.childNodes[1].nodeName == 'mo'
    assert mml_1.childNodes[1].childNodes[0].nodeValue == '='
    assert mml_1.childNodes[2].nodeName == 'mn'
    assert mml_1.childNodes[2].childNodes[0].nodeValue == '1'

    mml_2 = mpp._print(Ne(1, x))
    assert len(mml_2.childNodes) == 3
    assert mml_2.childNodes[0].nodeName == 'mn'
    assert mml_2.childNodes[0].childNodes[0].nodeValue == '1'
    assert mml_2.childNodes[1].nodeName == 'mo'
    assert mml_2.childNodes[1].childNodes[0].nodeValue == '&#x2260;'
    assert mml_2.childNodes[2].nodeName == 'mi'
    assert mml_2.childNodes[2].childNodes[0].nodeValue == 'x'

    mml_3 = mpp._print(Ge(1, x))
    assert len(mml_3.childNodes) == 3
    assert mml_3.childNodes[0].nodeName == 'mn'
    assert mml_3.childNodes[0].childNodes[0].nodeValue == '1'
    assert mml_3.childNodes[1].nodeName == 'mo'
    assert mml_3.childNodes[1].childNodes[0].nodeValue == '&#x2265;'
    assert mml_3.childNodes[2].nodeName == 'mi'
    assert mml_3.childNodes[2].childNodes[0].nodeValue == 'x'

    mml_4 = mpp._print(Lt(1, x))
    assert len(mml_4.childNodes) == 3
    assert mml_4.childNodes[0].nodeName == 'mn'
    assert mml_4.childNodes[0].childNodes[0].nodeValue == '1'
    assert mml_4.childNodes[1].nodeName == 'mo'
    assert mml_4.childNodes[1].childNodes[0].nodeValue == '<'
    assert mml_4.childNodes[2].nodeName == 'mi'
    assert mml_4.childNodes[2].childNodes[0].nodeValue == 'x'


def test_presentation_symbol():
    mml = mpp._print(Symbol("x"))
    assert mml.nodeName == 'mi'
    assert mml.childNodes[0].nodeValue == 'x'
    del mml

    mml = mpp._print(Symbol("x^2"))
    assert mml.nodeName == 'mi'
    assert mml.childNodes[0].nodeName == 'msup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    del mml

    mml = mpp._print(Symbol("x__2"))
    assert mml.nodeName == 'mi'
    assert mml.childNodes[0].nodeName == 'msup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    del mml

    mml = mpp._print(Symbol("x_2"))
    assert mml.nodeName == 'mi'
    assert mml.childNodes[0].nodeName == 'msub'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    del mml

    mml = mpp._print(Symbol("x^3_2"))
    assert mml.nodeName == 'mi'
    assert mml.childNodes[0].nodeName == 'msubsup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    assert mml.childNodes[0].childNodes[2].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[2].childNodes[0].nodeValue == '3'
    del mml

    mml = mpp._print(Symbol("x__3_2"))
    assert mml.nodeName == 'mi'
    assert mml.childNodes[0].nodeName == 'msubsup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeValue == '2'
    assert mml.childNodes[0].childNodes[2].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[2].childNodes[0].nodeValue == '3'
    del mml

    mml = mpp._print(Symbol("x_2_a"))
    assert mml.nodeName == 'mi'
    assert mml.childNodes[0].nodeName == 'msub'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mrow'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[1].childNodes[0].childNodes[
        0].nodeValue == '2'
    assert mml.childNodes[0].childNodes[1].childNodes[1].nodeName == 'mo'
    assert mml.childNodes[0].childNodes[1].childNodes[1].childNodes[
        0].nodeValue == ' '
    assert mml.childNodes[0].childNodes[1].childNodes[2].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[1].childNodes[2].childNodes[
        0].nodeValue == 'a'
    del mml

    mml = mpp._print(Symbol("x^2^a"))
    assert mml.nodeName == 'mi'
    assert mml.childNodes[0].nodeName == 'msup'
    assert mml.childNodes[0].childNodes[0].nodeName == 'mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    aName == 'mi'
    assert mml.childNodes[0].childNodes[0].childNodes[0].nodeValue == 'x'
    assert mml.childNodes[0].childNodes[1].nodeName == 'mrow'
    assert mml.childNodes[0].childNodes[1].childNodes[0].nodeName == 'mi'
    assert mml.childNode
