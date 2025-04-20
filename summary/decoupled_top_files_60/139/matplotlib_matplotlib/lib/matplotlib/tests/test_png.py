from io import BytesIO
from pathlib import Path

import pytest

from matplotlib.testing.decorators import image_comparison
from matplotlib import cm, pyplot as plt


@image_comparison(['pngsuite.png'], tol=0.03)
def test_pngsuite():
    """
    Test PNGSuite images.
    
    This function displays a series of PNGSuite baseline images in a single figure. Each image is displayed as a separate subplot along the x-axis.
    
    Parameters:
    None
    
    Returns:
    None: This function does not return any value. It displays the images using matplotlib.
    
    Notes:
    - The images are read from the 'baseline_images/pngsuite' directory and are named 'basn*.png'.
    - The images are displayed in a figure with a specified size.
    -
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
    Function to test the behavior of truncated buffer when saving and reading an image using matplotlib and BytesIO.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    Exception: If the truncated buffer (b2) is not large enough to contain a valid image, an exception is raised when attempting to read the image using plt.imread.
    
    This function creates a BytesIO buffer, saves a plot to it, and then attempts to read a truncated version of the buffer to simulate a scenario where the buffer might
    """

    b = BytesIO()
    plt.savefig(b)
    b.seek(0)
    b2 = BytesIO(b.read(20))
    b2.seek(0)

    with pytest.raises(Exception):
        plt.imread(b2)
