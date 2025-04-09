import importlib
import importlib.util
import inspect
import json
import os
import platform
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request

from PIL import Image

import pytest

import matplotlib as mpl
from matplotlib import _c_internal_utils
from matplotlib.backend_tools import ToolToggleBase
from matplotlib.testing import subprocess_run_helper as _run_helper


# Minimal smoke-testing of the backends for which the dependencies are
# PyPI-installable on CI.  They are not available for all tested Python
# versions so we don't fail on missing backends.

def _get_testable_interactive_backends():
    """
    Get testable interactive backends.
    
    This function generates a list of test environments for interactive backends,
    including various combinations of dependencies and environment variables.
    The generated environments are then used to run tests for different backend
    configurations.
    
    Args:
    None
    
    Returns:
    A list of test environments (pytest param objects) for interactive backends.
    """

    envs = []
    for deps, env in [
            *[([qt_api],
               {"MPLBACKEND": "qtagg", "QT_API": qt_api})
              for qt_api in ["PyQt6", "PySide6", "PyQt5", "PySide2"]],
            *[([qt_api, "cairocffi"],
               {"MPLBACKEND": "qtcairo", "QT_API": qt_api})
              for qt_api in ["PyQt6", "PySide6", "PyQt5", "PySide2"]],
            *[(["cairo", "gi"], {"MPLBACKEND": f"gtk{version}{renderer}"})
              for version in [3, 4] for renderer in ["agg", "cairo"]],
            (["tkinter"], {"MPLBACKEND": "tkagg"}),
            (["wx"], {"MPLBACKEND": "wx"}),
            (["wx"], {"MPLBACKEND": "wxagg"}),
            (["matplotlib.backends._macosx"], {"MPLBACKEND": "macosx"}),
    ]:
        reason = None
        missing = [dep for dep in deps if not importlib.util.find_spec(dep)]
        if (sys.platform == "linux" and
                not _c_internal_utils.display_is_valid()):
            reason = "$DISPLAY and $WAYLAND_DISPLAY are unset"
        elif missing:
            reason = "{} cannot be imported".format(", ".join(missing))
        elif env["MPLBACKEND"] == 'macosx' and os.environ.get('TF_BUILD'):
            reason = "macosx backend fails on Azure"
        elif env["MPLBACKEND"].startswith('gtk'):
            import gi
            version = env["MPLBACKEND"][3]
            repo = gi.Repository.get_default()
            if f'{version}.0' not in repo.enumerate_versions('Gtk'):
                reason = "no usable GTK bindings"
        marks = []
        if reason:
            marks.append(pytest.mark.skip(
                reason=f"Skipping {env} because {reason}"))
        elif env["MPLBACKEND"].startswith('wx') and sys.platform == 'darwin':
            # ignore on OSX because that's currently broken (github #16849)
            marks.append(pytest.mark.xfail(reason='github #16849'))
        envs.append(
            pytest.param(
                {**env, 'BACKEND_DEPS': ','.join(deps)},
                marks=marks, id=str(env)
            )
        )
    return envs


_test_timeout = 120  # A reasonably safe value for slower architectures.


def _test_toolbar_button_la_mode_icon(fig):
    """
    Test a toolbar button icon using an image in LA mode.
    
    This function creates a custom toolbar button with an image in LA mode,
    which is then added to the figure's canvas toolbar. The function uses a
    temporary directory to save the image and a custom tool class derived from
    `ToolToggleBase`.
    
    Parameters:
    fig (matplotlib.figure.Figure): The figure to which the toolbar button will be added.
    
    Returns:
    None: The function modifies the figure's canvas
    """

    # test a toolbar button icon using an image in LA mode (GH issue 25174)
    # create an icon in LA mode
    with tempfile.TemporaryDirectory() as tempdir:
        img = Image.new("LA", (26, 26))
        tmp_img_path = os.path.join(tempdir, "test_la_icon.png")
        img.save(tmp_img_path)

        class CustomTool(ToolToggleBase):
            image = tmp_img_path
            description = ""  # gtk3 backend does not allow None

        toolmanager = fig.canvas.manager.toolmanager
        toolbar = fig.canvas.manager.toolbar
        toolmanager.add_tool("test", CustomTool)
        toolbar.add_tool("test", "group")


# The source of this function gets extracted and run in another process, so it
# must be fully self-contained.
# Using a timer not only allows testing of timers (on other backends), but is
# also necessary on gtk3 and wx, where directly processing a KeyEvent() for "q"
# from draw_event causes breakage as the canvas widget gets deleted too early.
def _test_interactive_impl():
    """
    Test interactive plotting functionality.
    
    This function tests various aspects of interactive plotting, including:
    - Setting Matplotlib backend parameters.
    - Checking the ability to switch between different backends.
    - Creating and manipulating figures and axes.
    - Testing toolbar button icons in the toolmanager toolbar.
    - Handling events such as key press, draw, and close.
    - Saving figures to PNG format before and after closing the interactive window.
    - Ensuring that the saved figures match when using certain back
    """

    import importlib.util
    import io
    import json
    import sys
    from unittest import TestCase

    import matplotlib as mpl
    from matplotlib import pyplot as plt
    from matplotlib.backend_bases import KeyEvent
    mpl.rcParams.update({
        "webagg.open_in_browser": False,
        "webagg.port_retries": 1,
    })

    mpl.rcParams.update(json.loads(sys.argv[1]))
    backend = plt.rcParams["backend"].lower()
    assert_equal = TestCase().assertEqual
    assert_raises = TestCase().assertRaises

    if backend.endswith("agg") and not backend.startswith(("gtk", "web")):
        # Force interactive framework setup.
        plt.figure()

        # Check that we cannot switch to a backend using another interactive
        # framework, but can switch to a backend using cairo instead of agg,
        # or a non-interactive backend.  In the first case, we use tkagg as
        # the "other" interactive backend as it is (essentially) guaranteed
        # to be present.  Moreover, don't test switching away from gtk3 (as
        # Gtk.main_level() is not set up at this point yet) and webagg (which
        # uses no interactive framework).

        if backend != "tkagg":
            with assert_raises(ImportError):
                mpl.use("tkagg", force=True)

        def check_alt_backend(alt_backend):
            """
            Check if the alternative backend is correctly set.
            
            This function sets the specified alternative backend using `mpl.use` and
            creates a new figure. It then asserts that the type of the canvas object
            matches the expected backend type, which is derived from the alternative
            backend name.
            
            Parameters:
            -----------
            alt_backend : str
            The name of the alternative backend to be used with Matplotlib.
            
            Returns:
            --------
            None
            
            Raises:
            -------
            AssertionError
            """

            mpl.use(alt_backend, force=True)
            fig = plt.figure()
            assert_equal(
                type(fig.canvas).__module__,
                f"matplotlib.backends.backend_{alt_backend}")

        if importlib.util.find_spec("cairocffi"):
            check_alt_backend(backend[:-3] + "cairo")
        check_alt_backend("svg")
    mpl.use(backend, force=True)

    fig, ax = plt.subplots()
    assert_equal(
        type(fig.canvas).__module__,
        f"matplotlib.backends.backend_{backend}")

    if mpl.rcParams["toolbar"] == "toolmanager":
        # test toolbar button icon LA mode see GH issue 25174
        _test_toolbar_button_la_mode_icon(fig)

    if mpl.rcParams["toolbar"] == "toolmanager":
        # test toolbar button icon LA mode see GH issue 25174
        _test_toolbar_button_la_mode_icon(fig)

    ax.plot([0, 1], [2, 3])
    if fig.canvas.toolbar:  # i.e toolbar2.
        fig.canvas.toolbar.draw_rubberband(None, 1., 1, 2., 2)

    timer = fig.canvas.new_timer(1.)  # Test that floats are cast to int.
    timer.add_callback(KeyEvent("key_press_event", fig.canvas, "q")._process)
    # Trigger quitting upon draw.
    fig.canvas.mpl_connect("draw_event", lambda event: timer.start())
    fig.canvas.mpl_connect("close_event", print)

    result = io.BytesIO()
    fig.savefig(result, format='png')

    plt.show()

    # Ensure that the window is really closed.
    plt.pause(0.5)

    # Test that saving works after interactive window is closed, but the figure
    # is not deleted.
    result_after = io.BytesIO()
    fig.savefig(result_after, format='png')

    if not backend.startswith('qt5') and sys.platform == 'darwin':
        # FIXME: This should be enabled everywhere once Qt5 is fixed on macOS
        # to not resize incorrectly.
        assert_equal(result.getvalue(), result_after.getvalue())


@pytest.mark.parametrize("env", _get_testable_interactive_backends())
@pytest.mark.parametrize("toolbar", ["toolbar2", "toolmanager"])
@pytest.mark.flaky(reruns=3)
def test_interactive_backend(env, toolbar):
    """
    Test the interactive backend with specified toolbar.
    
    Parameters
    ----------
    env : dict
    Environment variables for the test process.
    toolbar : str
    The toolbar type to use for the test.
    
    Returns
    -------
    None
    
    Raises
    ------
    AssertionError
    If the number of "CloseEvent" occurrences in the test output does not match the expected value.
    """

    if env["MPLBACKEND"] == "macosx":
        if toolbar == "toolmanager":
            pytest.skip("toolmanager is not implemented for macosx.")
    if env["MPLBACKEND"] == "wx":
        pytest.skip("wx backend is deprecated; tests failed on appveyor")
    try:
        proc = _run_helper(
                _test_interactive_impl,
                json.dumps({"toolbar": toolbar}),
                timeout=_test_timeout,
                extra_env=env,
                )
    except subprocess.CalledProcessError as err:
        pytest.fail(
                "Subprocess failed to test intended behavior\n"
                + str(err.stderr))
    assert proc.stdout.count("CloseEvent") == 1


def _test_thread_impl():
    """
    Test artist creation and drawing from a separate thread using ThreadPoolExecutor. This function creates a matplotlib figure and axis, plots data, and ensures that the drawing process completes without crashing. It also connects a close event handler and flushes events before closing the figure. The function uses `plt.pause` to ensure that the drawing process has time to complete and handles exceptions by joining the thread and rethrowing any errors.
    
    Args:
    None
    
    Returns:
    None
    
    Functions Used:
    -
    """

    from concurrent.futures import ThreadPoolExecutor

    import matplotlib as mpl
    from matplotlib import pyplot as plt

    mpl.rcParams.update({
        "webagg.open_in_browser": False,
        "webagg.port_retries": 1,
    })

    # Test artist creation and drawing does not crash from thread
    # No other guarantees!
    fig, ax = plt.subplots()
    # plt.pause needed vs plt.show(block=False) at least on toolbar2-tkagg
    plt.pause(0.5)

    future = ThreadPoolExecutor().submit(ax.plot, [1, 3, 6])
    future.result()  # Joins the thread; rethrows any exception.

    fig.canvas.mpl_connect("close_event", print)
    future = ThreadPoolExecutor().submit(fig.canvas.draw)
    plt.pause(0.5)  # flush_events fails here on at least Tkagg (bpo-41176)
    future.result()  # Joins the thread; rethrows any exception.
    plt.close()  # backend is responsible for flushing any events here
    if plt.rcParams["backend"].startswith("WX"):
        # TODO: debug why WX needs this only on py3.8
        fig.canvas.flush_events()


_thread_safe_backends = _get_testable_interactive_backends()
# Known unsafe backends. Remove the xfails if they start to pass!
for param in _thread_safe_backends:
    backend = param.values[0]["MPLBACKEND"]
    if "cairo" in backend:
        # Cairo backends save a cairo_t on the graphics context, and sharing
        # these is not threadsafe.
        param.marks.append(
            pytest.mark.xfail(raises=subprocess.CalledProcessError))
    elif backend == "wx":
        param.marks.append(
            pytest.mark.xfail(raises=subprocess.CalledProcessError))
    elif backend == "macosx":
        from packaging.version import parse
        mac_ver = platform.mac_ver()[0]
        # Note, macOS Big Sur is both 11 and 10.16, depending on SDK that
        # Python was compiled against.
        if mac_ver and parse(mac_ver) < parse('10.16'):
            param.marks.append(
                pytest.mark.xfail(raises=subprocess.TimeoutExpired,
                                  strict=True))
    elif param.values[0].get("QT_API") == "PySide2":
        param.marks.append(
            pytest.mark.xfail(raises=subprocess.CalledProcessError))
    elif backend == "tkagg" and platform.python_implementation() != 'CPython':
        param.marks.append(
            pytest.mark.xfail(
                reason='PyPy does not support Tkinter threading: '
                       'https://foss.heptapod.net/pypy/pypy/-/issues/1929',
                strict=True))


@pytest.mark.parametrize("env", _thread_safe_backends)
@pytest.mark.flaky(reruns=3)
def test_interactive_thread_safety(env):
    proc = _run_helper(_test_thread_impl, timeout=_test_timeout, extra_env=env)
    assert proc.stdout.count("CloseEvent") == 1


def _impl_test_lazy_auto_backend_selection():
    """
    Test lazy auto backend selection in Matplotlib.
    
    This function tests the lazy auto backend selection mechanism in Matplotlib by:
    - Importing `matplotlib` and `matplotlib.pyplot`.
    - Checking if the backend is resolved as a string.
    - Verifying that the backend module is `None` after importing `pyplot`.
    - Plotting a value (5) to trigger backend resolution.
    - Confirming that the backend module is no longer `None` after plotting.
    - Ver
    """

    import matplotlib
    import matplotlib.pyplot as plt
    # just importing pyplot should not be enough to trigger resolution
    bk = matplotlib.rcParams._get('backend')
    assert not isinstance(bk, str)
    assert plt._backend_mod is None
    # but actually plotting should
    plt.plot(5)
    assert plt._backend_mod is not None
    bk = matplotlib.rcParams._get('backend')
    assert isinstance(bk, str)


def test_lazy_auto_backend_selection():
    _run_helper(_impl_test_lazy_auto_backend_selection,
                timeout=_test_timeout)


def _implqt5agg():
    """
    Imports the necessary backend for Qt5Agg in Matplotlib, ensuring that PyQt5 or PySide2 is available. It also checks if PyQt6 or PySide6 are not imported. The function sets up the application instance for Qt5Agg backend and issues a deprecation warning.
    
    Args:
    None
    
    Returns:
    None
    """

    import matplotlib.backends.backend_qt5agg  # noqa
    import sys

    assert 'PyQt6' not in sys.modules
    assert 'pyside6' not in sys.modules
    assert 'PyQt5' in sys.modules or 'pyside2' in sys.modules

    import matplotlib.backends.backend_qt5
    with pytest.warns(DeprecationWarning,
                      match="QtWidgets.QApplication.instance"):
        matplotlib.backends.backend_qt5.qApp


def _implcairo():
    """
    Initialize the Cairo backend for Matplotlib with PyQt5 or PySide2.
    
    This function imports the necessary backend for rendering graphics using
    Cairo with either PyQt5 or PySide2. It ensures that the correct backend is
    loaded by checking if PyQt6 or PySide6 are already imported, and raises an
    assertion error if they are. The function also checks if PyQt5 or PySide2
    is available and raises an assertion error if neither is found.
    
    The function
    """

    import matplotlib.backends.backend_qt5cairo # noqa
    import sys

    assert 'PyQt6' not in sys.modules
    assert 'pyside6' not in sys.modules
    assert 'PyQt5' in sys.modules or 'pyside2' in sys.modules

    import matplotlib.backends.backend_qt5
    with pytest.warns(DeprecationWarning,
                      match="QtWidgets.QApplication.instance"):
        matplotlib.backends.backend_qt5.qApp


def _implcore():
    """
    Initialize and return a Qt backend for Matplotlib.
    
    This function imports the necessary backend module, checks for the presence of specific modules, and returns an instance of `QtWidgets.QApplication`.
    
    :return: An instance of `QtWidgets.QApplication`.
    """

    import matplotlib.backends.backend_qt5
    import sys

    assert 'PyQt6' not in sys.modules
    assert 'pyside6' not in sys.modules
    assert 'PyQt5' in sys.modules or 'pyside2' in sys.modules

    with pytest.warns(DeprecationWarning,
                      match="QtWidgets.QApplication.instance"):
        matplotlib.backends.backend_qt5.qApp


def test_qt5backends_uses_qt5():
    """
    Test that the Qt5 backends use the correct bindings.
    
    This function checks for the availability of PyQt5 and PySide2 (QT5 bindings) and PyQt6 and PySide6 (QT6 bindings). If either set is empty, the test is skipped. The function then runs several helper functions (_implqt5agg, _implcairo, _implcore) with a specified timeout.
    
    Args:
    None
    
    Returns:
    None
    """

    qt5_bindings = [
        dep for dep in ['PyQt5', 'pyside2']
        if importlib.util.find_spec(dep) is not None
    ]
    qt6_bindings = [
        dep for dep in ['PyQt6', 'pyside6']
        if importlib.util.find_spec(dep) is not None
    ]
    if len(qt5_bindings) == 0 or len(qt6_bindings) == 0:
        pytest.skip('need both QT6 and QT5 bindings')
    _run_helper(_implqt5agg, timeout=_test_timeout)
    if importlib.util.find_spec('pycairo') is not None:
        _run_helper(_implcairo, timeout=_test_timeout)
    _run_helper(_implcore, timeout=_test_timeout)


def _impl_test_cross_Qt_imports():
    """
    Summary: This function imports necessary modules and sets up a QApplication object using the specified host binding. It then creates a qApp using the specified mpl binding and checks for mixing of Qt major versions.
    
    Args:
    host_binding (str): The name of the host binding module.
    mpl_binding (str): The name of the mpl binding module.
    
    Returns:
    None
    """

    import sys
    import importlib
    import pytest

    _, host_binding, mpl_binding = sys.argv
    # import the mpl binding.  This will force us to use that binding
    importlib.import_module(f'{mpl_binding}.QtCore')
    mpl_binding_qwidgets = importlib.import_module(f'{mpl_binding}.QtWidgets')
    import matplotlib.backends.backend_qt
    host_qwidgets = importlib.import_module(f'{host_binding}.QtWidgets')

    host_app = host_qwidgets.QApplication(["mpl testing"])
    with pytest.warns(UserWarning, match="Mixing Qt major"):
        matplotlib.backends.backend_qt._create_qApp()


def test_cross_Qt_imports():
    """
    Test cross-Qt imports by importing PyQt5/PySide2 and PyQt6/PySide6 bindings, and run helper function with different combinations of these bindings. Skip the test if either PyQt5/PySide2 or PyQt6/PySide6 bindings are not found. Handle specific exceptions such as segfault and abort signals during the test.
    """

    qt5_bindings = [
        dep for dep in ['PyQt5', 'PySide2']
        if importlib.util.find_spec(dep) is not None
    ]
    qt6_bindings = [
        dep for dep in ['PyQt6', 'PySide6']
        if importlib.util.find_spec(dep) is not None
    ]
    if len(qt5_bindings) == 0 or len(qt6_bindings) == 0:
        pytest.skip('need both QT6 and QT5 bindings')

    for qt5 in qt5_bindings:
        for qt6 in qt6_bindings:
            for pair in ([qt5, qt6], [qt6, qt5]):
                try:
                    _run_helper(_impl_test_cross_Qt_imports,
                                *pair,
                                timeout=_test_timeout)
                except subprocess.CalledProcessError as ex:
                    # if segfault, carry on.  We do try to warn the user they
                    # are doing something that we do not expect to work
                    if ex.returncode == -signal.SIGSEGV:
                        continue
                    # We got the abort signal which is likely because the Qt5 /
                    # Qt6 cross import is unhappy, carry on.
                    elif ex.returncode == -signal.SIGABRT:
                        continue
                    raise


@pytest.mark.skipif('TF_BUILD' in os.environ,
                    reason="this test fails an azure for unknown reasons")
@pytest.mark.skipif(os.name == "nt", reason="Cannot send SIGINT on Windows.")
def test_webagg():
    """
    Summary: This function tests the webagg backend by starting a subprocess with the specified Python code and checking if it can connect to the webagg server running on the given address and port. It uses the `subprocess` module to start the server and the `urllib.request` module to make a connection to the server. The function also uses the `pytest.importorskip` function to skip the test if the tornado package is not installed.
    
    Parameters: None
    
    Returns: None
    """

    pytest.importorskip("tornado")
    proc = subprocess.Popen(
        [sys.executable, "-c",
         inspect.getsource(_test_interactive_impl)
         + "\n_test_interactive_impl()", "{}"],
        env={**os.environ, "MPLBACKEND": "webagg", "SOURCE_DATE_EPOCH": "0"})
    url = "http://{}:{}".format(
        mpl.rcParams["webagg.address"], mpl.rcParams["webagg.port"])
    timeout = time.perf_counter() + _test_timeout
    while True:
        try:
            retcode = proc.poll()
            # check that the subprocess for the server is not dead
            assert retcode is None
            conn = urllib.request.urlopen(url)
            break
        except urllib.error.URLError:
            if time.perf_counter() > timeout:
                pytest.fail("Failed to connect to the webagg server.")
            else:
                continue
    conn.close()
    proc.send_signal(signal.SIGINT)
    assert proc.wait(timeout=_test_timeout) == 0


def _lazy_headless():
    """
    Lazyly sets the Matplotlib backend to a specified non-headless backend.
    
    This function is designed to simulate a headless environment by removing
    display-related environment variables and ensuring that certain dependencies
    are loaded. It then attempts to switch the Matplotlib backend to a specified
    non-headless backend and checks if the switch was successful.
    
    Args:
    backend (str): The name of the non-headless backend to set Matplotlib to.
    deps (str): A comma-separated
    """

    import os
    import sys

    backend, deps = sys.argv[1:]
    deps = deps.split(',')

    # make it look headless
    os.environ.pop('DISPLAY', None)
    os.environ.pop('WAYLAND_DISPLAY', None)
    for dep in deps:
        assert dep not in sys.modules

    # we should fast-track to Agg
    import matplotlib.pyplot as plt
    assert plt.get_backend() == 'agg'
    for dep in deps:
        assert dep not in sys.modules

    # make sure we really have dependencies installed
    for dep in deps:
        importlib.import_module(dep)
        assert dep in sys.modules

    # try to switch and make sure we fail with ImportError
    try:
        plt.switch_backend(backend)
    except ImportError:
        ...
    else:
        sys.exit(1)


@pytest.mark.skipif(sys.platform != "linux", reason="this a linux-only test")
@pytest.mark.parametrize("env", _get_testable_interactive_backends())
def test_lazy_linux_headless(env):
    """
    Test running a lazy headless environment with specified backend dependencies.
    
    Args:
    env (dict): A dictionary containing environment variables and their values.
    
    Returns:
    subprocess.Popen: The process object representing the running lazy headless environment.
    """

    proc = _run_helper(
        _lazy_headless,
        env.pop('MPLBACKEND'), env.pop("BACKEND_DEPS"),
        timeout=_test_timeout,
        extra_env={**env, 'DISPLAY': '', 'WAYLAND_DISPLAY': ''}
    )


def _qApp_warn_impl():
    """
    Generate a warning when attempting to access the QApplication instance.
    
    This function is designed to warn users about the deprecation of accessing
    `QtWidgets.QApplication.instance` within Matplotlib's backend code.
    
    :meta private:
    """

    import matplotlib.backends.backend_qt
    import pytest

    with pytest.warns(
            DeprecationWarning, match="QtWidgets.QApplication.instance"):
        matplotlib.backends.backend_qt.qApp


@pytest.mark.backend('QtAgg', skip_on_importerror=True)
def test_qApp_warn():
    _run_helper(_qApp_warn_impl, timeout=_test_timeout)


def _test_number_of_draws_script():
    """
    Test the number of redraws.
    
    This function creates a plot with an animated line and counts the number of times the plot is redrawn. It uses `matplotlib` for plotting and `blit` for efficient redrawing. The function connects to the 'draw_event' to track redraws and iterates through a loop to simulate multiple redraws, ensuring the screen updates appropriately.
    
    Parameters:
    None
    
    Returns:
    None
    """

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    # animated=True tells matplotlib to only draw the artist when we
    # explicitly request it
    ln, = ax.plot([0, 1], [1, 2], animated=True)

    # make sure the window is raised, but the script keeps going
    plt.show(block=False)
    plt.pause(0.3)
    # Connect to draw_event to count the occurrences
    fig.canvas.mpl_connect('draw_event', print)

    # get copy of entire figure (everything inside fig.bbox)
    # sans animated artist
    bg = fig.canvas.copy_from_bbox(fig.bbox)
    # draw the animated artist, this uses a cached renderer
    ax.draw_artist(ln)
    # show the result to the screen
    fig.canvas.blit(fig.bbox)

    for j in range(10):
        # reset the background back in the canvas state, screen unchanged
        fig.canvas.restore_region(bg)
        # Create a **new** artist here, this is poor usage of blitting
        # but good for testing to make sure that this doesn't create
        # excessive draws
        ln, = ax.plot([0, 1], [1, 2])
        # render the artist, updating the canvas state, but not the screen
        ax.draw_artist(ln)
        # copy the image to the GUI state, but screen might not changed yet
        fig.canvas.blit(fig.bbox)
        # flush any pending GUI events, re-painting the screen if needed
        fig.canvas.flush_events()

    # Let the event loop process everything before leaving
    plt.pause(0.1)


_blit_backends = _get_testable_interactive_backends()
for param in _blit_backends:
    backend = param.values[0]["MPLBACKEND"]
    if backend == "gtk3cairo":
        # copy_from_bbox only works when rendering to an ImageSurface
        param.marks.append(
            pytest.mark.skip("gtk3cairo does not support blitting"))
    elif backend == "gtk4cairo":
        # copy_from_bbox only works when rendering to an ImageSurface
        param.marks.append(
            pytest.mark.skip("gtk4cairo does not support blitting"))
    elif backend == "wx":
        param.marks.append(
            pytest.mark.skip("wx does not support blitting"))


@pytest.mark.parametrize("env", _blit_backends)
# subprocesses can struggle to get the display, so rerun a few times
@pytest.mark.flaky(reruns=4)
def test_blitting_events(env):
    """
    Tests the blitting functionality by running a script and counting the number of draw events generated. Ensures that the number of draw events falls within a specific range, indicating proper blitting implementation.
    
    Args:
    env (dict): Environment variables required to run the test script.
    
    Returns:
    None: The function asserts whether the number of draw events is within an expected range.
    """

    proc = _run_helper(
        _test_number_of_draws_script, timeout=_test_timeout, extra_env=env)
    # Count the number of draw_events we got. We could count some initial
    # canvas draws (which vary in number by backend), but the critical
    # check here is that it isn't 10 draws, which would be called if
    # blitting is not properly implemented
    ndraws = proc.stdout.count("DrawEvent")
    assert 0 < ndraws < 5


# The source of this function gets extracted and run in another process, so it
# must be fully self-contained.
def _test_figure_leak():
    """
    Test memory leak in Matplotlib figures.
    
    This function measures the memory usage before and after creating and closing multiple Matplotlib figures with optional pauses between them. It calculates the memory growth due to figure creation and helps identify potential memory leaks.
    
    Args:
    t (float): Pause time in seconds between figure creation and closing. If zero, no pause is performed.
    
    Returns:
    int: Memory growth in bytes after creating and closing the figures.
    """

    import gc
    import sys

    import psutil
    from matplotlib import pyplot as plt
    # Second argument is pause length, but if zero we should skip pausing
    t = float(sys.argv[1])
    p = psutil.Process()

    # Warmup cycle, this reasonably allocates a lot
    for _ in range(2):
        fig = plt.figure()
        if t:
            plt.pause(t)
        plt.close(fig)
    mem = p.memory_info().rss
    gc.collect()

    for _ in range(5):
        fig = plt.figure()
        if t:
            plt.pause(t)
        plt.close(fig)
        gc.collect()
    growth = p.memory_info().rss - mem

    print(growth)


# TODO: "0.1" memory threshold could be reduced 10x by fixing tkagg
@pytest.mark.skipif(sys.platform == "win32",
                    reason="appveyor tests fail; gh-22988 suggests reworking")
@pytest.mark.parametrize("env", _get_testable_interactive_backends())
@pytest.mark.parametrize("time_mem", [(0.0, 2_000_000), (0.1, 30_000_000)])
def test_figure_leak_20490(env, time_mem):
    """
    Test for memory leakage in figure creation.
    
    This function checks for memory leakage when creating figures using the specified backend. It uses the `psutil` library to monitor memory usage over time. The test is skipped for certain backends like 'wx' and 'macosx'. For the 'tkagg' backend on macOS, an additional allowance for memory leakage is made.
    
    Parameters:
    -----------
    env : dict
    Environment variables to be passed to the test.
    time_mem :
    """

    pytest.importorskip("psutil", reason="psutil needed to run this test")

    # We haven't yet directly identified the leaks so test with a memory growth
    # threshold.
    pause_time, acceptable_memory_leakage = time_mem
    if env["MPLBACKEND"] == "wx":
        pytest.skip("wx backend is deprecated; tests failed on appveyor")

    if env["MPLBACKEND"] == "macosx" or (
            env["MPLBACKEND"] == "tkagg" and sys.platform == 'darwin'
    ):
        acceptable_memory_leakage += 11_000_000

    result = _run_helper(
        _test_figure_leak, str(pause_time),
        timeout=_test_timeout, extra_env=env)

    growth = int(result.stdout)
    assert growth <= acceptable_memory_leakage
