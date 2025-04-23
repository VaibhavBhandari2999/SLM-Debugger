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
    Write source code to the terminal with optional color highlighting.
    
    This function writes source code to the terminal using a `TerminalWriter` instance. It can optionally apply color highlighting based on the `has_markup` parameter. The function takes a list of lines of code and writes them to the terminal with appropriate indentation and color highlighting if enabled.
    
    Parameters:
    has_markup (bool): Indicates whether color markup should be applied.
    expected (str): The expected output string after color highlighting.
    color_mapping (dict
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
