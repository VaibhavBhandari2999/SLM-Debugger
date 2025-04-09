import pickle
from textwrap import dedent

import numpy as np
import pandas as pd
import pytest

import xarray as xr
import xarray.ufuncs as xu
from xarray import DataArray, Variable
from xarray.core.npcompat import IS_NEP18_ACTIVE
from xarray.core.pycompat import sparse_array_type

from . import assert_equal, assert_identical, requires_dask

param = pytest.param
xfail = pytest.mark.xfail

if not IS_NEP18_ACTIVE:
    pytest.skip(
        "NUMPY_EXPERIMENTAL_ARRAY_FUNCTION is not enabled", allow_module_level=True
    )

sparse = pytest.importorskip("sparse")


def assert_sparse_equal(a, b):
    """
    Asserts that two sparse arrays are equal by comparing their dense representations.
    
    Parameters
    ----------
    a : {sparse_array_type}
    The first sparse array to compare.
    b : {sparse_array_type}
    The second sparse array to compare.
    
    Raises
    ------
    AssertionError
    If the dense representations of `a` and `b` are not equal.
    """

    assert isinstance(a, sparse_array_type)
    assert isinstance(b, sparse_array_type)
    np.testing.assert_equal(a.todense(), b.todense())


def make_ndarray(shape):
    return np.arange(np.prod(shape)).reshape(shape)


def make_sparray(shape):
    return sparse.random(shape, density=0.1, random_state=0)


def make_xrvar(dim_lengths):
    """
    Create an xarray Variable from dimension lengths.
    
    Args:
    dim_lengths (dict): A dictionary where keys represent dimension names
    and values represent the corresponding length of each dimension.
    
    Returns:
    xr.Variable: An xarray Variable with dimensions based on the input
    dictionary and data stored as a sparse array.
    
    Notes:
    - The function utilizes `make_sparray` to create the underlying sparse
    array data structure.
    - The returned variable has dimensions defined by the keys
    """

    return xr.Variable(
        tuple(dim_lengths.keys()), make_sparray(shape=tuple(dim_lengths.values()))
    )


def make_xrarray(dim_lengths, coords=None, name="test"):
    """
    Create an xarray DataArray with specified dimensions and coordinates.
    
    Parameters
    ----------
    dim_lengths : dict
    A dictionary specifying the length of each dimension.
    coords : dict, optional
    A dictionary specifying the coordinates for each dimension (default is None).
    name : str, optional
    The name of the DataArray (default is "test").
    
    Returns
    -------
    xr.DataArray
    An xarray DataArray with the specified dimensions, coordinates, and name.
    """

    if coords is None:
        coords = {d: np.arange(n) for d, n in dim_lengths.items()}
    return xr.DataArray(
        make_sparray(shape=tuple(dim_lengths.values())),
        dims=tuple(coords.keys()),
        coords=coords,
        name=name,
    )


class do:
    def __init__(self, meth, *args, **kwargs):
        """
        Initialize a new instance of the class.
        
        Args:
        meth (function): The method to be called.
        args (tuple): Positional arguments to be passed to the method.
        kwargs (dict): Keyword arguments to be passed to the method.
        
        Attributes:
        meth (function): The method to be called.
        args (tuple): Positional arguments to be passed to the method.
        kwargs (dict): Keyword arguments to be passed to the method.
        """

        self.meth = meth
        self.args = args
        self.kwargs = kwargs

    def __call__(self, obj):
        """
        Call the specified method of the given object with the provided arguments and keyword arguments.
        
        Args:
        obj (object): The object whose method is to be called.
        
        Keyword Args:
        meth (str): The name of the method to call on the object.
        args (tuple): Positional arguments to pass to the method.
        func (str or callable): The function to use for aggregation, if applicable.
        
        Returns:
        The result of calling the specified method on the object with the
        """


        # cannot pass np.sum when using pytest-xdist
        kwargs = self.kwargs.copy()
        if "func" in self.kwargs:
            kwargs["func"] = getattr(np, kwargs["func"])

        return getattr(obj, self.meth)(*self.args, **kwargs)

    def __repr__(self):
        return f"obj.{self.meth}(*{self.args}, **{self.kwargs})"


@pytest.mark.parametrize(
    "prop",
    [
        "chunks",
        "data",
        "dims",
        "dtype",
        "encoding",
        "imag",
        "nbytes",
        "ndim",
        param("values", marks=xfail(reason="Coercion to dense")),
    ],
)
def test_variable_property(prop):
    var = make_xrvar({"x": 10, "y": 5})
    getattr(var, prop)


@pytest.mark.parametrize(
    "func,sparse_output",
    [
        (do("all"), False),
        (do("any"), False),
        (do("astype", dtype=int), True),
        (do("clip", min=0, max=1), True),
        (do("coarsen", windows={"x": 2}, func="sum"), True),
        (do("compute"), True),
        (do("conj"), True),
        (do("copy"), True),
        (do("count"), False),
        (do("get_axis_num", dim="x"), False),
        (do("isel", x=slice(2, 4)), True),
        (do("isnull"), True),
        (do("load"), True),
        (do("mean"), False),
        (do("notnull"), True),
        (do("roll"), True),
        (do("round"), True),
        (do("set_dims", dims=("x", "y", "z")), True),
        (do("stack", dimensions={"flat": ("x", "y")}), True),
        (do("to_base_variable"), True),
        (do("transpose"), True),
        (do("unstack", dimensions={"x": {"x1": 5, "x2": 2}}), True),
        (do("broadcast_equals", make_xrvar({"x": 10, "y": 5})), False),
        (do("equals", make_xrvar({"x": 10, "y": 5})), False),
        (do("identical", make_xrvar({"x": 10, "y": 5})), False),
        param(
            do("argmax"),
            True,
            marks=xfail(reason="Missing implementation for np.argmin"),
        ),
        param(
            do("argmin"),
            True,
            marks=xfail(reason="Missing implementation for np.argmax"),
        ),
        param(
            do("argsort"),
            True,
            marks=xfail(reason="'COO' object has no attribute 'argsort'"),
        ),
        param(
            do(
                "concat",
                variables=[
                    make_xrvar({"x": 10, "y": 5}),
                    make_xrvar({"x": 10, "y": 5}),
                ],
            ),
            True,
            marks=xfail(reason="Coercion to dense"),
        ),
        param(
            do("conjugate"),
            True,
            marks=xfail(reason="'COO' object has no attribute 'conjugate'"),
        ),
        param(
            do("cumprod"),
            True,
            marks=xfail(reason="Missing implementation for np.nancumprod"),
        ),
        param(
            do("cumsum"),
            True,
            marks=xfail(reason="Missing implementation for np.nancumsum"),
        ),
        (do("fillna", 0), True),
        param(
            do("item", (1, 1)),
            False,
            marks=xfail(reason="'COO' object has no attribute 'item'"),
        ),
        param(
            do("median"),
            False,
            marks=xfail(reason="Missing implementation for np.nanmedian"),
        ),
        param(do("max"), False),
        param(do("min"), False),
        param(
            do("no_conflicts", other=make_xrvar({"x": 10, "y": 5})),
            True,
            marks=xfail(reason="mixed sparse-dense operation"),
        ),
        param(
            do("pad", mode="constant", pad_widths={"x": (1, 1)}, fill_value=5),
            True,
            marks=xfail(reason="Missing implementation for np.pad"),
        ),
        (do("prod"), False),
        param(
            do("quantile", q=0.5),
            True,
            marks=xfail(reason="Missing implementation for np.nanpercentile"),
        ),
        param(
            do("rank", dim="x"),
            False,
            marks=xfail(reason="Only implemented for NumPy arrays (via bottleneck)"),
        ),
        param(
            do("reduce", func="sum", dim="x"),
            True,
            marks=xfail(reason="Coercion to dense"),
        ),
        param(
            do("rolling_window", dim="x", window=2, window_dim="x_win"),
            True,
            marks=xfail(reason="Missing implementation for np.pad"),
        ),
        param(
            do("shift", x=2), True, marks=xfail(reason="mixed sparse-dense operation")
        ),
        param(
            do("std"), False, marks=xfail(reason="Missing implementation for np.nanstd")
        ),
        (do("sum"), False),
        param(
            do("var"), False, marks=xfail(reason="Missing implementation for np.nanvar")
        ),
        param(do("to_dict"), False, marks=xfail(reason="Coercion to dense")),
        (do("where", cond=make_xrvar({"x": 10, "y": 5}) > 0.5), True),
    ],
    ids=repr,
)
def test_variable_method(func, sparse_output):
    """
    Tests a function's behavior with both sparse and dense input variables.
    
    This function evaluates a given function `func` on two types of input variables:
    a sparse variable (`xr.Variable`) and its dense equivalent (`xr.Variable` converted from sparse).
    The function checks whether the output is consistent between the sparse and dense inputs,
    depending on the value of `sparse_output`.
    
    Parameters:
    func (callable): The function to be tested.
    sparse_output (bool): A
    """

    var_s = make_xrvar({"x": 10, "y": 5})
    var_d = xr.Variable(var_s.dims, var_s.data.todense())
    ret_s = func(var_s)
    ret_d = func(var_d)

    if sparse_output:
        assert isinstance(ret_s.data, sparse.SparseArray)
        assert np.allclose(ret_s.data.todense(), ret_d.data, equal_nan=True)
    else:
        assert np.allclose(ret_s, ret_d, equal_nan=True)


@pytest.mark.parametrize(
    "func,sparse_output",
    [
        (do("squeeze"), True),
        param(do("to_index"), False, marks=xfail(reason="Coercion to dense")),
        param(do("to_index_variable"), False, marks=xfail(reason="Coercion to dense")),
        param(
            do("searchsorted", 0.5),
            True,
            marks=xfail(reason="'COO' object has no attribute 'searchsorted'"),
        ),
    ],
)
def test_1d_variable_method(func, sparse_output):
    """
    Tests a function's behavior with both sparse and dense 1D xarray variables.
    
    This function evaluates a given function `func` on both sparse and dense
    1D xarray variables. It creates a sparse xarray variable `var_s` with
    dimension 'x' and size 10, and a corresponding dense xarray variable `var_d`.
    The function `func` is applied to both variables, and the results are compared.
    
    Parameters:
    func (
    """

    var_s = make_xrvar({"x": 10})
    var_d = xr.Variable(var_s.dims, var_s.data.todense())
    ret_s = func(var_s)
    ret_d = func(var_d)

    if sparse_output:
        assert isinstance(ret_s.data, sparse.SparseArray)
        assert np.allclose(ret_s.data.todense(), ret_d.data)
    else:
        assert np.allclose(ret_s, ret_d)


class TestSparseVariable:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.data = sparse.random((4, 6), random_state=0, density=0.5)
        self.var = xr.Variable(("x", "y"), self.data)

    def test_unary_op(self):
        """
        Tests unary operations on sparse variables.
        
        This method verifies that unary operations such as negation (-), absolute value (abs),
        and rounding (round) are correctly applied to both the variable and its underlying data.
        The expected behavior is that these operations are performed element-wise on the data,
        and the result is then assigned back to the variable's data.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the results of the unary operations do not
        """

        assert_sparse_equal(-self.var.data, -self.data)
        assert_sparse_equal(abs(self.var).data, abs(self.data))
        assert_sparse_equal(self.var.round().data, self.data.round())

    @pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
    def test_univariate_ufunc(self):
        assert_sparse_equal(np.sin(self.data), xu.sin(self.var).data)

    @pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
    def test_bivariate_ufunc(self):
        assert_sparse_equal(np.maximum(self.data, 0), xu.maximum(self.var, 0).data)
        assert_sparse_equal(np.maximum(self.data, 0), xu.maximum(0, self.var).data)

    def test_repr(self):
        """
        \
        <xarray.Variable (x: 4, y: 6)>
        <COO: shape=(4, 6), dtype=float64, nnz=12, fill_value=0.0>
        """

        expected = dedent(
            """\
            <xarray.Variable (x: 4, y: 6)>
            <COO: shape=(4, 6), dtype=float64, nnz=12, fill_value=0.0>"""
        )
        assert expected == repr(self.var)

    def test_pickle(self):
        """
        Tests the pickling functionality of the variable object.
        
        This method serializes and deserializes the variable object using the `pickle` module,
        ensuring that the data remains consistent before and after the process.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `pickle.dumps`: Serializes the variable object.
        - `pickle.loads`: Deserializes the serialized variable object.
        - `assert_sparse_equal`: Compares the original and deserialized sparse data
        """

        v1 = self.var
        v2 = pickle.loads(pickle.dumps(v1))
        assert_sparse_equal(v1.data, v2.data)

    def test_missing_values(self):
        """
        Fills missing values (NaNs) in the variable with a specified value (2) and checks the count of non-missing values.
        
        Args:
        self: The instance of the class containing the variable.
        
        Variables:
        a (numpy.ndarray): Input array containing NaN values.
        s (sparse.COO): Sparse COO representation of the input array.
        var_s (Variable): Variable object initialized with the sparse COO array.
        
        Returns:
        None
        
        Notes:
        """

        a = np.array([0, 1, np.nan, 3])
        s = sparse.COO.from_numpy(a)
        var_s = Variable("x", s)
        assert np.all(var_s.fillna(2).data.todense() == np.arange(4))
        assert np.all(var_s.count() == 3)


@pytest.mark.parametrize(
    "prop",
    [
        "attrs",
        "chunks",
        "coords",
        "data",
        "dims",
        "dtype",
        "encoding",
        "imag",
        "indexes",
        "loc",
        "name",
        "nbytes",
        "ndim",
        "plot",
        "real",
        "shape",
        "size",
        "sizes",
        "str",
        "variable",
    ],
)
def test_dataarray_property(prop):
    arr = make_xrarray({"x": 10, "y": 5})
    getattr(arr, prop)


@pytest.mark.parametrize(
    "func,sparse_output",
    [
        (do("all"), False),
        (do("any"), False),
        (do("assign_attrs", {"foo": "bar"}), True),
        (do("assign_coords", x=make_xrarray({"x": 10}).x + 1), True),
        (do("astype", int), True),
        (do("clip", min=0, max=1), True),
        (do("compute"), True),
        (do("conj"), True),
        (do("copy"), True),
        (do("count"), False),
        (do("diff", "x"), True),
        (do("drop_vars", "x"), True),
        (do("expand_dims", {"z": 2}, axis=2), True),
        (do("get_axis_num", "x"), False),
        (do("get_index", "x"), False),
        (do("identical", make_xrarray({"x": 5, "y": 5})), False),
        (do("integrate", "x"), True),
        (do("isel", {"x": slice(0, 3), "y": slice(2, 4)}), True),
        (do("isnull"), True),
        (do("load"), True),
        (do("mean"), False),
        (do("persist"), True),
        (do("reindex", {"x": [1, 2, 3]}), True),
        (do("rename", "foo"), True),
        (do("reorder_levels"), True),
        (do("reset_coords", drop=True), True),
        (do("reset_index", "x"), True),
        (do("round"), True),
        (do("sel", x=[0, 1, 2]), True),
        (do("shift"), True),
        (do("sortby", "x", ascending=False), True),
        (do("stack", z=["x", "y"]), True),
        (do("transpose"), True),
        # TODO
        # set_index
        # swap_dims
        (do("broadcast_equals", make_xrvar({"x": 10, "y": 5})), False),
        (do("equals", make_xrvar({"x": 10, "y": 5})), False),
        param(
            do("argmax"),
            True,
            marks=xfail(reason="Missing implementation for np.argmax"),
        ),
        param(
            do("argmin"),
            True,
            marks=xfail(reason="Missing implementation for np.argmin"),
        ),
        param(
            do("argsort"),
            True,
            marks=xfail(reason="'COO' object has no attribute 'argsort'"),
        ),
        param(
            do("bfill", dim="x"),
            False,
            marks=xfail(reason="Missing implementation for np.flip"),
        ),
        (do("combine_first", make_xrarray({"x": 10, "y": 5})), True),
        param(
            do("conjugate"),
            False,
            marks=xfail(reason="'COO' object has no attribute 'conjugate'"),
        ),
        param(
            do("cumprod"),
            True,
            marks=xfail(reason="Missing implementation for np.nancumprod"),
        ),
        param(
            do("cumsum"),
            True,
            marks=xfail(reason="Missing implementation for np.nancumsum"),
        ),
        param(
            do("differentiate", "x"),
            False,
            marks=xfail(reason="Missing implementation for np.gradient"),
        ),
        param(
            do("dot", make_xrarray({"x": 10, "y": 5})),
            True,
            marks=xfail(reason="Missing implementation for np.einsum"),
        ),
        param(do("dropna", "x"), False, marks=xfail(reason="Coercion to dense")),
        param(do("ffill", "x"), False, marks=xfail(reason="Coercion to dense")),
        (do("fillna", 0), True),
        param(
            do("interp", coords={"x": np.arange(10) + 0.5}),
            True,
            marks=xfail(reason="Coercion to dense"),
        ),
        param(
            do(
                "interp_like",
                make_xrarray(
                    {"x": 10, "y": 5},
                    coords={"x": np.arange(10) + 0.5, "y": np.arange(5) + 0.5},
                ),
            ),
            True,
            marks=xfail(reason="Indexing COO with more than one iterable index"),
        ),
        param(do("interpolate_na", "x"), True, marks=xfail(reason="Coercion to dense")),
        param(
            do("isin", [1, 2, 3]),
            False,
            marks=xfail(reason="Missing implementation for np.isin"),
        ),
        param(
            do("item", (1, 1)),
            False,
            marks=xfail(reason="'COO' object has no attribute 'item'"),
        ),
        param(do("max"), False),
        param(do("min"), False),
        param(
            do("median"),
            False,
            marks=xfail(reason="Missing implementation for np.nanmedian"),
        ),
        (do("notnull"), True),
        (do("pipe", func="sum", axis=1), True),
        (do("prod"), False),
        param(
            do("quantile", q=0.5),
            False,
            marks=xfail(reason="Missing implementation for np.nanpercentile"),
        ),
        param(
            do("rank", "x"),
            False,
            marks=xfail(reason="Only implemented for NumPy arrays (via bottleneck)"),
        ),
        param(
            do("reduce", func="sum", dim="x"),
            False,
            marks=xfail(reason="Coercion to dense"),
        ),
        param(
            do(
                "reindex_like",
                make_xrarray(
                    {"x": 10, "y": 5},
                    coords={"x": np.arange(10) + 0.5, "y": np.arange(5) + 0.5},
                ),
            ),
            True,
            marks=xfail(reason="Indexing COO with more than one iterable index"),
        ),
        (do("roll", x=2, roll_coords=True), True),
        param(
            do("sel", x=[0, 1, 2], y=[2, 3]),
            True,
            marks=xfail(reason="Indexing COO with more than one iterable index"),
        ),
        param(
            do("std"), False, marks=xfail(reason="Missing implementation for np.nanstd")
        ),
        (do("sum"), False),
        param(
            do("var"), False, marks=xfail(reason="Missing implementation for np.nanvar")
        ),
        param(
            do("where", make_xrarray({"x": 10, "y": 5}) > 0.5),
            False,
            marks=xfail(reason="Conversion of dense to sparse when using sparse mask"),
        ),
    ],
    ids=repr,
)
def test_dataarray_method(func, sparse_output):
    """
    Tests a method applied to both sparse and dense DataArray objects.
    
    This function evaluates a given method on both a sparse and a dense
    `xarray.DataArray` object. It ensures that the method produces consistent
    results regardless of whether the input is sparse or dense.
    
    Parameters:
    -----------
    func : callable
    The function/method to be tested, which should accept an `xarray.DataArray`
    as its primary argument.
    sparse_output : bool
    A
    """

    arr_s = make_xrarray(
        {"x": 10, "y": 5}, coords={"x": np.arange(10), "y": np.arange(5)}
    )
    arr_d = xr.DataArray(arr_s.data.todense(), coords=arr_s.coords, dims=arr_s.dims)
    ret_s = func(arr_s)
    ret_d = func(arr_d)

    if sparse_output:
        assert isinstance(ret_s.data, sparse.SparseArray)
        assert np.allclose(ret_s.data.todense(), ret_d.data, equal_nan=True)
    else:
        assert np.allclose(ret_s, ret_d, equal_nan=True)


@pytest.mark.parametrize(
    "func,sparse_output",
    [
        (do("squeeze"), True),
        param(
            do("searchsorted", [1, 2, 3]),
            False,
            marks=xfail(reason="'COO' object has no attribute 'searchsorted'"),
        ),
    ],
)
def test_datarray_1d_method(func, sparse_output):
    """
    Test a method on a 1-dimensional xarray DataArray with sparse and dense representations.
    
    This function compares the results of applying a given method to both a sparse
    and dense representation of an xarray DataArray. The input array is created using
    `make_xrarray` with a single dimension 'x' ranging from 0 to 9. The method is
    expected to modify the data within the array.
    
    Parameters:
    func (callable): The method to be
    """

    arr_s = make_xrarray({"x": 10}, coords={"x": np.arange(10)})
    arr_d = xr.DataArray(arr_s.data.todense(), coords=arr_s.coords, dims=arr_s.dims)
    ret_s = func(arr_s)
    ret_d = func(arr_d)

    if sparse_output:
        assert isinstance(ret_s.data, sparse.SparseArray)
        assert np.allclose(ret_s.data.todense(), ret_d.data, equal_nan=True)
    else:
        assert np.allclose(ret_s, ret_d, equal_nan=True)


class TestSparseDataArrayAndDataset:
    @pytest.fixture(autouse=True)
    def setUp(self):
        """
        Sets up test data for sparse and dense DataArray and Dataset objects.
        
        This method initializes two sets of test data: one using sparse matrices and another using dense matrices. Both sets include DataArray objects with specific coordinates and dimensions.
        
        Parameters:
        None
        
        Returns:
        None
        
        Variables:
        - sp_ar (scipy.sparse.csr_matrix): A randomly generated sparse matrix with shape (4, 6) and a density of 0.5.
        - sp_xr
        """

        self.sp_ar = sparse.random((4, 6), random_state=0, density=0.5)
        self.sp_xr = xr.DataArray(
            self.sp_ar, coords={"x": range(4)}, dims=("x", "y"), name="foo"
        )
        self.ds_ar = self.sp_ar.todense()
        self.ds_xr = xr.DataArray(
            self.ds_ar, coords={"x": range(4)}, dims=("x", "y"), name="foo"
        )

    def test_to_dataset_roundtrip(self):
        x = self.sp_xr
        assert_equal(x, x.to_dataset("x").to_array("x"))

    def test_align(self):
        """
        Aligns two xarray DataArrays with sparse coordinates along the 'x' dimension.
        
        This function takes two xarray DataArrays `a1` and `b1`, both containing
        sparse COO (Coordinate List) arrays with coordinates along the 'x'
        dimension. It aligns these arrays by intersecting their coordinates,
        resulting in new DataArrays `a2` and `b2` that share the same coordinate
        values. The alignment is performed using the 'inner
        """

        a1 = xr.DataArray(
            sparse.COO.from_numpy(np.arange(4)),
            dims=["x"],
            coords={"x": ["a", "b", "c", "d"]},
        )
        b1 = xr.DataArray(
            sparse.COO.from_numpy(np.arange(4)),
            dims=["x"],
            coords={"x": ["a", "b", "d", "e"]},
        )
        a2, b2 = xr.align(a1, b1, join="inner")
        assert isinstance(a2.data, sparse.SparseArray)
        assert isinstance(b2.data, sparse.SparseArray)
        assert np.all(a2.coords["x"].data == ["a", "b", "d"])
        assert np.all(b2.coords["x"].data == ["a", "b", "d"])

    @pytest.mark.xfail(
        reason="COO objects currently do not accept more than one "
        "iterable index at a time"
    )
    def test_align_2d(self):
        """
        Aligns two 2D xarray DataArrays along their shared coordinates.
        
        This function takes two 2D xarray DataArrays, `A1` and `A2`, with different coordinate ranges and aligns them along their shared coordinates using the `xr.align` method with 'inner' join. The resulting aligned DataArrays, `B1` and `B2`, have the same coordinate ranges, which are adjusted to match the overlapping region of the original arrays.
        
        Parameters:
        """

        A1 = xr.DataArray(
            self.sp_ar,
            dims=["x", "y"],
            coords={
                "x": np.arange(self.sp_ar.shape[0]),
                "y": np.arange(self.sp_ar.shape[1]),
            },
        )

        A2 = xr.DataArray(
            self.sp_ar,
            dims=["x", "y"],
            coords={
                "x": np.arange(1, self.sp_ar.shape[0] + 1),
                "y": np.arange(1, self.sp_ar.shape[1] + 1),
            },
        )

        B1, B2 = xr.align(A1, A2, join="inner")
        assert np.all(B1.coords["x"] == np.arange(1, self.sp_ar.shape[0]))
        assert np.all(B1.coords["y"] == np.arange(1, self.sp_ar.shape[0]))
        assert np.all(B1.coords["x"] == B2.coords["x"])
        assert np.all(B1.coords["y"] == B2.coords["y"])

    def test_align_outer(self):
        """
        Aligns two xarray DataArrays along their 'x' dimension using an outer join.
        
        This function takes two xarray DataArrays `a1` and `b1`, both with a single
        dimension 'x' and coordinates representing labels ['a', 'b', 'c', 'd'] and
        ['a', 'b', 'd', 'e'], respectively. It aligns these arrays using an outer
        join, resulting in new DataArrays `a2`
        """

        a1 = xr.DataArray(
            sparse.COO.from_numpy(np.arange(4)),
            dims=["x"],
            coords={"x": ["a", "b", "c", "d"]},
        )
        b1 = xr.DataArray(
            sparse.COO.from_numpy(np.arange(4)),
            dims=["x"],
            coords={"x": ["a", "b", "d", "e"]},
        )
        a2, b2 = xr.align(a1, b1, join="outer")
        assert isinstance(a2.data, sparse.SparseArray)
        assert isinstance(b2.data, sparse.SparseArray)
        assert np.all(a2.coords["x"].data == ["a", "b", "c", "d", "e"])
        assert np.all(b2.coords["x"].data == ["a", "b", "c", "d", "e"])

    def test_concat(self):
        """
        Concatenates multiple datasets or data arrays along a specified dimension.
        
        This function takes multiple datasets or data arrays and concatenates them
        along a specified dimension ('x' or 'y'). The resulting dataset or array
        is then compared against expected sparse array concatenations using the
        `assert_sparse_equal` function.
        
        Parameters:
        None (The function uses predefined datasets and arrays)
        
        Returns:
        None (The function asserts equality between the concatenated results and
        expected values)
        """

        ds1 = xr.Dataset(data_vars={"d": self.sp_xr})
        ds2 = xr.Dataset(data_vars={"d": self.sp_xr})
        ds3 = xr.Dataset(data_vars={"d": self.sp_xr})
        out = xr.concat([ds1, ds2, ds3], dim="x")
        assert_sparse_equal(
            out["d"].data,
            sparse.concatenate([self.sp_ar, self.sp_ar, self.sp_ar], axis=0),
        )

        out = xr.concat([self.sp_xr, self.sp_xr, self.sp_xr], dim="y")
        assert_sparse_equal(
            out.data, sparse.concatenate([self.sp_ar, self.sp_ar, self.sp_ar], axis=1)
        )

    def test_stack(self):
        """
        Stacks multiple dimensions of an xarray dataset into a single dimension 'z', then reshapes and reassigns the data accordingly. The function takes an xarray dataset `arr` with dimensions 'w', 'x', and 'y'. It stacks 'x' and 'y' into 'z', creating a new MultiIndex. The reshaped data is then assigned to a new DataArray with dimensions 'w' and 'z'. Finally, the function checks if unstacking the Data
        """

        arr = make_xrarray({"w": 2, "x": 3, "y": 4})
        stacked = arr.stack(z=("x", "y"))

        z = pd.MultiIndex.from_product([np.arange(3), np.arange(4)], names=["x", "y"])

        expected = xr.DataArray(
            arr.data.reshape((2, -1)), {"w": [0, 1], "z": z}, dims=["w", "z"]
        )

        assert_equal(expected, stacked)

        roundtripped = stacked.unstack()
        assert_identical(arr, roundtripped)

    @pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
    def test_ufuncs(self):
        x = self.sp_xr
        assert_equal(np.sin(x), xu.sin(x))

    def test_dataarray_repr(self):
        """
        \
        <xarray.DataArray (x: 4)>
        <COO: shape=(4,), dtype=float64, nnz=4, fill_value=0.0>
        Coordinates:
        y        (x) int64 <COO: nnz=3, fill_value=0>
        Dimensions without coordinates: x
        """

        a = xr.DataArray(
            sparse.COO.from_numpy(np.ones(4)),
            dims=["x"],
            coords={"y": ("x", sparse.COO.from_numpy(np.arange(4, dtype="i8")))},
        )
        expected = dedent(
            """\
            <xarray.DataArray (x: 4)>
            <COO: shape=(4,), dtype=float64, nnz=4, fill_value=0.0>
            Coordinates:
                y        (x) int64 <COO: nnz=3, fill_value=0>
            Dimensions without coordinates: x"""
        )
        assert expected == repr(a)

    def test_dataset_repr(self):
        """
        \
        <xarray.Dataset>
        Dimensions:  (x: 4)
        Coordinates:
        y        (x) int64 <COO: nnz=3, fill_value=0>
        Dimensions without coordinates: x
        Data variables:
        a        (x) float64 <COO: nnz=4, fill_value=0.0>
        """

        ds = xr.Dataset(
            data_vars={"a": ("x", sparse.COO.from_numpy(np.ones(4)))},
            coords={"y": ("x", sparse.COO.from_numpy(np.arange(4, dtype="i8")))},
        )
        expected = dedent(
            """\
            <xarray.Dataset>
            Dimensions:  (x: 4)
            Coordinates:
                y        (x) int64 <COO: nnz=3, fill_value=0>
            Dimensions without coordinates: x
            Data variables:
                a        (x) float64 <COO: nnz=4, fill_value=0.0>"""
        )
        assert expected == repr(ds)

    def test_sparse_dask_dataset_repr(self):
        """
        \
        <xarray.Dataset>
        Dimensions:  (x: 4)
        Dimensions without coordinates: x
        Data variables:
        a        (x) float64 dask.array<chunksize=(4,), meta=sparse.COO>
        """

        pytest.importorskip("dask", minversion="2.0")
        ds = xr.Dataset(
            data_vars={"a": ("x", sparse.COO.from_numpy(np.ones(4)))}
        ).chunk()
        expected = dedent(
            """\
            <xarray.Dataset>
            Dimensions:  (x: 4)
            Dimensions without coordinates: x
            Data variables:
                a        (x) float64 dask.array<chunksize=(4,), meta=sparse.COO>"""
        )
        assert expected == repr(ds)

    def test_dataarray_pickle(self):
        """
        Tests the pickling of a DataArray with sparse coordinates.
        
        This function creates a DataArray `a1` with sparse coordinates and then
        pickles and unpickles it to obtain `a2`. The function asserts that the
        original DataArray `a1` is identical to the unpickled DataArray `a2`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Keywords and Functions:
        - `xr.DataArray`: Creates a DataArray with specified
        """

        a1 = xr.DataArray(
            sparse.COO.from_numpy(np.ones(4)),
            dims=["x"],
            coords={"y": ("x", sparse.COO.from_numpy(np.arange(4)))},
        )
        a2 = pickle.loads(pickle.dumps(a1))
        assert_identical(a1, a2)

    def test_dataset_pickle(self):
        """
        Tests the pickling and unpickling of an xarray dataset containing sparse COO arrays.
        
        This function creates an xarray dataset with a single variable 'a' and coordinate 'y', both using sparse COO arrays. It then pickles and unpickles the dataset, and asserts that the original and reconstructed datasets are identical.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `xr.Dataset`: Creates an xarray dataset.
        - `sparse
        """

        ds1 = xr.Dataset(
            data_vars={"a": ("x", sparse.COO.from_numpy(np.ones(4)))},
            coords={"y": ("x", sparse.COO.from_numpy(np.arange(4)))},
        )
        ds2 = pickle.loads(pickle.dumps(ds1))
        assert_identical(ds1, ds2)

    def test_coarsen(self):
        """
        Coarsens the input datasets along the 'x' dimension by a factor of 2 using the 'trim' boundary condition and compares the results.
        
        Summary:
        - Input: `a1` (xarray.Dataset), `a2` (xarray.Dataset)
        - Coarsening: `coarsen(x=2, boundary="trim")`
        - Aggregation: `.mean()`
        - Output: `m1` (xarray.Dataset), `m2`
        """

        a1 = self.ds_xr
        a2 = self.sp_xr
        m1 = a1.coarsen(x=2, boundary="trim").mean()
        m2 = a2.coarsen(x=2, boundary="trim").mean()

        assert isinstance(m2.data, sparse.SparseArray)
        assert np.allclose(m1.data, m2.data.todense())

    @pytest.mark.xfail(reason="No implementation of np.pad")
    def test_rolling(self):
        """
        Tests rolling mean computation on x-axis for both xarray datasets.
        
        This function computes the rolling mean along the x-axis for two given
        xarray datasets (`a1` and `a2`). It then compares the results to ensure
        they are consistent, taking into account the sparsity of one of the datasets.
        
        Parameters:
        None
        
        Returns:
        None
        
        Methods/Functions Used:
        - `rolling(x=2, center=True)`: Computes the rolling window
        """

        a1 = self.ds_xr
        a2 = self.sp_xr
        m1 = a1.rolling(x=2, center=True).mean()
        m2 = a2.rolling(x=2, center=True).mean()

        assert isinstance(m2.data, sparse.SparseArray)
        assert np.allclose(m1.data, m2.data.todense())

    @pytest.mark.xfail(reason="Coercion to dense")
    def test_rolling_exp(self):
        """
        Tests rolling exponential window mean on xarray datasets.
        
        This function compares the results of applying a rolling exponential window
        mean with a center=True parameter on two different datasets: one using an
        xarray dataset (`a1`) and another using a sparse xarray dataset (`a2`).
        
        Parameters:
        None
        
        Returns:
        None
        
        Summary:
        - Applies `rolling_exp` with `x=2` and `center=True` to both `a1` and
        """

        a1 = self.ds_xr
        a2 = self.sp_xr
        m1 = a1.rolling_exp(x=2, center=True).mean()
        m2 = a2.rolling_exp(x=2, center=True).mean()

        assert isinstance(m2.data, sparse.SparseArray)
        assert np.allclose(m1.data, m2.data.todense())

    @pytest.mark.xfail(reason="No implementation of np.einsum")
    def test_dot(self):
        """
        Tests the dot product between an array and its first element using both `xp_xr` and `sp_ar`.
        
        This function computes the dot product of the array `self.xp_xr` with its first element and compares it to the dot product of the array `self.sp_ar` with its first element. The results are then compared using `assert_equal`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Notes:
        - `xp_xr`: Array used for
        """

        a1 = self.xp_xr.dot(self.xp_xr[0])
        a2 = self.sp_ar.dot(self.sp_ar[0])
        assert_equal(a1, a2)

    @pytest.mark.xfail(reason="Groupby reductions produce dense output")
    def test_groupby(self):
        """
        Groups the data by the 'x' dimension and computes the mean for each group. Compares the results from xarray (m1) and sparse (m2) datasets, ensuring that the output from the sparse dataset is a `SparseArray` and that the mean values match those computed by xarray.
        
        Parameters:
        None
        
        Returns:
        None
        
        Important Functions:
        - `groupby`: Groups the data by the 'x' dimension.
        - `mean`: Computes
        """

        x1 = self.ds_xr
        x2 = self.sp_xr
        m1 = x1.groupby("x").mean(...)
        m2 = x2.groupby("x").mean(...)
        assert isinstance(m2.data, sparse.SparseArray)
        assert np.allclose(m1.data, m2.data.todense())

    @pytest.mark.xfail(reason="Groupby reductions produce dense output")
    def test_groupby_first(self):
        """
        Groups the data along the 'ab' coordinate and returns the first element of each group. The `groupby` method is used to group the data based on the 'ab' coordinate, and the `first` method is called to select the first element from each group. This operation can be performed with or without skipping NaN values, controlled by the `skipna` parameter.
        
        Parameters:
        -----------
        skipna : bool, optional
        If True (default), NaN values are skipped
        """

        x = self.sp_xr.copy()
        x.coords["ab"] = ("x", ["a", "a", "b", "b"])
        x.groupby("ab").first()
        x.groupby("ab").first(skipna=False)

    @pytest.mark.xfail(reason="Groupby reductions produce dense output")
    def test_groupby_bins(self):
        """
        Groups the data by specified bins and calculates the sum.
        
        This function groups the datasets `x1` and `x2` based on the "x" coordinate using predefined bins and then computes the sum within each bin. The resulting objects are compared to ensure consistency between dense and sparse representations.
        
        Parameters:
        None (the function uses instance variables `ds_xr` and `sp_xr`)
        
        Returns:
        None (the function asserts equality of the results)
        
        Keywords and
        """

        x1 = self.ds_xr
        x2 = self.sp_xr
        m1 = x1.groupby_bins("x", bins=[0, 3, 7, 10]).sum(...)
        m2 = x2.groupby_bins("x", bins=[0, 3, 7, 10]).sum(...)
        assert isinstance(m2.data, sparse.SparseArray)
        assert np.allclose(m1.data, m2.data.todense())

    @pytest.mark.xfail(reason="Resample produces dense output")
    def test_resample(self):
        """
        Resamples two DataArrays, one with dense data and one with sparse data, using a quarterly frequency for December. The function compares the resampled results and asserts that the sparse array's dense representation matches the dense array's result.
        
        Parameters:
        None
        
        Returns:
        None
        
        Important Functions:
        - `xr.DataArray`: Creates DataArray objects for the input time series.
        - `pd.date_range`: Generates date ranges for the time dimension.
        - `sparse.COO
        """

        t1 = xr.DataArray(
            np.linspace(0, 11, num=12),
            coords=[
                pd.date_range("15/12/1999", periods=12, freq=pd.DateOffset(months=1))
            ],
            dims="time",
        )
        t2 = t1.copy()
        t2.data = sparse.COO(t2.data)
        m1 = t1.resample(time="QS-DEC").mean()
        m2 = t2.resample(time="QS-DEC").mean()
        assert isinstance(m2.data, sparse.SparseArray)
        assert np.allclose(m1.data, m2.data.todense())

    @pytest.mark.xfail
    def test_reindex(self):
        """
        Reindexes the datasets `x1` and `x2` using specified keyword arguments. The function iterates over a list of keyword argument dictionaries, reindexing both datasets with each set of arguments. It then compares the reindexed datasets using `np.allclose` with `equal_nan=True`.
        
        Parameters:
        None (the parameters are derived from instance attributes `ds_xr` and `sp_xr`).
        
        Returns:
        None (the function asserts equality of reindexed datasets).
        """

        x1 = self.ds_xr
        x2 = self.sp_xr
        for kwargs in [
            {"x": [2, 3, 4]},
            {"x": [1, 100, 2, 101, 3]},
            {"x": [2.5, 3, 3.5], "y": [2, 2.5, 3]},
        ]:
            m1 = x1.reindex(**kwargs)
            m2 = x2.reindex(**kwargs)
            assert np.allclose(m1, m2, equal_nan=True)

    @pytest.mark.xfail
    def test_merge(self):
        """
        Merge multiple datasets or data arrays along a new variable dimension and convert the result to a sparse array.
        
        Args:
        self (object): The object containing the sparse dataset `sp_xr`.
        
        Returns:
        sparse.SparseArray: A merged and converted sparse array.
        
        Summary:
        This function merges two versions of the sparse dataset `sp_xr` along a new variable dimension using `xr.merge`, renames one of the datasets, and converts the result to a sparse array using
        """

        x = self.sp_xr
        y = xr.merge([x, x.rename("bar")]).to_array()
        assert isinstance(y, sparse.SparseArray)

    @pytest.mark.xfail
    def test_where(self):
        """
        Tests the `where` method for different input types.
        
        This function tests the `where` method of xarray DataArray with various inputs, including a NumPy array, a sparse COO matrix, and an xarray DataArray containing a sparse COO matrix. The `where` method is used to apply a condition to the data and return a new DataArray with values where the condition is `True`.
        
        Parameters:
        None
        
        Returns:
        None
        
        Methods Used:
        """

        a = np.arange(10)
        cond = a > 3
        xr.DataArray(a).where(cond)

        s = sparse.COO.from_numpy(a)
        cond = s > 3
        xr.DataArray(s).where(cond)

        x = xr.DataArray(s)
        cond = x > 3
        x.where(cond)


class TestSparseCoords:
    @pytest.mark.xfail(reason="Coercion of coords to dense")
    def test_sparse_coords(self):
        """
        Tests creating a DataArray with sparse coordinates.
        
        This function creates a `DataArray` using the `sparse.COO` format from NumPy
        arrays. The `DataArray` is initialized with the following parameters:
        - Data: A `sparse.COO` object created from a NumPy array of integers ranging
        from 0 to 3.
        - Dimensions: A single dimension named 'x'.
        - Coordinates: A coordinate 'x' associated with the dimension 'x
        """

        xr.DataArray(
            sparse.COO.from_numpy(np.arange(4)),
            dims=["x"],
            coords={"x": sparse.COO.from_numpy([1, 2, 3, 4])},
        )


@requires_dask
def test_chunk():
    """
    Chunk a sparse COO array or dataset.
    
    This function takes a `DataArray` or `Dataset` containing a sparse COO
    array and chunks it into smaller arrays or datasets based on the specified
    chunk size. The resulting chunked object retains the original data's
    structure but is divided into chunks for efficient computation.
    
    Parameters:
    None
    
    Returns:
    A chunked `DataArray` or `Dataset` with the same data but divided into
    smaller
    """

    s = sparse.COO.from_numpy(np.array([0, 0, 1, 2]))
    a = DataArray(s)
    ac = a.chunk(2)
    assert ac.chunks == ((2, 2),)
    assert isinstance(ac.data._meta, sparse.COO)
    assert_identical(ac, a)

    ds = a.to_dataset(name="a")
    dsc = ds.chunk(2)
    assert dsc.chunks == {"dim_0": (2, 2)}
    assert_identical(dsc, ds)


@requires_dask
def test_dask_token():
    """
    Tokenizes Dask-backed sparse arrays and their operations.
    
    This function tests the tokenization of Dask-backed sparse arrays using the `dask` library. It ensures that the tokenization process correctly identifies the unique identity of an array and its chunked version, as well as the impact of arithmetic operations on the token.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `dask.base.tokenize`: Tokenizes the given Dask-backed sparse array.
    """

    import dask

    s = sparse.COO.from_numpy(np.array([0, 0, 1, 2]))

    # https://github.com/pydata/sparse/issues/300
    s.__dask_tokenize__ = lambda: dask.base.normalize_token(s.__dict__)

    a = DataArray(s)
    t1 = dask.base.tokenize(a)
    t2 = dask.base.tokenize(a)
    t3 = dask.base.tokenize(a + 1)
    assert t1 == t2
    assert t3 != t2
    assert isinstance(a.data, sparse.COO)

    ac = a.chunk(2)
    t4 = dask.base.tokenize(ac)
    t5 = dask.base.tokenize(ac + 1)
    assert t4 != t5
    assert isinstance(ac.data._meta, sparse.COO)


@requires_dask
def test_apply_ufunc_check_meta_coherence():
    """
    Apply a universal function (ufunc) to a sparse DataArray and verify that the metadata coherence is maintained.
    
    This function tests the application of a ufunc to a sparse DataArray using Dask parallelization. It ensures that the metadata of the resulting array remains consistent with the original metadata.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `xr.apply_ufunc`: Applies a ufunc to the sparse DataArray.
    - `assert_sparse_equal
    """

    s = sparse.COO.from_numpy(np.array([0, 0, 1, 2]))
    a = DataArray(s)
    ac = a.chunk(2)
    sparse_meta = ac.data._meta

    result = xr.apply_ufunc(lambda x: x, ac, dask="parallelized").data._meta

    assert_sparse_equal(result, sparse_meta)
