from io import BytesIO
from pathlib import Path

import pytest

from matplotlib.testing.decorators import image_comparison
from matplotlib import cm, pyplot as plt


@image_comparison(['pngsuite.png'], tol=0.03)
def test_pngsuite():
    """
    Test PNGSuite baseline images.
    
    This function displays a series of PNGSuite baseline images in a matplotlib figure. Each image is displayed as a separate vertical strip.
    
    Parameters:
    None
    
    Returns:
    None: The function generates a matplotlib figure and does not return any value.
    
    Usage:
    Call the function `test_pngsuite()` to display the PNGSuite baseline images.
    """

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


def test_truncated_file(tmp_path):
    path = tmp_path / 'test.png'
    path_t = tmp_path / 'test_truncated.png'
    plt.savefig(path)
    with open(path, 'rb') as fin:
        buf = fin.read()
    with open(path_t, 'wb') as fout:
        fout.write(buf[:20])

    with pytest.raises(Exception):
        plt.imread(path_t)


def test_truncated_buffer():
    """
    Function to test the behavior of saving and reading a truncated buffer.
    
    This function creates a BytesIO object, saves a plot to it, and then attempts to read a truncated version of the buffer to check for expected exceptions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    Exception: If the truncated buffer can be read without raising an exception, indicating a potential issue with buffer truncation.
    
    Notes:
    - A BytesIO object is used to save the plot.
    - The buffer is
    """

    b = BytesIO()
    plt.savefig(b)
    b.seek(0)
    b2 = BytesIO(b.read(20))
    b2.seek(0)

    with pytest.raises(Exception):
        plt.imread(b2)
