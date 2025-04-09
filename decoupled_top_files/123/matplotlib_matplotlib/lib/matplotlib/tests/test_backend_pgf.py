import datetime
from io import BytesIO
import os
import shutil

import numpy as np
from packaging.version import parse as parse_version
import pytest

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.testing import _has_tex_package, _check_for_pgf
from matplotlib.testing.compare import compare_images, ImageComparisonFailure
from matplotlib.backends.backend_pgf import PdfPages, _tex_escape
from matplotlib.testing.decorators import (
    _image_directories, check_figures_equal, image_comparison)
from matplotlib.testing._markers import (
    needs_ghostscript, needs_pgf_lualatex, needs_pgf_pdflatex,
    needs_pgf_xelatex)


baseline_dir, result_dir = _image_directories(lambda: 'dummy func')


def compare_figure(fname, savefig_kwargs={}, tol=0):
    """
    Compare a generated figure with an expected baseline image.
    
    This function saves the given figure to a file, then compares it with
    an expected baseline image using the `compare_images` function. If the
    images differ by more than the specified tolerance (`tol`), an
    `ImageComparisonFailure` is raised.
    
    Parameters:
    -----------
    fname : str
    The name of the figure file to be compared.
    savefig_kwargs : dict, optional
    Keyword arguments
    """

    actual = os.path.join(result_dir, fname)
    plt.savefig(actual, **savefig_kwargs)

    expected = os.path.join(result_dir, "expected_%s" % fname)
    shutil.copyfile(os.path.join(baseline_dir, fname), expected)
    err = compare_images(expected, actual, tol=tol)
    if err:
        raise ImageComparisonFailure(err)


def create_figure():
    """
    Create a figure with various plot elements.
    
    This function generates a matplotlib figure containing different types of plot elements such as line plots, markers, filled paths, patterns, text, and typesetting. The figure includes a line plot of y = x^2, a marker at a specific point, filled areas with hatching and patterns, and text with mathematical expressions and unicode characters.
    
    Parameters:
    None
    
    Returns:
    fig: A matplotlib figure object containing the created plot elements.
    """

    plt.figure()
    x = np.linspace(0, 1, 15)

    # line plot
    plt.plot(x, x ** 2, "b-")

    # marker
    plt.plot(x, 1 - x**2, "g>")

    # filled paths and patterns
    plt.fill_between([0., .4], [.4, 0.], hatch='//', facecolor="lightgray",
                     edgecolor="red")
    plt.fill([3, 3, .8, .8, 3], [2, -2, -2, 0, 2], "b")

    # text and typesetting
    plt.plot([0.9], [0.5], "ro", markersize=3)
    plt.text(0.9, 0.5, 'unicode (ü, °, µ) and math ($\\mu_i = x_i^2$)',
             ha='right', fontsize=20)
    plt.ylabel('sans-serif, blue, $\\frac{\\sqrt{x}}{y^2}$..',
               family='sans-serif', color='blue')

    plt.xlim(0, 1)
    plt.ylim(0, 1)


@pytest.mark.parametrize('plain_text, escaped_text', [
    (r'quad_sum: $\sum x_i^2$', r'quad\_sum: \(\displaystyle \sum x_i^2\)'),
    (r'no \$splits \$ here', r'no \$splits \$ here'),
    ('with_underscores', r'with\_underscores'),
    ('% not a comment', r'\% not a comment'),
    ('^not', r'\^not'),
])
def test_tex_escape(plain_text, escaped_text):
    assert _tex_escape(plain_text) == escaped_text


# test compiling a figure to pdf with xelatex
@needs_pgf_xelatex
@pytest.mark.backend('pgf')
@image_comparison(['pgf_xelatex.pdf'], style='default')
def test_xelatex():
    """
    Generate a figure using XeLaTeX for text rendering.
    
    This function updates the Matplotlib configuration to use XeLaTeX for
    rendering text, sets the font family to 'serif', and disables the default
    PGF backend. It then calls the `create_figure` function to generate the
    figure.
    
    Parameters:
    None
    
    Returns:
    None
    """

    rc_xelatex = {'font.family': 'serif',
                  'pgf.rcfonts': False}
    mpl.rcParams.update(rc_xelatex)
    create_figure()


try:
    _old_gs_version = \
        mpl._get_executable_info('gs').version < parse_version('9.50')
except mpl.ExecutableNotFoundError:
    _old_gs_version = True


# test compiling a figure to pdf with pdflatex
@needs_pgf_pdflatex
@pytest.mark.skipif(not _has_tex_package('ucs'), reason='needs ucs.sty')
@pytest.mark.backend('pgf')
@image_comparison(['pgf_pdflatex.pdf'], style='default',
                  tol=11.7 if _old_gs_version else 0)
def test_pdflatex():
    """
    Test pdflatex functionality.
    
    This test ensures that the matplotlib backend is configured to use pdflatex
    for rendering LaTeX equations and that the necessary preamble is set up.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    xfail: If running on AppVeyor, due to missing LaTeX fonts.
    
    Important Functions:
    - `os.environ.get`: Checks if the environment variable `APPVEYOR` is set.
    - `pytest.xfail
    """

    if os.environ.get('APPVEYOR'):
        pytest.xfail("pdflatex test does not work on appveyor due to missing "
                     "LaTeX fonts")

    rc_pdflatex = {'font.family': 'serif',
                   'pgf.rcfonts': False,
                   'pgf.texsystem': 'pdflatex',
                   'pgf.preamble': ('\\usepackage[utf8x]{inputenc}'
                                    '\\usepackage[T1]{fontenc}')}
    mpl.rcParams.update(rc_pdflatex)
    create_figure()


# test updating the rc parameters for each figure
@needs_pgf_xelatex
@needs_pgf_pdflatex
@mpl.style.context('default')
@pytest.mark.backend('pgf')
def test_rcupdate():
    """
    Test the rcupdate functionality of Matplotlib.
    
    This function tests the rcupdate feature by setting different
    `rcParams` configurations and comparing the generated figures with
    expected outputs. The test involves two sets of `rcParams`:
    
    - The first set configures the font family to 'sans-serif', sets the
    font size to 30, adjusts the figure subplot left margin to 0.2,
    sets the line markersize to 10, disables pg
    """

    rc_sets = [{'font.family': 'sans-serif',
                'font.size': 30,
                'figure.subplot.left': .2,
                'lines.markersize': 10,
                'pgf.rcfonts': False,
                'pgf.texsystem': 'xelatex'},
               {'font.family': 'monospace',
                'font.size': 10,
                'figure.subplot.left': .1,
                'lines.markersize': 20,
                'pgf.rcfonts': False,
                'pgf.texsystem': 'pdflatex',
                'pgf.preamble': ('\\usepackage[utf8x]{inputenc}'
                                 '\\usepackage[T1]{fontenc}'
                                 '\\usepackage{sfmath}')}]
    tol = [0, 13.2] if _old_gs_version else [0, 0]
    for i, rc_set in enumerate(rc_sets):
        with mpl.rc_context(rc_set):
            for substring, pkg in [('sfmath', 'sfmath'), ('utf8x', 'ucs')]:
                if (substring in mpl.rcParams['pgf.preamble']
                        and not _has_tex_package(pkg)):
                    pytest.skip(f'needs {pkg}.sty')
            create_figure()
            compare_figure(f'pgf_rcupdate{i + 1}.pdf', tol=tol[i])


# test backend-side clipping, since large numbers are not supported by TeX
@needs_pgf_xelatex
@mpl.style.context('default')
@pytest.mark.backend('pgf')
def test_pathclip():
    """
    Test path clipping.
    
    This function creates two subplots using Matplotlib. The first subplot
    contains a line plot with specific x and y limits. The second subplot
    includes a scatter plot and a histogram with logarithmic scaling on the
    x-axis. The function saves the figure as a PDF without generating an
    image comparison.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.subplots()`: Creates a figure and a set of
    """

    np.random.seed(19680801)
    mpl.rcParams.update({'font.family': 'serif', 'pgf.rcfonts': False})
    fig, axs = plt.subplots(1, 2)

    axs[0].plot([0., 1e100], [0., 1e100])
    axs[0].set_xlim(0, 1)
    axs[0].set_ylim(0, 1)

    axs[1].scatter([0, 1], [1, 1])
    axs[1].hist(np.random.normal(size=1000), bins=20, range=[-10, 10])
    axs[1].set_xscale('log')

    fig.savefig(BytesIO(), format="pdf")  # No image comparison.


# test mixed mode rendering
@needs_pgf_xelatex
@pytest.mark.backend('pgf')
@image_comparison(['pgf_mixedmode.pdf'], style='default')
def test_mixedmode():
    """
    Generate a pcolor plot with rasterized rendering.
    
    This function creates a pcolor plot of a 2D grid where the values are
    determined by the sum of squares of the grid coordinates. The resulting
    plot is rendered using rasterized mode, which improves the appearance when
    saving the figure in vector formats.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `np.ogrid`: Generates open multi-dimensional "meshgrid".
    """

    mpl.rcParams.update({'font.family': 'serif', 'pgf.rcfonts': False})
    Y, X = np.ogrid[-1:1:40j, -1:1:40j]
    plt.pcolor(X**2 + Y**2).set_rasterized(True)


# test bbox_inches clipping
@needs_pgf_xelatex
@mpl.style.context('default')
@pytest.mark.backend('pgf')
def test_bbox_inches():
    """
    Generate a PDF figure with specified bounding box.
    
    This function creates a two-panel plot using Matplotlib, where each panel
    contains a simple line plot of numbers ranging from 0 to 4. The figure is
    then saved as a PDF file with a specified bounding box that captures only
    the first panel's content.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt.subplots`: Creates a figure and a set of subplots.
    """

    mpl.rcParams.update({'font.family': 'serif', 'pgf.rcfonts': False})
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.plot(range(5))
    ax2.plot(range(5))
    plt.tight_layout()
    bbox = ax1.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    compare_figure('pgf_bbox_inches.pdf', savefig_kwargs={'bbox_inches': bbox},
                   tol=0)


@mpl.style.context('default')
@pytest.mark.backend('pgf')
@pytest.mark.parametrize('system', [
    pytest.param('lualatex', marks=[needs_pgf_lualatex]),
    pytest.param('pdflatex', marks=[needs_pgf_pdflatex]),
    pytest.param('xelatex', marks=[needs_pgf_xelatex]),
])
def test_pdf_pages(system):
    """
    Generates a multipage PDF using Matplotlib figures and the PdfPages class.
    
    This function creates two Matplotlib figures, configures the LaTeX system
    for PDF generation, and saves them into a single multipage PDF file. The
    function uses the `PdfPages` class from matplotlib.backends.backend_pdf
    to manage the PDF creation process. The generated PDF includes three pages
    with the first figure repeated on the third page.
    
    Parameters:
    - system (str): The
    """

    rc_pdflatex = {
        'font.family': 'serif',
        'pgf.rcfonts': False,
        'pgf.texsystem': system,
    }
    mpl.rcParams.update(rc_pdflatex)

    fig1, ax1 = plt.subplots()
    ax1.plot(range(5))
    fig1.tight_layout()

    fig2, ax2 = plt.subplots(figsize=(3, 2))
    ax2.plot(range(5))
    fig2.tight_layout()

    path = os.path.join(result_dir, f'pdfpages_{system}.pdf')
    md = {
        'Author': 'me',
        'Title': 'Multipage PDF with pgf',
        'Subject': 'Test page',
        'Keywords': 'test,pdf,multipage',
        'ModDate': datetime.datetime(
            1968, 8, 1, tzinfo=datetime.timezone(datetime.timedelta(0))),
        'Trapped': 'Unknown'
    }

    with PdfPages(path, metadata=md) as pdf:
        pdf.savefig(fig1)
        pdf.savefig(fig2)
        pdf.savefig(fig1)

        assert pdf.get_pagecount() == 3


@mpl.style.context('default')
@pytest.mark.backend('pgf')
@pytest.mark.parametrize('system', [
    pytest.param('lualatex', marks=[needs_pgf_lualatex]),
    pytest.param('pdflatex', marks=[needs_pgf_pdflatex]),
    pytest.param('xelatex', marks=[needs_pgf_xelatex]),
])
def test_pdf_pages_metadata_check(monkeypatch, system):
    """
    Check the metadata of a multipage PDF created using Matplotlib's pgf backend.
    
    This function creates a multipage PDF with specified metadata using Matplotlib's pgf backend and verifies that the metadata is correctly set. The metadata includes information such as author, title, subject, keywords, modification date, and trapping status. The function uses `pikepdf` to read and inspect the PDF file.
    
    Parameters:
    - monkeypatch (pytest.MonkeyPatch): A pytest fixture used to modify environment
    """

    # Basically the same as test_pdf_pages, but we keep it separate to leave
    # pikepdf as an optional dependency.
    pikepdf = pytest.importorskip('pikepdf')
    monkeypatch.setenv('SOURCE_DATE_EPOCH', '0')

    mpl.rcParams.update({'pgf.texsystem': system})

    fig, ax = plt.subplots()
    ax.plot(range(5))

    md = {
        'Author': 'me',
        'Title': 'Multipage PDF with pgf',
        'Subject': 'Test page',
        'Keywords': 'test,pdf,multipage',
        'ModDate': datetime.datetime(
            1968, 8, 1, tzinfo=datetime.timezone(datetime.timedelta(0))),
        'Trapped': 'True'
    }
    path = os.path.join(result_dir, f'pdfpages_meta_check_{system}.pdf')
    with PdfPages(path, metadata=md) as pdf:
        pdf.savefig(fig)

    with pikepdf.Pdf.open(path) as pdf:
        info = {k: str(v) for k, v in pdf.docinfo.items()}

    # Not set by us, so don't bother checking.
    if '/PTEX.FullBanner' in info:
        del info['/PTEX.FullBanner']
    if '/PTEX.Fullbanner' in info:
        del info['/PTEX.Fullbanner']

    # Some LaTeX engines ignore this setting, and state themselves as producer.
    producer = info.pop('/Producer')
    assert producer == f'Matplotlib pgf backend v{mpl.__version__}' or (
            system == 'lualatex' and 'LuaTeX' in producer)

    assert info == {
        '/Author': 'me',
        '/CreationDate': 'D:19700101000000Z',
        '/Creator': f'Matplotlib v{mpl.__version__}, https://matplotlib.org',
        '/Keywords': 'test,pdf,multipage',
        '/ModDate': 'D:19680801000000Z',
        '/Subject': 'Test page',
        '/Title': 'Multipage PDF with pgf',
        '/Trapped': '/True',
    }


@needs_pgf_xelatex
def test_tex_restart_after_error():
    """
    Test the restart functionality of a matplotlib figure after encountering an error during LaTeX rendering.
    
    This function creates a matplotlib figure, attempts to set a title containing an invalid LaTeX command, and expects a ValueError to be raised. After restarting the figure from scratch, it sets a valid LaTeX title and saves the figure in PGF format without errors.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    - matplotlib.pyplot: Used for creating and manipulating figures.
    - pytest.raises: Used
    """

    fig = plt.figure()
    fig.suptitle(r"\oops")
    with pytest.raises(ValueError):
        fig.savefig(BytesIO(), format="pgf")

    fig = plt.figure()  # start from scratch
    fig.suptitle(r"this is ok")
    fig.savefig(BytesIO(), format="pgf")


@needs_pgf_xelatex
def test_bbox_inches_tight():
    """
    Save an image with tight bounding box in PDF format using PGF backend.
    
    This function creates a simple 2x2 image using `imshow` and saves it as a
    PDF file with a tight bounding box. The `bbox_inches='tight'` parameter is
    used to ensure that only the image content is included in the saved file,
    without any extra whitespace around it.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `plt
    """

    fig, ax = plt.subplots()
    ax.imshow([[0, 1], [2, 3]])
    fig.savefig(BytesIO(), format="pdf", backend="pgf", bbox_inches="tight")


@needs_pgf_xelatex
@needs_ghostscript
def test_png_transparency():  # Actually, also just testing that png works.
    """
    Test PNG transparency.
    
    This function creates a PNG image with transparency using Matplotlib and
    verifies that the alpha channel is set to zero, indicating full transparency.
    
    Parameters:
    None
    
    Returns:
    None
    
    Methods:
    - `BytesIO`: A memory-based stream for handling binary data.
    - `plt.figure()`: Creates a new figure.
    - `savefig(buf, format="png", backend="pgf", transparent=True)`: Saves the current figure to
    """

    buf = BytesIO()
    plt.figure().savefig(buf, format="png", backend="pgf", transparent=True)
    buf.seek(0)
    t = plt.imread(buf)
    assert (t[..., 3] == 0).all()  # fully transparent.


@needs_pgf_xelatex
def test_unknown_font(caplog):
    """
    Test the handling of an unknown font in Matplotlib.
    
    This function sets the font family to an unknown font, creates a figure
    containing text, and saves it as a PGF file. It captures the log messages
    generated during this process and verifies that a warning is issued about
    the unknown font.
    
    Parameters:
    -----------
    caplog : pytest.LogCaptureFixture
    A fixture that captures log messages.
    
    Returns:
    --------
    None
    
    Raises:
    """

    with caplog.at_level("WARNING"):
        mpl.rcParams["font.family"] = "this-font-does-not-exist"
        plt.figtext(.5, .5, "hello, world")
        plt.savefig(BytesIO(), format="pgf")
    assert "Ignoring unknown font: this-font-does-not-exist" in [
        r.getMessage() for r in caplog.records]


@check_figures_equal(extensions=["pdf"])
@pytest.mark.parametrize("texsystem", ("pdflatex", "xelatex", "lualatex"))
@pytest.mark.backend("pgf")
def test_minus_signs_with_tex(fig_test, fig_ref, texsystem):
    """
    Generate a Python docstring for the provided function.
    
    Args:
    fig_test (matplotlib.figure.Figure): The figure object to be tested.
    fig_ref (matplotlib.figure.Figure): The reference figure object.
    texsystem (str): The LaTeX system to be used.
    
    Summary:
    This function tests the rendering of minus signs in matplotlib figures using the specified LaTeX system. It sets the global `pgf.texsystem` parameter to the given `texsystem`, then adds a text annotation
    """

    if not _check_for_pgf(texsystem):
        pytest.skip(texsystem + ' + pgf is required')
    mpl.rcParams["pgf.texsystem"] = texsystem
    fig_test.text(.5, .5, "$-1$")
    fig_ref.text(.5, .5, "$\N{MINUS SIGN}1$")


@pytest.mark.backend("pgf")
def test_sketch_params():
    """
    \pgfpathmoveto{\pgfqpoint{0.375000in}{0.300000in}}%
    \pgfpathlineto{\pgfqpoint{2.700000in}{2.700000in}}%
    \usepgfmodule{decorations}%
    \usepgflibrary{decorations.pathmorphing}%
    \pgfkeys{/pgf/decoration/.cd,
    """

    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    handle, = ax.plot([0, 1])
    handle.set_sketch_params(scale=5, length=30, randomness=42)

    with BytesIO() as fd:
        fig.savefig(fd, format='pgf')
        buf = fd.getvalue().decode()

    baseline = r"""\pgfpathmoveto{\pgfqpoint{0.375000in}{0.300000in}}%
\pgfpathlineto{\pgfqpoint{2.700000in}{2.700000in}}%
\usepgfmodule{decorations}%
\usepgflibrary{decorations.pathmorphing}%
\pgfkeys{/pgf/decoration/.cd, """ \
    r"""segment length = 0.150000in, amplitude = 0.100000in}%
\pgfmathsetseed{42}%
\pgfdecoratecurrentpath{random steps}%
\pgfusepath{stroke}%"""
    # \pgfdecoratecurrentpath must be after the path definition and before the
    # path is used (\pgfusepath)
    assert baseline in buf
