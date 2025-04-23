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
    Test if a BZIP2-compressed file is equivalent to its uncompressed counterpart.
    
    This function reads a BZIP2-compressed file and its corresponding uncompressed file, compares their data, and ensures they are identical.
    
    Parameters:
    filename (str): The name of the BZIP2-compressed file to test.
    
    Returns:
    None: The function asserts that the compressed and uncompressed files are identical. If they are not, an AssertionError is raised.
    """

    t_comp = read(os.path.join(ROOT, filename))
    t_uncomp = read(os.path.join(ROOT, filename.replace('.bz2', '')))
    assert t_comp.dtype.names == t_uncomp.dtype.names
    assert np.all(t_comp.as_array() == t_uncomp.as_array())


@pytest.mark.xfail('not HAS_XZ')
@pytest.mark.parametrize('filename', ['t/short.rdb.xz', 't/ipac.dat.xz'])
def test_xz(filename):
    """
    Test if the compressed and uncompressed versions of a file have the same data.
    
    Parameters:
    filename (str): The name of the file to be tested. The function expects a file with a '.xz' extension, and also looks for an uncompressed version of the file with the same name but without the '.xz' extension.
    
    This function reads in a compressed file and its corresponding uncompressed version, then checks if they have the same structure and data. It asserts that the data arrays of the compressed and uncompressed
    """

    t_comp = read(os.path.join(ROOT, filename))
    t_uncomp = read(os.path.join(ROOT, filename.replace('.xz', '')))
    assert t_comp.dtype.names == t_uncomp.dtype.names
    assert np.all(t_comp.as_array() == t_uncomp.as_array())
