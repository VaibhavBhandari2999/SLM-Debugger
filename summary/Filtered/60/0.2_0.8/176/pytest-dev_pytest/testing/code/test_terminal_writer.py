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
    This function tests code highlighting in a terminal writer.
    
    Parameters:
    has_markup (bool): Indicates whether the terminal writer supports markup.
    expected (str): The expected output string.
    color_mapping (str): A string containing color codes for the expected output.
    
    The function writes source code to a terminal writer and checks if the output matches the expected string. It also raises a ValueError if the indents size does not match the lines size.
    
    Returns:
    None
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
