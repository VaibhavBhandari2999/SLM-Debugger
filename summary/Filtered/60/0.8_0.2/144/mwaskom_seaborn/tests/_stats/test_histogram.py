
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
        """
        Generate a grouped aggregation with a scaled continuous variable.
        
        This function returns a GroupBy object, a column name, and a dictionary specifying the column and its scale type.
        
        Parameters:
        None
        
        Returns:
        tuple: A tuple containing:
        - GroupBy: A GroupBy object with specified grouping columns.
        - str: The column name to aggregate.
        - dict: A dictionary specifying the column and its scale type for aggregation.
        """


        groupby = GroupBy(["group", "a", "s"])

        class Scale:
            scale_type = "continuous"

        return groupby, "x", {"x": Scale()}

    def test_string_bins(self, long_df):

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
        """
        Function to test the binning parameters for discrete data in a histogram.
        
        This function tests the binning parameters for a discrete variable in a histogram.
        It calculates the bin range and number of bins based on the minimum and maximum values of the 'x' column in the provided DataFrame.
        
        Parameters:
        long_df (pandas.DataFrame): DataFrame containing the data to be binned.
        
        Returns:
        None: This function does not return any value. It asserts the correctness of the binning parameters.
        
        Key Assertions
        """


        h = Hist(discrete=True)
        x = long_df["x"].astype(int)
        bin_kws = h._define_bin_params(long_df.assign(x=x), "x", "continuous")
        assert bin_kws["range"] == (x.min() - .5, x.max() + .5)
        assert bin_kws["bins"] == (x.max() - x.min() + 1)

    def test_discrete_bins_from_nominal_scale(self, rng):

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
        """
        Tests the probability statistic functionality of a histogram.
        
        This function evaluates whether the sum of the y-values (frequencies) in a histogram equals 1, which is a characteristic of a probability distribution.
        
        Parameters:
        long_df (pandas.DataFrame): The DataFrame containing the data to be binned and plotted.
        single_args (tuple): A tuple containing the arguments to be passed to the histogram function. These typically include the column name for the x-values and optionally the number of bins.
        
        Returns:
        """


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
        """
        Tests the cumulative density function for a histogram.
        
        This function evaluates the cumulative density of a histogram using the specified arguments. It computes the histogram with a density statistic and cumulative sum.
        
        Parameters:
        long_df (pandas.DataFrame): The input DataFrame containing the data to be binned and aggregated.
        single_args (tuple): A tuple containing the arguments required to compute the histogram, such as bins, range, etc.
        
        Returns:
        pandas.DataFrame: A DataFrame containing the bin edges and the cumulative density values
        """


        h = Hist(stat="density", cumulative=True)
        out = h(long_df, *single_args)
        assert out["y"].max() == 1

    def test_common_norm_default(self, long_df, triple_args):
        """
        Function to test the normalization of a histogram using default settings.
        
        Parameters:
        long_df (pandas.DataFrame): The input DataFrame containing the data to be histogrammed.
        triple_args (tuple): A tuple containing three arguments required for the histogram function.
        
        Returns:
        pandas.DataFrame: A DataFrame containing the histogram results with normalized values.
        
        The function creates a histogram using the specified DataFrame and arguments, with normalization set to "percent". The sum of the normalized values in the 'y' column of the output
        """


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
        """
        Tests the functionality of the `Hist` function with the `common_bins=False` option.
        
        This function evaluates the `Hist` function's ability to handle different binning for each group when `common_bins=False`.
        
        Parameters:
        - long_df (pandas.DataFrame): The input DataFrame containing the data to be binned.
        - triple_args (tuple): A tuple containing the arguments required by the `Hist` function.
        
        Returns:
        - None: The function asserts the correctness of the output through internal checks.
        
        Key
        """


        h = Hist(common_bins=False)
        out = h(long_df, *triple_args)
        bins = []
        for _, out_part in out.groupby(["a"]):
            bins.append(tuple(out_part["x"]))
        assert len(set(bins)) == out["a"].nunique()

    def test_histogram_single(self, long_df, single_args):

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
