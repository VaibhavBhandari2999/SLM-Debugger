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
    assert fig.canvas.get_renderer()._renderer is not None

    fig = plt.figure(2)
    fig.draw_without_rendering()
    assert fig.canvas.get_renderer()._renderer is not None


@pytest.mark.backend('macosx')
def test_savefig_rcparam(monkeypatch, tmp_path):
    """
    Tests the functionality of saving a figure with updated rcParams.
    
    This function simulates saving a figure using a default filename in a specified directory. It uses a monkeypatch to replace the `choose_save_file` function with a custom implementation that creates a new directory for testing and returns a specific file path. The function then checks if the file is saved correctly and if the `savefig.directory` rcParam is updated to reflect the new directory.
    
    Parameters:
    - monkeypatch (pytest MonkeyPatch): A fixture
    """


    def new_choose_save_file(title, directory, filename):
        """
        Generate a new file path for saving a file.
        
        This function is designed to replace the functionality of opening a GUI window to choose a save file. Instead, it creates a new directory within the specified directory and returns a new file path for the given filename.
        
        Parameters:
        title (str): The title of the file dialog, not used in this function.
        directory (str): The base directory where the new directory will be created.
        filename (str): The name of the file to be saved
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
