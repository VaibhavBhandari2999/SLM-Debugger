
import numpy as np
import pandas as pd

import pytest
from numpy.testing import assert_array_equal, assert_array_almost_equal

from seaborn._core.groupby import GroupBy
from seaborn._stats.regression import PolyFit


class TestPolyFit:

    @pytest.fixture
    def df(self, rng):

        n = 100
        return pd.DataFrame(dict(
            x=rng.normal(0, 1, n),
            y=rng.normal(0, 1, n),
            color=rng.choice(["a", "b", "c"], n),
            group=rng.choice(["x", "y"], n),
        ))

    def test_no_grouper(self, df):
        """
        Tests the `PolyFit` function without a grouper.
        
        This function evaluates the `PolyFit` function on a DataFrame `df` without using a grouper. It fits a polynomial of order 1 to the 'x' and 'y' columns of the DataFrame.
        
        Parameters:
        df (pandas.DataFrame): The input DataFrame containing the 'x' and 'y' columns.
        
        Returns:
        pandas.DataFrame: A DataFrame containing the fitted polynomial values for 'x' and 'y' over
        """


        groupby = GroupBy(["group"])
        res = PolyFit(order=1, gridsize=100)(df[["x", "y"]], groupby, "x", {})

        assert_array_equal(res.columns, ["x", "y"])

        grid = np.linspace(df["x"].min(), df["x"].max(), 100)
        assert_array_equal(res["x"], grid)
        assert_array_almost_equal(
            res["y"].diff().diff().dropna(), np.zeros(grid.size - 2)
        )

    def test_one_grouper(self, df):

        groupby = GroupBy(["group"])
        gridsize = 50
        res = PolyFit(gridsize=gridsize)(df, groupby, "x", {})

        assert res.columns.to_list() == ["x", "y", "group"]

        ngroups = df["group"].nunique()
        assert_array_equal(res.index, np.arange(ngroups * gridsize))

        for _, part in res.groupby("group"):
            grid = np.linspace(part["x"].min(), part["x"].max(), gridsize)
            assert_array_equal(part["x"], grid)
            assert part["y"].diff().diff().dropna().abs().gt(0).all()
).dropna().abs().gt(0).all()
