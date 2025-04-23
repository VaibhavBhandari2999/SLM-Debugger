import re
from io import StringIO

import pytest
from _pytest._io import TerminalWriter


@pytest.mark.parametrize(
    "has_markup, expected",
    [
        pytest.param(
            True, "{kw}assert{hl-reset} {number}0{hl-reset}\n", id="with markup"
        ),
        pytest.param(False, "assert 0\n", id="no markup"),
    ],
)
def test_code_highlight(has_markup, expected, color_mapping):
    """
    Write source code to the terminal with optional syntax highlighting.
    
    This function writes source code to the terminal using a `TerminalWriter` instance. It can optionally highlight the code using ANSI escape sequences based on the `has_markup` flag. The function takes a list of lines of code and writes them to the terminal, optionally applying syntax highlighting.
    
    Parameters:
    has_markup (bool): A flag indicating whether to use markup for syntax highlighting.
    expected (str): The expected output of the function.
    color
    """

    f = StringIO()
    tw = TerminalWriter(f)
    tw.hasmarkup = has_markup
    tw._write_source(["assert 0"])
    assert f.getvalue().splitlines(keepends=True) == color_mapping.format([expected])

    with pytest.raises(
        ValueError,
        match=re.escape("indents size (2) should have same size as lines (1)"),
    ):
        tw._write_source(["assert 0"], [" ", " "])
