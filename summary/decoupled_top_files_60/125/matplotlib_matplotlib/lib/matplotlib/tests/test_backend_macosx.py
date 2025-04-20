import os

import pytest

import matplotlib as mpl
import matplotlib.pyplot as plt
try:
    from matplotlib.backends import _macosx
except ImportError:
    pytest.skip("These are mac only tests", allow_module_level=True)


@pytest.mark.backend('macosx')
def test_cached_renderer():
    # Make sure that figures have an associated renderer after
    # a fig.canvas.draw() call
    fig = plt.figure(1)
    fig.canvas.draw()
    assert fig._cachedRenderer is not None

    fig = plt.figure(2)
    fig.draw_without_rendering()
    assert fig._cachedRenderer is not None


@pytest.mark.backend('macosx')
def test_savefig_rcparam(monkeypatch, tmp_path):
    """
    Test the functionality of saving a figure with updated rcParams.
    
    This function simulates saving a figure using the `save_figure` method of a figure's canvas. It uses a monkeypatch to replace the `choose_save_file` function with a custom implementation that creates a new directory for testing and returns a specific file path. The function also uses a context manager to temporarily update the `savefig.directory` rcParam to a specified directory.
    
    Parameters:
    monkeypatch (pytest MonkeyPatch): A pytest fixture
    """


    def new_choose_save_file(title, directory, filename):
        # Replacement function instead of opening a GUI window
        # Make a new directory for testing the update of the rcParams
        assert directory == str(tmp_path)
        os.makedirs(f"{directory}/test")
        return f"{directory}/test/{filename}"

    monkeypatch.setattr(_macosx, "choose_save_file", new_choose_save_file)
    fig = plt.figure()
    with mpl.rc_context({"savefig.directory": tmp_path}):
        fig.canvas.toolbar.save_figure()
        # Check the saved location got created
        save_file = f"{tmp_path}/test/{fig.canvas.get_default_filename()}"
        assert os.path.exists(save_file)

        # Check the savefig.directory rcParam got updated because
        # we added a subdirectory "test"
        assert mpl.rcParams["savefig.directory"] == f"{tmp_path}/test"
