from io import BytesIO
from pathlib import Path

import pytest

from matplotlib.testing.decorators import image_comparison
from matplotlib import cm, pyplot as plt


@image_comparison(['pngsuite.png'], tol=0.03)
def test_pngsuite():
    """
    Test PNGSuite baseline images.
    
    This function displays a series of PNGSuite baseline images in a figure. Each image is displayed as a separate vertical strip, with the index of the image along the x-axis.
    
    Parameters:
    None
    
    Returns:
    None: The function generates a matplotlib figure and does not return any value.
    
    Usage:
    test_pngsuite()
    
    Key Points:
    - The images are read from the 'baseline_images/pngsuite' directory.
    - The images are displayed in a figure with
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


def test_truncated_file(tmpdir):
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
    Function to test the behavior of truncated buffer when saving and reading an image using matplotlib and BytesIO.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    Exception: If the truncated buffer cannot be read as an image, indicating the truncation was too severe.
    
    Explanation:
    This function creates a BytesIO buffer, saves a plot to it, and then truncates the buffer to a specified size. It then attempts to read the truncated buffer as an image using plt.imread. If the buffer
    """

    b = BytesIO()
    plt.savefig(b)
    b.seek(0)
    b2 = BytesIO(b.read(20))
    b2.seek(0)

    with pytest.raises(Exception):
        plt.imread(b2)
