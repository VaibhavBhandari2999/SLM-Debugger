from sympy.external import import_module


autolevparser = import_module('sympy.parsing.autolev._antlr.autolevparser',
                              import_kwargs={'fromlist': ['AutolevParser']})
autolevlexer = import_module('sympy.parsing.autolev._antlr.autolevlexer',
                             import_kwargs={'fromlist': ['AutolevLexer']})
autolevlistener = import_module('sympy.parsing.autolev._antlr.autolevlistener',
                                import_kwargs={'fromlist': ['AutolevListener']})

AutolevParser = getattr(autolevparser, 'AutolevParser', None)
AutolevLexer = getattr(autolevlexer, 'AutolevLexer', None)
AutolevListener = getattr(autolevlistener, 'AutolevListener', None)


def parse_autolev(autolev_code, include_numeric):
    """
    Parse AutoLev code using ANTLR4.
    
    This function takes AutoLev code and parses it using ANTLR4 to generate a
    Python representation of the code. The parsing can include numeric values
    depending on the `include_numeric` parameter.
    
    Parameters:
    autolev_code (str or file-like object): The AutoLev code to parse.
    include_numeric (bool): If True, numeric values will be included in the
    parsed output.
    
    Returns:
    str:
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
