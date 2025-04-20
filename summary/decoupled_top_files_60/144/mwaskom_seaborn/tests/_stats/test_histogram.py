
import numpy as np
import pandas as pd

import pytest
from numpy.testing import assert_array_equal

from seaborn._core.groupby import GroupBy
from seaborn._stats.histogram import Hist


class TestHist:

    @pytest.fixture
    def single_args(self):
        """
        Generates a GroupBy object and a scale configuration for a single argument.
        
        This function creates a GroupBy object with a specified group column and a Scale object for a given argument. The Scale object is initialized with a continuous scale type.
        
        Parameters:
        None
        
        Returns:
        tuple: A tuple containing the GroupBy object, the argument name ('x' in this case), and a dictionary with the argument name and the Scale object.
        
        Example:
        >>> groupby, arg_name, scale_config =
        """


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

        h = Hist(bins="sqrt")
        bin_kws = h._define_bin_params(long_df, "x", "continuous")
        assert bin_kws["range"] == (long_df["x"].min(), long_df["x"].max())
        assert bin_kws["bins"] == int(np.sqrt(len(long_df)))

    def test_int_bins(self, long_df):
        """
        Function to test the binning process for a histogram.
        
        This function tests the binning process for a histogram by creating a histogram object with a specified number of bins and then defining the bin parameters based on the provided DataFrame and column.
        
        Parameters:
        long_df (pandas.DataFrame): The DataFrame containing the data to be binned.
        
        Returns:
        None: This function does not return any value. It asserts the correctness of the bin parameters.
        
        Key Parameters:
        n (int): The number of bins
        """


        n = 24
        h = Hist(bins=n)
        bin_kws = h._define_bin_params(long_df, "x", "continuous")
        assert bin_kws["range"] == (long_df["x"].min(), long_df["x"].max())
        assert bin_kws["bins"] == n

    def test_array_bins(self, long_df):
        """
        Function to test the binning process for a histogram.
        
        This function checks if the binning process for a histogram is correctly defined based on the provided bins.
        
        Parameters:
        long_df (pandas.DataFrame): The DataFrame containing the data to be binned.
        
        Returns:
        None: The function asserts the correctness of the binning process and does not return any value.
        
        Key Parameters:
        bins (list): A list of bin edges. The function checks if these edges are correctly assigned to the histogram bins
        """


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
        Generate discrete bins for a given DataFrame column.
        
        This function creates bins for a discrete column in a DataFrame. It is used to define the binning parameters for a histogram where the data is considered discrete.
        
        Parameters:
        long_df (pandas.DataFrame): The DataFrame containing the data to be binned.
        
        Returns:
        dict: A dictionary containing the binning parameters, specifically the range and number of bins.
        
        Key Steps:
        1. Convert the 'x' column in the DataFrame to integer type
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
        """
        Function to test the count statistic in a histogram.
        
        This function creates a histogram using the specified statistic ("count") and checks if the sum of the counts equals the number of rows in the input DataFrame.
        
        Parameters:
        long_df (pandas.DataFrame): The input DataFrame containing the data to be histogrammed.
        single_args (tuple): A tuple containing the single argument(s) required by the histogram function, typically bin edges or similar parameters.
        
        Returns:
        pandas.DataFrame: A DataFrame containing the histogram results
        """


        h = Hist(stat="count")
        out = h(long_df, *single_args)
        assert out["y"].sum() == len(long_df)

    def test_probability_stat(self, long_df, single_args):

        h = Hist(stat="probability")
        out = h(long_df, *single_args)
        assert out["y"].sum() == 1

    def test_proportion_stat(self, long_df, single_args):
        """
        Function to test the proportion statistic in a histogram.
        
        This function creates a histogram using the specified statistic as "proportion" and checks if the sum of the y-values equals 1, which is expected for a proportion.
        
        Parameters:
        long_df (pandas.DataFrame): The long-form DataFrame containing the data to be binned and counted.
        single_args (tuple): A tuple containing the arguments required to configure the histogram, such as bins or range.
        
        Returns:
        pandas.DataFrame: A DataFrame containing
        """


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
        """
        Tests the cumulative count functionality of a histogram.
        
        This function evaluates the cumulative count of occurrences in a given DataFrame.
        
        Parameters:
        long_df (pandas.DataFrame): The DataFrame containing the data to be binned and counted.
        single_args (tuple): A tuple containing the arguments to be passed to the histogram function.
        
        Returns:
        pandas.Series: A series containing the cumulative count of occurrences.
        
        Assertions:
        - The maximum value in the 'y' column of the output should equal the length of the
        """


        h = Hist(stat="count", cumulative=True)
        out = h(long_df, *single_args)
        assert out["y"].max() == len(long_df)

    def test_cumulative_proportion(self, long_df, single_args):
        """
        Tests the cumulative proportion functionality of the Hist object.
        
        This function evaluates whether the cumulative proportion of a histogram
        computed using the Hist object with the `stat="proportion"` and `cumulative=True`
        parameters correctly sums to 1 for the maximum value in the output.
        
        Parameters:
        long_df (pandas.DataFrame): The input DataFrame containing the data to be binned and aggregated.
        single_args (tuple): A tuple containing the additional arguments required by the Hist object.
        
        Returns:
        None:
        """


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
        """
        Function to test the common normalization behavior in a histogram.
        
        This function checks whether the common normalization flag is correctly applied to the histogram. It ensures that the sum of the 'y' column in each group of the output is approximately 100 when common normalization is set to False.
        
        Parameters:
        long_df (pandas.DataFrame): The input DataFrame containing the data to be histogrammed.
        triple_args (tuple): A tuple containing the arguments needed to perform the histogram operation.
        
        Returns:
        pandas
        """


        h = Hist(stat="percent", common_norm=False)
        out = h(long_df, *triple_args)
        for _, out_part in out.groupby(["a", "s"]):
            assert out_part["y"].sum() == pytest.approx(100)

    def test_common_norm_subset(self, long_df, triple_args):
        """
        Tests the common normalization functionality on a subset of data.
        
        This function checks if the common normalization on the 'a' column results in the sum of the 'y' column being approximately 100 for each unique value in 'a'.
        
        Parameters:
        long_df (pandas.DataFrame): The input DataFrame containing the data to be normalized.
        triple_args (tuple): A tuple containing the arguments required for the histogram calculation.
        
        Returns:
        pandas.DataFrame: A DataFrame with the normalized data.
        
        Key Points
        """


        h = Hist(stat="percent", common_norm=["a"])
        out = h(long_df, *triple_args)
        for _, out_part in out.groupby(["a"]):
            assert out_part["y"].sum() == pytest.approx(100)

    def test_common_bins_default(self, long_df, triple_args):
        """
        Function to test the common bins functionality of a histogram object.
        
        This function checks if the histogram object correctly groups and bins the input DataFrame based on specified arguments.
        
        Parameters:
        long_df (pandas.DataFrame): The input DataFrame containing the data to be binned.
        triple_args (tuple): A tuple containing the arguments to be passed to the histogram object for binning.
        
        Returns:
        None: The function asserts that all groups in the output have the same bins.
        
        Example:
        >>> long_df =
        """


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
        Function to test the creation of histograms with common bins.
        
        This function checks that when `common_bins` is set to `False`, the histograms
        generated for different groups of the 'a' column have distinct bin edges.
        
        Parameters:
        long_df (pandas.DataFrame): The input DataFrame containing the data.
        triple_args (tuple): A tuple containing the arguments needed for the histogram
        function. Typically, these are the columns to group by and
        the column to bin.
        
        Returns:
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
t["space"], np.diff(edges))
