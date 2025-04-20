from io import BytesIO, StringIO
import multiprocessing
import os
from pathlib import Path
from PIL import Image
import shutil
import subprocess
import sys
import warnings

import numpy as np
import pytest

from matplotlib.font_manager import (
    findfont, findSystemFonts, FontEntry, FontProperties, fontManager,
    json_dump, json_load, get_font, is_opentype_cff_font,
    MSUserFontDirectories, _get_fontconfig_fonts, ft2font,
    ttfFontProperty, cbook)
from matplotlib import pyplot as plt, rc_context

has_fclist = shutil.which('fc-list') is not None


def test_font_priority():
    """
    Test the font priority mechanism.
    
    This function checks the font priority mechanism by setting a specific font
    configuration and then finding the font used for a given family. It also
    verifies the character map of the selected font.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Steps:
    1. Set the font configuration to use 'cmmi10' as the primary sans-serif font
    and 'Bitstream Vera Sans' as the secondary option.
    2. Find the font used for the
    """

    with rc_context(rc={
            'font.sans-serif':
            ['cmmi10', 'Bitstream Vera Sans']}):
        font = findfont(FontProperties(family=["sans-serif"]))
    assert Path(font).name == 'cmmi10.ttf'

    # Smoketest get_charmap, which isn't used internally anymore
    font = get_font(font)
    cmap = font.get_charmap()
    assert len(cmap) == 131
    assert cmap[8729] == 30


def test_score_weight():
    assert 0 == fontManager.score_weight("regular", "regular")
    assert 0 == fontManager.score_weight("bold", "bold")
    assert (0 < fontManager.score_weight(400, 400) <
            fontManager.score_weight("normal", "bold"))
    assert (0 < fontManager.score_weight("normal", "regular") <
            fontManager.score_weight("normal", "bold"))
    assert (fontManager.score_weight("normal", "regular") ==
            fontManager.score_weight(400, 400))


def test_json_serialization(tmpdir):
    """
    Test JSON serialization of a font manager.
    
    This function serializes a font manager object to a JSON file and then deserializes it back. It verifies that the deserialized font manager can find fonts correctly for given font properties.
    
    Parameters:
    tmpdir (py.path.local): A temporary directory object provided by pytest for creating temporary files.
    
    Returns:
    None: This function does not return anything. It asserts that the deserialized font manager behaves the same as the original one for specific font properties.
    """

    # Can't open a NamedTemporaryFile twice on Windows, so use a temporary
    # directory instead.
    path = Path(tmpdir, "fontlist.json")
    json_dump(fontManager, path)
    copy = json_load(path)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', 'findfont: Font family.*not found')
        for prop in ({'family': 'STIXGeneral'},
                     {'family': 'Bitstream Vera Sans', 'weight': 700},
                     {'family': 'no such font family'}):
            fp = FontProperties(**prop)
            assert (fontManager.findfont(fp, rebuild_if_missing=False) ==
                    copy.findfont(fp, rebuild_if_missing=False))


def test_otf():
    fname = '/usr/share/fonts/opentype/freefont/FreeMono.otf'
    if Path(fname).exists():
        assert is_opentype_cff_font(fname)
    for f in fontManager.ttflist:
        if 'otf' in f.fname:
            with open(f.fname, 'rb') as fd:
                res = fd.read(4) == b'OTTO'
            assert res == is_opentype_cff_font(f.fname)


@pytest.mark.skipif(sys.platform == "win32" or not has_fclist,
                    reason='no fontconfig installed')
def test_get_fontconfig_fonts():
    assert len(_get_fontconfig_fonts()) > 1


@pytest.mark.parametrize('factor', [2, 4, 6, 8])
def test_hinting_factor(factor):
    font = findfont(FontProperties(family=["sans-serif"]))

    font1 = get_font(font, hinting_factor=1)
    font1.clear()
    font1.set_size(12, 100)
    font1.set_text('abc')
    expected = font1.get_width_height()

    hinted_font = get_font(font, hinting_factor=factor)
    hinted_font.clear()
    hinted_font.set_size(12, 100)
    hinted_font.set_text('abc')
    # Check that hinting only changes text layout by a small (10%) amount.
    np.testing.assert_allclose(hinted_font.get_width_height(), expected,
                               rtol=0.1)


def test_utf16m_sfnt():
    try:
        # seguisbi = Microsoft Segoe UI Semibold
        entry = next(entry for entry in fontManager.ttflist
                     if Path(entry.fname).name == "seguisbi.ttf")
    except StopIteration:
        pytest.skip("Couldn't find seguisbi.ttf font to test against.")
    else:
        # Check that we successfully read "semibold" from the font's sfnt table
        # and set its weight accordingly.
        assert entry.weight == 600


def test_find_ttc():
    fp = FontProperties(family=["WenQuanYi Zen Hei"])
    if Path(findfont(fp)).name != "wqy-zenhei.ttc":
        pytest.skip("Font wqy-zenhei.ttc may be missing")
    fig, ax = plt.subplots()
    ax.text(.5, .5, "\N{KANGXI RADICAL DRAGON}", fontproperties=fp)
    for fmt in ["raw", "svg", "pdf", "ps"]:
        fig.savefig(BytesIO(), format=fmt)


def test_find_noto():
    """
    Function to test the availability and usage of the Noto Sans CJK SC font in matplotlib.
    
    This function checks if the Noto Sans CJK SC font is available and correctly configured for use in matplotlib. It skips the test if the font is not found or is not one of the expected variants. If the font is available, it creates a matplotlib figure with a text containing both Latin and CJK characters, and saves the figure in various formats (raw, SVG, PDF, PS).
    
    Parameters:
    """

    fp = FontProperties(family=["Noto Sans CJK SC", "Noto Sans CJK JP"])
    name = Path(findfont(fp)).name
    if name not in ("NotoSansCJKsc-Regular.otf", "NotoSansCJK-Regular.ttc"):
        pytest.skip(f"Noto Sans CJK SC font may be missing (found {name})")

    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, 'Hello, 你好', fontproperties=fp)
    for fmt in ["raw", "svg", "pdf", "ps"]:
        fig.savefig(BytesIO(), format=fmt)


def test_find_invalid(tmpdir):
    tmp_path = Path(tmpdir)

    with pytest.raises(FileNotFoundError):
        get_font(tmp_path / 'non-existent-font-name.ttf')

    with pytest.raises(FileNotFoundError):
        get_font(str(tmp_path / 'non-existent-font-name.ttf'))

    with pytest.raises(FileNotFoundError):
        get_font(bytes(tmp_path / 'non-existent-font-name.ttf'))

    # Not really public, but get_font doesn't expose non-filename constructor.
    from matplotlib.ft2font import FT2Font
    with pytest.raises(TypeError, match='font file or a binary-mode file'):
        FT2Font(StringIO())


@pytest.mark.skipif(sys.platform != 'linux' or not has_fclist,
                    reason='only Linux with fontconfig installed')
def test_user_fonts_linux(tmpdir, monkeypatch):
    """
    Test user fonts on Linux.
    
    This function checks if a specific test font file is available in the system fonts. If the font is already present, the test is skipped. Otherwise, a temporary user font directory is created and the test font file is copied into it. The function then sets the `XDG_DATA_HOME` environment variable to point to this temporary directory and verifies that the font is now available. Finally, the cache for font configuration is cleared to ensure no residual data affects subsequent tests.
    
    Parameters
    """

    font_test_file = 'mpltest.ttf'

    # Precondition: the test font should not be available
    fonts = findSystemFonts()
    if any(font_test_file in font for font in fonts):
        pytest.skip(f'{font_test_file} already exists in system fonts')

    # Prepare a temporary user font directory
    user_fonts_dir = tmpdir.join('fonts')
    user_fonts_dir.ensure(dir=True)
    shutil.copyfile(Path(__file__).parent / font_test_file,
                    user_fonts_dir.join(font_test_file))

    with monkeypatch.context() as m:
        m.setenv('XDG_DATA_HOME', str(tmpdir))
        _get_fontconfig_fonts.cache_clear()
        # Now, the font should be available
        fonts = findSystemFonts()
        assert any(font_test_file in font for font in fonts)

    # Make sure the temporary directory is no longer cached.
    _get_fontconfig_fonts.cache_clear()


def test_addfont_as_path():
    """Smoke test that addfont() accepts pathlib.Path."""
    font_test_file = 'mpltest.ttf'
    path = Path(__file__).parent / font_test_file
    try:
        fontManager.addfont(path)
        added, = [font for font in fontManager.ttflist
                  if font.fname.endswith(font_test_file)]
        fontManager.ttflist.remove(added)
    finally:
        to_remove = [font for font in fontManager.ttflist
                     if font.fname.endswith(font_test_file)]
        for font in to_remove:
            fontManager.ttflist.remove(font)


@pytest.mark.skipif(sys.platform != 'win32', reason='Windows only')
def test_user_fonts_win32():
    if not (os.environ.get('APPVEYOR') or os.environ.get('TF_BUILD')):
        pytest.xfail("This test should only run on CI (appveyor or azure) "
                     "as the developer's font directory should remain "
                     "unchanged.")
    pytest.xfail("We need to update the registry for this test to work")
    font_test_file = 'mpltest.ttf'

    # Precondition: the test font should not be available
    fonts = findSystemFonts()
    if any(font_test_file in font for font in fonts):
        pytest.skip(f'{font_test_file} already exists in system fonts')

    user_fonts_dir = MSUserFontDirectories[0]

    # Make sure that the user font directory exists (this is probably not the
    # case on Windows versions < 1809)
    os.makedirs(user_fonts_dir)

    # Copy the test font to the user font directory
    shutil.copy(Path(__file__).parent / font_test_file, user_fonts_dir)

    # Now, the font should be available
    fonts = findSystemFonts()
    assert any(font_test_file in font for font in fonts)


def _model_handler(_):
    fig, ax = plt.subplots()
    fig.savefig(BytesIO(), format="pdf")
    plt.close()


@pytest.mark.skipif(not hasattr(os, "register_at_fork"),
                    reason="Cannot register at_fork handlers")
def test_fork():
    _model_handler(0)  # Make sure the font cache is filled.
    ctx = multiprocessing.get_context("fork")
    with ctx.Pool(processes=2) as pool:
        pool.map(_model_handler, range(2))


def test_missing_family(caplog):
    plt.rcParams["font.sans-serif"] = ["this-font-does-not-exist"]
    with caplog.at_level("WARNING"):
        findfont("sans")
    assert [rec.getMessage() for rec in caplog.records] == [
        "findfont: Font family ['sans'] not found. "
        "Falling back to DejaVu Sans.",
        "findfont: Generic family 'sans' not found because none of the "
        "following families were found: this-font-does-not-exist",
    ]


def _test_threading():
    import threading
    from matplotlib.ft2font import LOAD_NO_HINTING
    import matplotlib.font_manager as fm

    N = 10
    b = threading.Barrier(N)

    def bad_idea(n):
        """
        Generate a string representation of a number using a specific font.
        
        This function retrieves a font with the specified name and uses it to create a string representation of the given number.
        
        Parameters:
        n (int): The number to be converted into a string.
        
        Returns:
        str: The string representation of the number.
        
        Notes:
        - The font used is "DejaVu Sans".
        - The font is loaded without hinting.
        - The function is intended for demonstration purposes and may not be efficient
        """

        b.wait()
        for j in range(100):
            font = fm.get_font(fm.findfont("DejaVu Sans"))
            font.set_text(str(n), 0.0, flags=LOAD_NO_HINTING)

    threads = [
        threading.Thread(target=bad_idea, name=f"bad_thread_{j}", args=(j,))
        for j in range(N)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


def test_fontcache_thread_safe():
    """
    This function tests the thread safety of the fontcache module. It uses the threading module to run a test function in a separate thread. The test function is defined in the inspect.getsource(_test_threading) and is executed in a subprocess. The function returns a boolean value indicating whether the test was successful or not. If the subprocess returns a non-zero exit status, it indicates a failure in the test, and the function raises a pytest.fail exception.
    
    Parameters:
    - None
    
    Returns:
    - bool
    """

    pytest.importorskip('threading')
    import inspect

    proc = subprocess.run(
        [sys.executable, "-c",
         inspect.getsource(_test_threading) + '\n_test_threading()']
    )
    if proc.returncode:
        pytest.fail("The subprocess returned with non-zero exit status "
                    f"{proc.returncode}.")


def test_fontentry_dataclass():
    fontent = FontEntry(name='font-name')

    png = fontent._repr_png_()
    img = Image.open(BytesIO(png))
    assert img.width > 0
    assert img.height > 0

    html = fontent._repr_html_()
    assert html.startswith("<img src=\"data:image/png;base64")


def test_fontentry_dataclass_invalid_path():
    with pytest.raises(FileNotFoundError):
        fontent = FontEntry(fname='/random', name='font-name')
        fontent._repr_html_()


@pytest.mark.skipif(sys.platform == 'win32', reason='Linux or OS only')
def test_get_font_names():
    """
    Test that the font names available through matplotlib match the system fonts.
    
    This function checks that the font names available through matplotlib match
    the system fonts. It does this by finding all TrueType fonts in the matplotlib
    data path and the system, and then extracting the font names from these
    fonts. The function then compares the sorted list of unique font names to the
    list of font names returned by matplotlib's font manager.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The set
    """

    paths_mpl = [cbook._get_data_path('fonts', subdir) for subdir in ['ttf']]
    fonts_mpl = findSystemFonts(paths_mpl, fontext='ttf')
    fonts_system = findSystemFonts(fontext='ttf')
    ttf_fonts = []
    for path in fonts_mpl + fonts_system:
        try:
            font = ft2font.FT2Font(path)
            prop = ttfFontProperty(font)
            ttf_fonts.append(prop.name)
        except Exception:
            pass
    available_fonts = sorted(list(set(ttf_fonts)))
    mpl_font_names = sorted(fontManager.get_font_names())
    assert set(available_fonts) == set(mpl_font_names)
    assert len(available_fonts) == len(mpl_font_names)
    assert available_fonts == mpl_font_names
