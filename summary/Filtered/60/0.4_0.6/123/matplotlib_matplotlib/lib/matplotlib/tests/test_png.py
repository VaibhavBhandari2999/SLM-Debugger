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
    Function to test the behavior of truncated buffer when saving and reading an image.
    
    This function creates a BytesIO buffer, saves a plot to it, and then attempts to read a truncated version of the buffer to check for expected exceptions.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    Exception: If the truncated buffer is successfully read, indicating a potential issue with buffer truncation.
    
    Usage:
    test_truncated_buffer()
    """

    b = BytesIO()
    plt.savefig(b)
    b.seek(0)
    b2 = BytesIO(b.read(20))
    b2.seek(0)

    with pytest.raises(Exception):
        plt.imread(b2)
