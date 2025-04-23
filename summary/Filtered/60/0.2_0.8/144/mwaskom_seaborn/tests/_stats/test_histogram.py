
import numpy as np
import pandas as pd

import pytest
from numpy.testing import assert_array_equal

from seaborn._core.groupby import GroupBy
from seaborn._stats.histogram import Hist


class TestHist:

    @pytest.fixture
    def single_args(self):

        groupby = GroupBy(["group"])

        class Scale:
            scale_type = "continuous"

        return groupby, "x", {"x": Scale()}

    @pytest.fixture
    def triple_args(self):

        groupby = GroupBy(["group", "a", "s"])

        class Scale:
            scale_type = "continuous"

        return groupby, "x", {"x": Scale()}

    def test_string_bins(self, long_df):
        """
        Tests the binning functionality of a histogram object.
        
        This function checks the binning parameters for a histogram object with a specified number of bins. It calculates and returns the bin range and the number of bins based on the input DataFrame and column.
        
        Parameters:
        long_df (pandas.DataFrame): The input DataFrame containing the data to be binned.
        
        Returns:
        None: This function asserts the correctness of the binning parameters rather than returning a value.
        
        Key Parameters:
        - `bins` (str
        """


        h = Hist(bins="sqrt")
        bin_kws = h._define_bin_params(long_df, "x", "continuous")
        assert bin_kws["range"] == (long_df["x"].min(), long_df["x"].max())
        assert bin_kws["bins"] == int(np.sqrt(len(long_df)))

    def test_int_bins(self, long_df):

        n = 24
        h = Hist(bins=n)
        bin_kws = h._define_bin_params(long_df, "x", "continuous")
        assert bin_kws["range"] == (long_df["x"].min(), long_df["x"].max())
        assert bin_kws["bins"] == n

    def test_array_bins(self, long_df):

        bins = [-3, -2, 1, 2, 3]
        h = Hist(bins=bins)
        bin_kws = h._define_bin_params(long_df, "x", "continuous")
        assert_array_equal(bin_kws["bins"], bins)

    def test_binwidth(self, long_df):
        """
        Function to test the binwidth calculation for a histogram.
        
        Parameters:
        long_df (pandas.DataFrame): A DataFrame containing the data to be binned.
        
        Returns:
        None: This function does not return any value. It asserts that the calculated binwidth matches the expected value.
        
        Key Parameters:
        - binwidth (float): The expected binwidth for the histogram.
        
        This function creates a histogram object with the specified binwidth, defines bin parameters for a continuous variable 'x' in the DataFrame,
        """


        binwidth = .5
        h = Hist(binwidth=binwidth)
        bin_kws = h._define_bin_params(long_df, "x", "continuous")
        n_bins = bin_kws["bins"]
        left, right = bin_kws["range"]
        assert (right - left) / n_bins == pytest.approx(binwidth)

    def test_binrange(self, long_df):

        binrange = (-4, 4)
        h = Hist(binrange=binrange)
        bin_kws = h._define_bin_params(long_df, "x", "continuous")
        assert bin_kws["range"] == binrange

    def test_discrete_bins(self, long_df):

        h = Hist(discrete=True)
        x = long_df["x"].astype(int)
        bin_kws = h._define_bin_params(long_df.assign(x=x), "x", "continuous")
        assert bin_kws["range"] == (x.min() - .5, x.max() + .5)
        assert bin_kws["bins"] == (x.max() - x.min() + 1)

    def test_discrete_bins_from_nominal_scale(self, rng):
        """
        Tests the binning behavior for a discrete variable from a nominal scale.
        
        This function tests the `_define_bin_params` method of the `Hist` class to ensure that it correctly defines the binning parameters for a discrete variable from a nominal scale.
        
        Parameters:
        rng (numpy.random.Generator): A random number generator used to generate test data.
        
        Returns:
        None: This function asserts the correctness of the binning parameters and does not return any value.
        
        Key Parameters:
        - `rng`: The
        """


        h = Hist()
        x = rng.randint(0, 5, 10)
        df = pd.DataFrame({"x": x})
        bin_kws = h._define_bin_params(df, "x", "nominal")
        assert bin_kws["range"] == (x.min() - .5, x.max() + .5)
        assert bin_kws["bins"] == (x.max() - x.min() + 1)

    def test_count_stat(self, long_df, single_args):

        h = Hist(stat="count")
        out = h(long_df, *single_args)
        assert out["y"].sum() == len(long_df)

    def test_probability_stat(self, long_df, single_args):

        h = Hist(stat="probability")
        out = h(long_df, *single_args)
        assert out["y"].sum() == 1

    def test_proportion_stat(self, long_df, single_args):

        h = Hist(stat="proportion")
        out = h(long_df, *single_args)
        assert out["y"].sum() == 1

    def test_percent_stat(self, long_df, single_args):

        h = Hist(stat="percent")
        out = h(long_df, *single_args)
        assert out["y"].sum() == 100

    def test_density_stat(self, long_df, single_args):

        h = Hist(stat="density")
        out = h(long_df, *single_args)
        assert (out["y"] * out["space"]).sum() == 1

    def test_frequency_stat(self, long_df, single_args):

        h = Hist(stat="frequency")
        out = h(long_df, *single_args)
        assert (out["y"] * out["space"]).sum() == len(long_df)

    def test_cumulative_count(self, long_df, single_args):

        h = Hist(stat="count", cumulative=True)
        out = h(long_df, *single_args)
        assert out["y"].max() == len(long_df)

    def test_cumulative_proportion(self, long_df, single_args):

        h = Hist(stat="proportion", cumulative=True)
        out = h(long_df, *single_args)
        assert out["y"].max() == 1

    def test_cumulative_density(self, long_df, single_args):

        h = Hist(stat="density", cumulative=True)
        out = h(long_df, *single_args)
        assert out["y"].max() == 1

    def test_common_norm_default(self, long_df, triple_args):

        h = Hist(stat="percent")
        out = h(long_df, *triple_args)
        assert out["y"].sum() == pytest.approx(100)

    def test_common_norm_false(self, long_df, triple_args):

        h = Hist(stat="percent", common_norm=False)
        out = h(long_df, *triple_args)
        for _, out_part in out.groupby(["a", "s"]):
            assert out_part["y"].sum() == pytest.approx(100)

    def test_common_norm_subset(self, long_df, triple_args):

        h = Hist(stat="percent", common_norm=["a"])
        out = h(long_df, *triple_args)
        for _, out_part in out.groupby(["a"]):
            assert out_part["y"].sum() == pytest.approx(100)

    def test_common_bins_default(self, long_df, triple_args):

        h = Hist()
        out = h(long_df, *triple_args)
        bins = []
        for _, out_part in out.groupby(["a", "s"]):
            bins.append(tuple(out_part["x"]))
        assert len(set(bins)) == 1

    def test_common_bins_false(self, long_df, triple_args):

        h = Hist(common_bins=False)
        out = h(long_df, *triple_args)
        bins = []
        for _, out_part in out.groupby(["a", "s"]):
            bins.append(tuple(out_part["x"]))
        assert len(set(bins)) == len(out.groupby(["a", "s"]))

    def test_common_bins_subset(self, long_df, triple_args):

        h = Hist(common_bins=False)
        out = h(long_df, *triple_args)
        bins = []
        for _, out_part in out.groupby(["a"]):
            bins.append(tuple(out_part["x"]))
        assert len(set(bins)) == out["a"].nunique()

    def test_histogram_single(self, long_df, single_args):
        """
        Tests the histogram functionality for a single argument.
        
        This function tests the histogram generation for a single argument using the Hist class. It takes a DataFrame and a set of arguments, generates a histogram, and compares the result with the expected output.
        
        Parameters:
        long_df (pandas.DataFrame): The DataFrame containing the data to be histogrammed. The DataFrame must have a column named 'x'.
        single_args (tuple): A tuple of arguments to be passed to the Hist class for histogram generation.
        
        Returns:
        """


        h = Hist()
        out = h(long_df, *single_args)
        hist, edges = np.histogram(long_df["x"], bins="auto")
        assert_array_equal(out["y"], hist)
        assert_array_equal(out["space"], np.diff(edges))

    def test_histogram_multiple(self, long_df, triple_args):

        h = Hist()
        out = h(long_df, *triple_args)
        bins = np.histogram_bin_edges(long_df["x"], "auto")
        for (a, s), out_part in out.groupby(["a", "s"]):
            x = long_df.loc[(long_df["a"] == a) & (long_df["s"] == s), "x"]
            hist, edges = np.histogram(x, bins=bins)
            assert_array_equal(out_part["y"], hist)
            assert_array_equal(out_part["space"], np.diff(edges))
