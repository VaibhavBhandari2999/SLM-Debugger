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
    
    This function serializes a font manager object to a JSON file and then deserializes it back. It checks the consistency of the font properties before and after serialization.
    
    Parameters:
    tmpdir (py.path.local): A temporary directory object provided by pytest for creating temporary files.
    
    Returns:
    None: The function asserts the equality of font properties before and after serialization, raising an AssertionError if they do not match.
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
    """
    Test if a given file is an OpenType CFF font.
    
    This function checks if the specified file is an OpenType CFF (Compact Font Format) font. It first verifies the existence of the file and then checks the file header to determine if it is an OpenType CFF font.
    
    Parameters:
    fname (str): The path to the font file to be tested.
    
    Returns:
    bool: True if the file is an OpenType CFF font, False otherwise.
    
    Example:
    >>>
    """

    fname = '/usr/share/fonts/opentype/freefont/FreeMono.otf'
    if Path(fname).exists():
        assert is_opentype_cff_font(fname)
    for f in fontManager.ttflist:
        if 'otf' in f.fname:
            with open(f.fname, 'rb') as fd:
                res = fd.read(4) == b'OTTO'
            assert res == is_opentype_cff_font(f.fname)


@pytest.mark.skipif(not has_fclist, reason='no fontconfig installed')
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
    Function to test the rendering of CJK text using the Noto Sans CJK SC font.
    
    This function checks if the Noto Sans CJK SC font is available and properly configured. If the font is not found, the test is skipped. The function then creates a plot with CJK text and saves it in different formats.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Steps:
    1. Set up a FontProperties object with the specified CJK font families.
    2. Check if the
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
    with pytest.raises(TypeError, match='path or binary-mode file'):
        FT2Font(StringIO())


@pytest.mark.skipif(sys.platform != 'linux', reason='Linux only')
def test_user_fonts_linux(tmpdir, monkeypatch):
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
    """
    Tests the behavior of the `findfont` function when a specified font family is missing.
    
    This function sets the default sans-serif font to a non-existent font and then attempts to find a matching font family. It captures the warning messages generated during this process and asserts that the expected warning messages are present.
    
    Parameters:
    caplog (pytest.LogCaptureFixture): A pytest fixture that captures log messages.
    
    Returns:
    None: This function does not return any value. It asserts that the expected warning messages are
    """

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
    paths_mpl = [cbook._get_data_path('fonts', subdir) for subdir in ['ttf']]
    fonts_mpl = findSystemFonts(paths_mpl, fontext='ttf')
    fonts_system = findSystemFonts(fontext='ttf')
    ttf_fonts = []
    for path in fonts_mpl + fonts_system:
        try:
            font = ft2font.FT2Font(path)
            prop = ttfFontProperty(font)
            ttf_fonts.append(prop.name)
        except:
            pass
    available_fonts = sorted(list(set(ttf_fonts)))
    mpl_font_names = sorted(fontManager.get_font_names())
    assert set(available_fonts) == set(mpl_font_names)
    assert len(available_fonts) == len(mpl_font_names)
    assert available_fonts == mpl_font_names
