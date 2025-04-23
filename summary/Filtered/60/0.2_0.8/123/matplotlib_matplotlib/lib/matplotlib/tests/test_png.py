from io import BytesIO
from pathlib import Path

import pytest

from matplotlib.testing.decorators import image_comparison
from matplotlib import cm, pyplot as plt


@image_comparison(['pngsuite.png'], tol=0.03)
def test_pngsuite():
    files = sorted(
        (Path(__file__).parent / "baseline_images/pngsuite").glob("basn*.png"))

    plt.figure(figsize=(len(files), 2))

    for i, fname in enumerate(files):
        data = plt.imread(fname)
        cmap = None  # use default colormap
        if data.ndim == 2:
            # keep grayscale images gray
            cmap = cm.gray
        plt.imshow(data, extent=[i, i + 1, 0, 1], cmap=cmap)

    plt.gca().patch.set_facecolor("#ddffff")
    plt.gca().set_xlim(0, len(files))


def test_truncated_file(tmpdir):
    """
    Test function to check the behavior of image loading with a truncated file.
    
    This function creates a test directory and saves a PNG image to it. It then truncates the saved file to a smaller size and attempts to load the truncated file using `plt.imread`. If the truncated file cannot be loaded, an exception is raised, indicating that the function is working as expected.
    
    Parameters:
    tmpdir (py.path.local): A temporary directory object provided by pytest for creating and managing temporary files and directories.
    
    Returns
    """

    d = tmpdir.mkdir('test')
    fname = str(d.join('test.png'))
    fname_t = str(d.join('test_truncated.png'))
    plt.savefig(fname)
    with open(fname, 'rb') as fin:
        buf = fin.read()
    with open(fname_t, 'wb') as fout:
        fout.write(buf[:20])

    with pytest.raises(Exception):
        plt.imread(fname_t)


def test_truncated_buffer():
    """
    Function to test the behavior of a truncated buffer when used with `plt.imread`.
    
    Parameters:
    None
    
    Returns:
    None
    
    This function creates a BytesIO buffer, saves a plot to it, and then attempts to read a truncated version of the buffer to check if `plt.imread` raises an exception as expected.
    
    Key Points:
    - A BytesIO buffer `b` is created and a plot is saved to it using `plt.savefig(b)`.
    - The buffer `b` is then seek
    """

    b = BytesIO()
    plt.savefig(b)
    b.seek(0)
    b2 = BytesIO(b.read(20))
    b2.seek(0)

    with pytest.raises(Exception):
        plt.imread(b2)
