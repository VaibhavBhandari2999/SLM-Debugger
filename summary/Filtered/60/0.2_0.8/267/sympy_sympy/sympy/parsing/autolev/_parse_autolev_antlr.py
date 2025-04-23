import sys
from sympy.external import import_module


autolevparser = import_module('sympy.parsing.autolev._antlr.autolevparser',
                              __import__kwargs={'fromlist': ['AutolevParser']})
autolevlexer = import_module('sympy.parsing.autolev._antlr.autolevlexer',
                             __import__kwargs={'fromlist': ['AutolevLexer']})
autolevlistener = import_module('sympy.parsing.autolev._antlr.autolevlistener',
                                __import__kwargs={'fromlist': ['AutolevListener']})

AutolevParser = getattr(autolevparser, 'AutolevParser', None)
AutolevLexer = getattr(autolevlexer, 'AutolevLexer', None)
AutolevListener = getattr(autolevlistener, 'AutolevListener', None)


def parse_autolev(autolev_code, include_numeric):
    """
    Parse AutoLev code into a string of Python code.
    
    This function takes AutoLev code and converts it into a string of Python code.
    The conversion can include numeric values if specified.
    
    Parameters:
    autolev_code (str or file-like object): The AutoLev code to be parsed.
    include_numeric (bool): Whether to include numeric values in the output.
    
    Returns:
    str: A string of Python code representing the parsed AutoLev code.
    
    Raises:
    ImportError: If
    """

    antlr4 = import_module('antlr4', warn_not_installed=True)
    if not antlr4:
        raise ImportError("Autolev parsing requires the antlr4 python package,"
                          " provided by pip (antlr4-python2-runtime or"
                          " antlr4-python3-runtime) or"
                          " conda (antlr-python-runtime)")
    try:
        l = autolev_code.readlines()
        input_stream = antlr4.InputStream("".join(l))
    except Exception:
        input_stream = antlr4.InputStream(autolev_code)

    if AutolevListener:
        from ._listener_autolev_antlr import MyListener
        lexer = AutolevLexer(input_stream)
        token_stream = antlr4.CommonTokenStream(lexer)
        parser = AutolevParser(token_stream)
        tree = parser.prog()
        my_listener = MyListener(include_numeric)
        walker = antlr4.ParseTreeWalker()
        walker.walk(my_listener, tree)
        return "".join(my_listener.output_code)
