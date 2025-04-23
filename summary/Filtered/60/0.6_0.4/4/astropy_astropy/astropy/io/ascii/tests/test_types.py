# Licensed under a 3-clause BSD style license - see LICENSE.rst


from io import StringIO

import numpy as np

from ... import ascii

from .common import assert_equal


def test_types_from_dat():
    converters = {'a': [ascii.convert_numpy(float)],
                  'e': [ascii.convert_numpy(str)]}

    dat = ascii.read(['a b c d e', '1 1 cat 2.1 4.2'],
                     Reader=ascii.Basic,
                     converters=converters)

    assert dat['a'].dtype.kind == 'f'
    assert dat['b'].dtype.kind == 'i'
    assert dat['c'].dtype.kind in ('S', 'U')
    assert dat['d'].dtype.kind == 'f'
    assert dat['e'].dtype.kind in ('S', 'U')


def test_rdb_write_types():
    dat = ascii.read(['a b c d', '1 1.0 cat 2.1'],
                     Reader=ascii.Basic)
    out = StringIO()
    ascii.write(dat, out, Writer=ascii.Rdb)
    outs = out.getvalue().splitlines()
    assert_equal(outs[1], 'N\tN\tS\tN')


def test_ipac_read_types():
    """
    Reads and checks the data types of columns in an IPAC formatted table.
    
    This function reads an IPAC formatted table and verifies the data types of each column against expected types.
    
    Parameters:
    table (str): The IPAC formatted table as a string.
    
    Returns:
    None: The function asserts the correctness of the data types but does not return any value.
    
    Example:
    >>> test_ipac_read_types()
    # The function will assert that the data types of the columns match the expected types
    """

    table = r"""\
|     ra   |    dec   |   sai   |-----v2---|    sptype        |
|    real  |   float  |   l     |    real  |     char         |
|    unit  |   unit   |   unit  |    unit  |     ergs         |
|    null  |   null   |   null  |    null  |     -999         |
   2.09708   2956        73765    2.06000   B8IVpMnHg
"""
    reader = ascii.get_reader(Reader=ascii.Ipac)
    dat = reader.read(table)
    types = [ascii.FloatType,
             ascii.FloatType,
             ascii.IntType,
             ascii.FloatType,
             ascii.StrType]
    for (col, expected_type) in zip(reader.cols, types):
        assert_equal(col.type, expected_type)
