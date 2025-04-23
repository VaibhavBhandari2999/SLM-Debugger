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
    Test that a bz2 compressed file can be read and compared to its uncompressed version.
    
    Parameters:
    filename (str): The name of the bz2 compressed file to be tested.
    
    This function reads a bz2 compressed file and its uncompressed version, compares them, and asserts that they have the same names and values in their arrays.
    """

    t_comp = read(os.path.join(ROOT, filename))
    t_uncomp = read(os.path.join(ROOT, filename.replace('.bz2', '')))
    assert t_comp.dtype.names == t_uncomp.dtype.names
    assert np.all(t_comp.as_array() == t_uncomp.as_array())


@pytest.mark.xfail('not HAS_XZ')
@pytest.mark.parametrize('filename', ['t/short.rdb.xz', 't/ipac.dat.xz'])
def test_xz(filename):
    """
    Test if the compressed file 'filename.xz' is equivalent to the uncompressed file 'filename'.
    
    Parameters:
    filename (str): The name of the compressed file to test, without the .xz extension.
    
    This function reads both the compressed and uncompressed versions of the file, compares their data types and arrays, and asserts that they are identical.
    """

    t_comp = read(os.path.join(ROOT, filename))
    t_uncomp = read(os.path.join(ROOT, filename.replace('.xz', '')))
    assert t_comp.dtype.names == t_uncomp.dtype.names
    assert np.all(t_comp.as_array() == t_uncomp.as_array())
