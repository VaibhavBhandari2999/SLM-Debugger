from io import BytesIO
from pathlib import Path

import pytest

from matplotlib.testing.decorators import image_comparison
from matplotlib import cm, pyplot as plt


@image_comparison(['pngsuite.png'], tol=0.03)
def test_pngsuite():
    """
    Test PNGSuite images.
    
    This function loads and displays a series of PNG images from the `PNGSuite` baseline images directory. The images are displayed in a figure with a specified size, and each image is plotted with an extent that corresponds to its position in the sequence. Grayscale images are displayed using the 'gray' colormap.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `sorted()`: Sorts the file paths.
    - `Path(__
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
    """
    Test saving and truncating an image file.
    
    This function creates a temporary directory and saves a PNG image to it.
    The image is then truncated by writing only the first 20 bytes to a new
    file. The truncated file is expected to raise an exception when read using
    `plt.imread`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `tmpdir.mkdir`: Creates a subdirectory within a temporary directory.
    - `str
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
    Test saving and reading an image from a truncated buffer.
    
    This function creates a BytesIO object, saves a plot to it, and then attempts to read a truncated version of the buffer using `BytesIO.read`. It raises an exception if the truncated buffer is successfully read by `plt.imread`.
    
    Args:
    None
    
    Returns:
    None
    """

    b = BytesIO()
    plt.savefig(b)
    b.seek(0)
    b2 = BytesIO(b.read(20))
    b2.seek(0)

    with pytest.raises(Exception):
        plt.imread(b2)
