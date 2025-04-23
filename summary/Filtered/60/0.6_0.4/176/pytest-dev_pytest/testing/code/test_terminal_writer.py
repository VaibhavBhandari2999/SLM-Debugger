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
    Write source code with syntax highlighting to a terminal.
    
    This function takes a list of source code lines and writes them to a terminal with syntax highlighting. It supports optional markup and uses a provided color mapping for highlighting.
    
    Parameters:
    lines (List[str]): The source code lines to be written.
    markup (bool): Whether to use markup for syntax highlighting. Default is True.
    color_mapping (Dict[str, str]): A dictionary mapping keywords to their color codes.
    
    Raises:
    ValueError: If the
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
