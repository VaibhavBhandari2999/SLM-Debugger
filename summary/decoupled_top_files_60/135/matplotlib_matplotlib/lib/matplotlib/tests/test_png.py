from io import BytesIO
from pathlib import Path

import pytest

from matplotlib.testing.decorators import image_comparison
from matplotlib import cm, pyplot as plt


@image_comparison(['pngsuite.png'], tol=0.03)
def test_pngsuite():
    """
    Test PNGSuite baseline images.
    
    This function displays a series of PNGSuite baseline images in a single figure.
    
    Parameters:
    None
    
    Returns:
    None: The function displays a matplotlib figure with the images and does not return any value.
    
    Notes:
    - The images are read from the 'baseline_images/pngsuite' directory.
    - The images are displayed in a figure with a size of (number of images, 2).
    - Each image is displayed with an extent that spans one unit in
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
    Function: test_truncated_buffer
    
    This function tests the behavior of reading a truncated buffer using the `BytesIO` class and `plt.imread` function.
    
    Parameters:
    None
    
    Returns:
    None
    
    Description:
    1. Creates a `BytesIO` object `b` to handle in-memory byte streams.
    2. Saves a plot to the buffer `b` using `plt.savefig(b)`.
    3. Seeks to the beginning of the buffer `b` using `b.seek(0)`.
    """

    b = BytesIO()
    plt.savefig(b)
    b.seek(0)
    b2 = BytesIO(b.read(20))
    b2.seek(0)

    with pytest.raises(Exception):
        plt.imread(b2)
