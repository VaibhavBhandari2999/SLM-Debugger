# Licensed under a 3-clause BSD style license - see LICENSE.rst

import sys

import numpy as np
import pytest

from astropy import table
from astropy import units as u
from astropy.table import Row

from .conftest import MaskedTable


def test_masked_row_with_object_col():
    """
    Numpy < 1.8 has a bug in masked array that prevents access a row if there is
    a column with object type.
    """
    t = table.Table([[1]], dtype=["O"], masked=True)
    t["col0"].mask = False
    assert t[0]["col0"] == 1
    t["col0"].mask = True
    assert t[0]["col0"] is np.ma.masked


@pytest.mark.usefixtures("table_types")
class TestRow:
    def _setup(self, table_types):
        self._table_type = table_types.Table
        self._column_type = table_types.Column

    @property
    def t(self):
        """
        Generates a table from column data.
        
        This method creates a table using the specified column type and data. It ensures that the table is only created once by storing it in an instance attribute `_t`. If the column type is not set (`_column_type` is `None`), the method returns `None`.
        
        Parameters:
        None
        
        Returns:
        A table object of type `_table_type` containing columns of type `_column_type`, or `None` if `_column_type`
        """

        # pytest wants to run this method once before table_types is run
        # to set Table and Column.  In this case just return None, which would
        # cause any downstream test to fail if this happened in any other context.
        if self._column_type is None:
            return None
        if not hasattr(self, "_t"):
            a = self._column_type(name="a", data=[1, 2, 3], dtype="i8")
            b = self._column_type(name="b", data=[4, 5, 6], dtype="i8")
            self._t = self._table_type([a, b])
        return self._t

    def test_subclass(self, table_types):
        """Row is subclass of ndarray and Row"""
        self._setup(table_types)
        c = Row(self.t, 2)
        assert isinstance(c, Row)

    def test_values(self, table_types):
        """Row accurately reflects table values and attributes"""
        self._setup(table_types)
        table = self.t
        row = table[1]
        assert row["a"] == 2
        assert row["b"] == 5
        assert row[0] == 2
        assert row[1] == 5
        assert row.meta is table.meta
        assert row.colnames == table.colnames
        assert row.columns is table.columns
        with pytest.raises(IndexError):
            row[2]
        if sys.byteorder == "little":
            assert str(row.dtype) == "[('a', '<i8'), ('b', '<i8')]"
        else:
            assert str(row.dtype) == "[('a', '>i8'), ('b', '>i8')]"

    def test_ref(self, table_types):
        """Row is a reference into original table data"""
        self._setup(table_types)
        table = self.t
        row = table[1]
        row["a"] = 10
        if table_types.Table is not MaskedTable:
            assert table["a"][1] == 10

    def test_left_equal(self, table_types):
        """Compare a table row to the corresponding structured array row"""
        self._setup(table_types)
        np_t = self.t.as_array()
        if table_types.Table is MaskedTable:
            with pytest.raises(ValueError):
                self.t[0] == np_t[0]
        else:
            for row, np_row in zip(self.t, np_t):
                assert np.all(row == np_row)

    def test_left_not_equal(self, table_types):
        """Compare a table row to the corresponding structured array row"""
        self._setup(table_types)
        np_t = self.t.as_array()
        np_t["a"] = [0, 0, 0]
        if table_types.Table is MaskedTable:
            with pytest.raises(ValueError):
                self.t[0] == np_t[0]
        else:
            for row, np_row in zip(self.t, np_t):
                assert np.all(row != np_row)

    def test_right_equal(self, table_types):
        """Test right equal"""
        self._setup(table_types)
        np_t = self.t.as_array()
        if table_types.Table is MaskedTable:
            with pytest.raises(ValueError):
                self.t[0] == np_t[0]
        else:
            for row, np_row in zip(self.t, np_t):
                assert np.all(np_row == row)

    def test_convert_numpy_array(self, table_types):
        """
        Converts a table row or column into a NumPy array.
        
        This function converts a row or column of a table into a NumPy array and checks for consistency between the table and the array. It also raises an error if the specified dtype does not match the table's columns.
        
        Parameters:
        -----------
        table_types : object
        The type of the table (e.g., Table, MaskedTable).
        
        Returns:
        --------
        None
        
        Raises:
        -------
        ValueError
        """

        self._setup(table_types)
        d = self.t[1]

        np_data = np.array(d)
        if table_types.Table is not MaskedTable:
            assert np.all(np_data == d.as_void())
        assert np_data is not d.as_void()
        assert d.colnames == list(np_data.dtype.names)

        np_data = np.array(d, copy=False)
        if table_types.Table is not MaskedTable:
            assert np.all(np_data == d.as_void())
        assert np_data is not d.as_void()
        assert d.colnames == list(np_data.dtype.names)

        with pytest.raises(ValueError):
            np_data = np.array(d, dtype=[("c", "i8"), ("d", "i8")])

    def test_format_row(self, table_types):
        """Test formatting row"""
        self._setup(table_types)
        table = self.t
        row = table[0]
        assert repr(row).splitlines() == [
            "<{} {}{}>".format(
                row.__class__.__name__,
                "index=0",
                " masked=True" if table.masked else "",
            ),
            "  a     b  ",
            "int64 int64",
            "----- -----",
            "    1     4",
        ]
        assert str(row).splitlines() == [" a   b ", "--- ---", "  1   4"]

        assert row._repr_html_().splitlines() == [
            "<i>{} {}{}</i>".format(
                row.__class__.__name__,
                "index=0",
                " masked=True" if table.masked else "",
            ),
            f'<table id="table{id(table)}">',
            "<thead><tr><th>a</th><th>b</th></tr></thead>",
            "<thead><tr><th>int64</th><th>int64</th></tr></thead>",
            "<tr><td>1</td><td>4</td></tr>",
            "</table>",
        ]

    def test_as_void(self, table_types):
        """Test the as_void() method"""
        self._setup(table_types)
        table = self.t
        row = table[0]

        # If masked then with no masks, issue numpy/numpy#483 should come
        # into play.  Make sure as_void() code is working.
        row_void = row.as_void()
        if table.masked:
            assert isinstance(row_void, np.ma.mvoid)
        else:
            assert isinstance(row_void, np.void)
        assert row_void["a"] == 1
        assert row_void["b"] == 4

        # Confirm row is a view of table but row_void is not.
        table["a"][0] = -100
        assert row["a"] == -100
        assert row_void["a"] == 1

        # Make sure it works for a table that has masked elements
        if table.masked:
            table["a"].mask = True

            # row_void is not a view, need to re-make
            assert row_void["a"] == 1
            row_void = row.as_void()  # but row is a view
            assert row["a"] is np.ma.masked

    def test_row_and_as_void_with_objects(self, table_types):
        """Test the deprecated data property and as_void() method"""
        t = table_types.Table([[{"a": 1}, {"b": 2}]], names=("a",))
        assert t[0][0] == {"a": 1}
        assert t[0]["a"] == {"a": 1}
        assert t[0].as_void()[0] == {"a": 1}
        assert t[0].as_void()["a"] == {"a": 1}

    def test_bounds_checking(self, table_types):
        """Row gives index error upon creation for out-of-bounds index"""
        self._setup(table_types)
        for ibad in (-5, -4, 3, 4):
            with pytest.raises(IndexError):
                self.t[ibad]

    def test_create_rows_from_list(self, table_types):
        """https://github.com/astropy/astropy/issues/8976"""
        orig_tab = table_types.Table([[1, 2, 3], [4, 5, 6]], names=("a", "b"))
        new_tab = type(orig_tab)(
            rows=[row for row in orig_tab], names=orig_tab.dtype.names
        )
        assert np.all(orig_tab == new_tab)

    def test_row_keys_values(self, table_types):
        """
        Tests that the row keys and values match the column keys and values in a given table.
        
        Args:
        table_types (list): A list of table types to be tested.
        
        Summary:
        This function sets up the test environment using the `_setup` method, then iterates over the keys and values of the first row in the table (`self.t[0]`). It compares the row keys with the column keys and the row values with the first value in each column. The function uses
        """

        self._setup(table_types)
        row = self.t[0]
        for row_key, col_key in zip(row.keys(), self.t.columns.keys()):
            assert row_key == col_key

        for row_value, col in zip(row.values(), self.t.columns.values()):
            assert row_value == col[0]

    def test_row_as_mapping(self, table_types):
        """
        Tests if a row from a table can be accessed as a mapping.
        
        Args:
        table_types (list): A list of table types to be tested.
        
        Summary:
        This function sets up the test environment using the provided `table_types`, retrieves the first row from the table, and converts it into a dictionary. It then iterates over the dictionary items, asserting that accessing the row by key returns the same value. The function also demonstrates how to splat a row into a dictionary using
        """

        self._setup(table_types)
        row = self.t[0]
        row_dict = dict(row)
        for key, value in row_dict.items():
            assert row[key] == value

        def f(**kwargs):
            return kwargs

        row_splatted = f(**row)
        for key, value in row_splatted.items():
            assert row[key] == value

    def test_row_as_sequence(self, table_types):
        """
        Tests if a row from a table can be accessed both as a dictionary and as a sequence.
        
        Args:
        table_types (list): A list of table types to be tested.
        
        Summary:
        - Sets up the test environment using `_setup` method.
        - Retrieves the first row from the table.
        - Converts the row to a tuple and extracts its keys.
        - Iterates over the keys and values, asserting that accessing the row via keys returns the same values.
        -
        """

        self._setup(table_types)
        row = self.t[0]
        row_tuple = tuple(row)
        keys = tuple(row.keys())
        for key, value in zip(keys, row_tuple):
            assert row[key] == value

        def f(*args):
            return args

        row_splatted = f(*row)
        for key, value in zip(keys, row_splatted):
            assert row[key] == value


def test_row_tuple_column_slice():
    """
    Test getting and setting a row using a tuple or list of column names
    """
    t = table.QTable(
        [
            [1, 2, 3] * u.m,
            [10.0, 20.0, 30.0],
            [100.0, 200.0, 300.0],
            ["x", "y", "z"],
        ],
        names=["a", "b", "c", "d"],
    )
    # Get a row for index=1
    r1 = t[1]
    # Column slice with tuple of col names
    r1_abc = r1["a", "b", "c"]  # Row object for these cols
    r1_abc_repr = [
        "<Row index=1>",
        "   a       b       c   ",
        "   m                   ",
        "float64 float64 float64",
        "------- ------- -------",
        "    2.0    20.0   200.0",
    ]
    assert repr(r1_abc).splitlines() == r1_abc_repr

    # Column slice with list of col names
    r1_abc = r1[["a", "b", "c"]]
    assert repr(r1_abc).splitlines() == r1_abc_repr

    # Make sure setting on a tuple or slice updates parent table and row
    r1["c"] = 1000
    r1["a", "b"] = 1000 * u.cm, 100.0
    assert r1["a"] == 10 * u.m
    assert r1["b"] == 100
    assert t["a"][1] == 10 * u.m
    assert t["b"][1] == 100.0
    assert t["c"][1] == 1000

    # Same but using a list of column names instead of tuple
    r1[["a", "b"]] = 2000 * u.cm, 200.0
    assert r1["a"] == 20 * u.m
    assert r1["b"] == 200
    assert t["a"][1] == 20 * u.m
    assert t["b"][1] == 200.0

    # Set column slice of column slice
    r1_abc["a", "c"] = -1 * u.m, -10
    assert t["a"][1] == -1 * u.m
    assert t["b"][1] == 200.0
    assert t["c"][1] == -10.0

    # Bad column name
    with pytest.raises(KeyError) as err:
        t[1]["a", "not_there"]
    assert "'not_there'" in str(err.value)

    # Too many values
    with pytest.raises(ValueError) as err:
        t[1]["a", "b"] = 1 * u.m, 2, 3
    assert "right hand side must be a sequence" in str(err.value)

    # Something without a length
    with pytest.raises(ValueError) as err:
        t[1]["a", "b"] = 1
    assert "right hand side must be a sequence" in str(err.value)


def test_row_tuple_column_slice_transaction():
    """
    Test that setting a row that fails part way through does not
    change the table at all.
    """
    t = table.QTable(
        [
            [10.0, 20.0, 30.0],
            [1, 2, 3] * u.m,
        ],
        names=["a", "b"],
    )
    tc = t.copy()

    # First one succeeds but second fails.
    with pytest.raises(ValueError) as err:
        t[1]["a", "b"] = (-1, -1 * u.s)  # Bad unit
    assert "'s' (time) and 'm' (length) are not convertible" in str(err.value)
    assert t[1] == tc[1]


def test_uint_indexing():
    """
    Test that accessing a row with an unsigned integer
    works as with a signed integer.  Similarly tests
    that printing such a row works.

    This is non-trivial: adding a signed and unsigned
    integer in numpy results in a float, which is an
    invalid slice index.

    Regression test for gh-7464.
    """
    t = table.Table([[1.0, 2.0, 3.0]], names="a")
    assert t["a"][1] == 2.0
    assert t["a"][np.int_(1)] == 2.0
    assert t["a"][np.uint(1)] == 2.0
    assert t[np.uint(1)]["a"] == 2.0

    trepr = [
        "<Row index=1>",
        "   a   ",
        "float64",
        "-------",
        "    2.0",
    ]

    assert repr(t[1]).splitlines() == trepr
    assert repr(t[np.int_(1)]).splitlines() == trepr
    assert repr(t[np.uint(1)]).splitlines() == trepr
