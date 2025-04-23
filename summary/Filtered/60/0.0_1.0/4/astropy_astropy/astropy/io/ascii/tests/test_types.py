# Licensed under a 3-clause BSD style license - see LICENSE.rst


from io import StringIO

import numpy as np

from ... import ascii

from .common import assert_equal


def test_types_from_dat():
    """
    Reads data from a string or file and returns an astropy.table.Table object.
    
    Parameters:
    dat (str or file-like object): The data to be read.
    
    Keyword Arguments:
    Reader (class): The class to use for reading the data. Default is ascii.Basic.
    converters (dict): A dictionary specifying converters for specific columns. Keys are column names or indices, and values are lists of converter functions.
    
    Returns:
    astropy.table.Table: The table containing the data read from the
    """

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
    """
    Test RDB writer for different data types.
    
    This function reads a table with mixed data types (integers, floats, strings, and
    floats) and writes it to a string buffer using the RDB (Red-Black Database)
    format. The function then checks the header of the written data to ensure that
    the correct column types are specified.
    
    Parameters:
    None
    
    Returns:
    None
    
    This test ensures that the RDB writer correctly identifies and labels the
    data types of the columns
    """

    dat = ascii.read(['a b c d', '1 1.0 cat 2.1'],
                     Reader=ascii.Basic)
    out = StringIO()
    ascii.write(dat, out, Writer=ascii.Rdb)
    outs = out.getvalue().splitlines()
    assert_equal(outs[1], 'N\tN\tS\tN')


def test_ipac_read_types():
    """
    Reads and validates the IPAC table format to ensure correct column types.
    
    This function tests the IPAC table format by reading a provided table and
    verifying that each column has the correct type. The expected types for each
    column are specified in the `types` list.
    
    Parameters:
    table (str): A string containing the IPAC formatted table data.
    
    Returns:
    None: The function asserts that each column has the correct type, and
    raises an AssertionError if any column type does
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
