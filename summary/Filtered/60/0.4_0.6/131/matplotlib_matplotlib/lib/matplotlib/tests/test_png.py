from io import BytesIO
from pathlib import Path

import pytest

from matplotlib.testing.decorators import image_comparison
from matplotlib import cm, pyplot as plt


@image_comparison(['pngsuite.png'], tol=0.03)
def test_pngsuite():
    """
    Test PNGSuite images.
    
    This function displays a series of PNGSuite baseline images in a single figure.
    
    Parameters:
    None
    
    Returns:
    None: The function displays a matplotlib figure with the images and does not return any value.
    
    Notes:
    - The images are read from the 'baseline_images/pngsuite' directory.
    - The images are displayed in a grid format, with each image occupying a row.
    - The function uses matplotlib to create the figure and display the images.
    - The
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
    Test function to check the behavior of `plt.imread` with a truncated image file.
    
    This function creates a temporary directory and saves a PNG image file to it. It then truncates the file to a specified size and checks if `plt.imread` raises an exception when trying to read the truncated file.
    
    Parameters:
    tmpdir (py.path.local): A temporary directory object provided by pytest for creating and managing temporary files and directories.
    
    Returns:
    None: The function does not return any value. It
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
    b = BytesIO()
    plt.savefig(b)
    b.seek(0)
    b2 = BytesIO(b.read(20))
    b2.seek(0)

    with pytest.raises(Exception):
        plt.imread(b2)
