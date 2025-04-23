# Licensed under a 3-clause BSD style license - see LICENSE.rst
import os
import sys

import pytest
import numpy as np

from .. import read

ROOT = os.path.abspath(os.path.dirname(__file__))


try:
    import bz2  # pylint: disable=W0611
except ImportError:
    HAS_BZ2 = False
else:
    HAS_BZ2 = True

try:
    import lzma
except ImportError:
    HAS_XZ = False
else:
    HAS_XZ = True


@pytest.mark.parametrize('filename', ['t/daophot.dat.gz', 't/latex1.tex.gz',
                                      't/short.rdb.gz'])
def test_gzip(filename):
    t_comp = read(os.path.join(ROOT, filename))
    t_uncomp = read(os.path.join(ROOT, filename.replace('.gz', '')))
    assert t_comp.dtype.names == t_uncomp.dtype.names
    assert np.all(t_comp.as_array() == t_uncomp.as_array())


@pytest.mark.xfail('not HAS_BZ2')
@pytest.mark.parametrize('filename', ['t/short.rdb.bz2', 't/ipac.dat.bz2'])
def test_bzip2(filename):
    """
    Test the bzip2 compression of a table.
    
    Parameters:
    filename (str): The name of the file to test, which should be a bzip2 compressed file.
    
    This function reads a bzip2 compressed file and its corresponding uncompressed version, compares their data types and arrays, and asserts that they are identical.
    """

    t_comp = read(os.path.join(ROOT, filename))
    t_uncomp = read(os.path.join(ROOT, filename.replace('.bz2', '')))
    assert t_comp.dtype.names == t_uncomp.dtype.names
    assert np.all(t_comp.as_array() == t_uncomp.as_array())


@pytest.mark.xfail('not HAS_XZ')
@pytest.mark.parametrize('filename', ['t/short.rdb.xz', 't/ipac.dat.xz'])
def test_xz(filename):
    """
    Test if a compressed file (in .xz format) matches its uncompressed version.
    
    This function reads a compressed file and its corresponding uncompressed file,
    compares their data types and arrays, and asserts that they are identical.
    
    Parameters:
    filename (str): The name of the compressed file to be tested, expected to end with '.xz'.
    
    Returns:
    None: The function does not return any value. It raises an AssertionError if the compressed
    and uncompressed files do not match.
    
    Notes:
    """

    t_comp = read(os.path.join(ROOT, filename))
    t_uncomp = read(os.path.join(ROOT, filename.replace('.xz', '')))
    assert t_comp.dtype.names == t_uncomp.dtype.names
    assert np.all(t_comp.as_array() == t_uncomp.as_array())
