# Licensed under a 3-clause BSD style license - see LICENSE.rst


from io import StringIO

import numpy as np

from ... import ascii

from .common import assert_equal


def test_types_from_dat():
    """
    Reads a table from a string using the `ascii.Basic` reader with specified converters and returns a `Table` object.
    
    Parameters:
    dat (str): A string containing the table data.
    
    Returns:
    Table: A `Table` object with the data from the input string, where the data types of the columns are converted according to the provided converters.
    
    Key Parameters:
    - `converters` (dict): A dictionary specifying the converters for each column. The keys are column names and the
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
    Test writing different data types using the RDB format.
    
    This function reads a table with mixed data types (integers, floats, strings, and floats) and writes it to an RDB file format. The function then checks the written file to ensure that the correct data types are specified for each column.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    - The input data contains a mix of integer, float, string, and float values.
    - The output is checked to ensure
    """

    dat = ascii.read(['a b c d', '1 1.0 cat 2.1'],
                     Reader=ascii.Basic)
    out = StringIO()
    ascii.write(dat, out, Writer=ascii.Rdb)
    outs = out.getvalue().splitlines()
    assert_equal(outs[1], 'N\tN\tS\tN')


def test_ipac_read_types():
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
      assert_equal(col.type, expected_type)
