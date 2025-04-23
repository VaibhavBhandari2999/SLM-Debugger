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
    """
    Tests the cached renderer functionality for Matplotlib figures.
    
    This function checks that figures have an associated renderer after a draw
    call, whether it's a normal draw or a draw without rendering.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # Make sure that figures have an associated renderer after
    # a fig.canvas.draw() call
    fig = plt.figure(1)
    fig.canvas.draw()
    assert fig.canvas.get_renderer()._renderer is not None

    fig = plt.figure(2)
    fig.draw_without_rendering()
    assert fig.canvas.get_renderer()._renderer is not None


@pytest.mark.backend('macosx')
def test_savefig_rcparam(monkeypatch, tmp_path):
    """
    Test the functionality of saving a figure to a specified directory with updated rcParams.
    
    This function simulates the process of saving a figure using the `save_figure` method of a figure canvas. It uses a monkeypatch to replace the `choose_save_file` function with a custom implementation that creates a new directory for testing and returns a specific file path. The function also updates the `savefig.directory` rcParam to the specified directory.
    
    Parameters:
    monkeypatch (pytest.MonkeyPatch): A pytest
    """


    def new_choose_save_file(title, directory, filename):
        """
        Generate a new file path for saving a file.
        
        This function is designed to replace the functionality of a graphical user interface (GUI) window for choosing a save file. Instead, it creates a new directory within the specified directory and returns a new file path for saving the file.
        
        Parameters:
        title (str): The title of the file dialog, which is not used in this function.
        directory (str): The base directory where the new directory will be created.
        filename (str): The name
        """

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
