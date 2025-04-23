import pytest
import sys
import matplotlib
from matplotlib import _api


def pytest_configure(config):
    """
    Configure pytest for Matplotlib testing.
    
    This function is called by pytest during its initialization. It configures
    pytest with various markers and filterwarnings to handle specific testing
    requirements for Matplotlib. It also sets the default backend for Matplotlib
    to 'agg' and marks the function as being called from pytest.
    
    Parameters:
    config (pytest.Config): The pytest configuration object.
    
    Returns:
    None: This function does not return any value. It modifies the pytest
    configuration in place.
    
    Key Mark
    """

    # config is initialized here rather than in pytest.ini so that `pytest
    # --pyargs matplotlib` (which would not find pytest.ini) works.  The only
    # entries in pytest.ini set minversion (which is checked earlier),
    # testpaths/python_files, as they are required to properly find the tests
    for key, value in [
        ("markers", "flaky: (Provided by pytest-rerunfailures.)"),
        ("markers", "timeout: (Provided by pytest-timeout.)"),
        ("markers", "backend: Set alternate Matplotlib backend temporarily."),
        ("markers", "baseline_images: Compare output against references."),
        ("markers", "pytz: Tests that require pytz to be installed."),
        ("filterwarnings", "error"),
        ("filterwarnings",
         "ignore:.*The py23 module has been deprecated:DeprecationWarning"),
        ("filterwarnings",
         r"ignore:DynamicImporter.find_spec\(\) not found; "
         r"falling back to find_module\(\):ImportWarning"),
    ]:
        config.addinivalue_line(key, value)

    matplotlib.use('agg', force=True)
    matplotlib._called_from_pytest = True
    matplotlib._init_tests()


def pytest_unconfigure(config):
    matplotlib._called_from_pytest = False


@pytest.fixture(autouse=True)
def mpl_test_settings(request):
    """
    mpl_test_settings(request)
    
    This function sets up a testing environment for Matplotlib, ensuring that the backend is correctly configured and that any necessary cleanup is performed. It is designed to be used as a fixture in pytest.
    
    Parameters:
    - request: The pytest request object, which provides information about the current test.
    
    Key Parameters:
    - backend: (Optional) A string specifying the Matplotlib backend to use for the test. If provided, the function will attempt to switch to this backend. If the specified backend
    """

    from matplotlib.testing.decorators import _cleanup_cm

    with _cleanup_cm():

        backend = None
        backend_marker = request.node.get_closest_marker('backend')
        prev_backend = matplotlib.get_backend()
        if backend_marker is not None:
            assert len(backend_marker.args) == 1, \
                "Marker 'backend' must specify 1 backend."
            backend, = backend_marker.args
            skip_on_importerror = backend_marker.kwargs.get(
                'skip_on_importerror', False)

            # special case Qt backend importing to avoid conflicts
            if backend.lower().startswith('qt5'):
                if any(sys.modules.get(k) for k in ('PyQt4', 'PySide')):
                    pytest.skip('Qt4 binding already imported')

        matplotlib.testing.setup()
        with _api.suppress_matplotlib_deprecation_warning():
            if backend is not None:
                # This import must come after setup() so it doesn't load the
                # default backend prematurely.
                import matplotlib.pyplot as plt
                try:
                    plt.switch_backend(backend)
                except ImportError as exc:
                    # Should only occur for the cairo backend tests, if neither
                    # pycairo nor cairocffi are installed.
                    if 'cairo' in backend.lower() or skip_on_importerror:
                        pytest.skip("Failed to switch to backend {} ({})."
                                    .format(backend, exc))
                    else:
                        raise
            # Default of cleanup and image_comparison too.
            matplotlib.style.use(["classic", "_classic_test_patch"])
        try:
            yield
        finally:
            matplotlib.use(prev_backend)


@pytest.fixture
def pd():
    """Fixture to import and configure pandas."""
    pd = pytest.importorskip('pandas')
    try:
        from pandas.plotting import (
            deregister_matplotlib_converters as deregister)
        deregister()
    except ImportError:
        pass
    return pd


@pytest.fixture
def xr():
    """Fixture to import xarray."""
    xr = pytest.importorskip('xarray')
    return xr
