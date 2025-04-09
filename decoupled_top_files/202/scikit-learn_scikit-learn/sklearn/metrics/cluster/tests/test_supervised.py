import numpy as np
import pytest

from sklearn.metrics.cluster import adjusted_mutual_info_score
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.metrics.cluster import completeness_score
from sklearn.metrics.cluster import contingency_matrix
from sklearn.metrics.cluster import entropy
from sklearn.metrics.cluster import expected_mutual_information
from sklearn.metrics.cluster import fowlkes_mallows_score
from sklearn.metrics.cluster import homogeneity_completeness_v_measure
from sklearn.metrics.cluster import homogeneity_score
from sklearn.metrics.cluster import mutual_info_score
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.metrics.cluster import v_measure_score
from sklearn.metrics.cluster._supervised import _generalized_average

from sklearn.utils import assert_all_finite
from sklearn.utils._testing import (
        assert_almost_equal, ignore_warnings)
from numpy.testing import assert_array_almost_equal


score_funcs = [
    adjusted_rand_score,
    homogeneity_score,
    completeness_score,
    v_measure_score,
    adjusted_mutual_info_score,
    normalized_mutual_info_score,
]


@ignore_warnings(category=FutureWarning)
def test_error_messages_on_wrong_input():
    """
    Test error messages for various incorrect inputs.
    
    This function tests the behavior of different scoring functions when
    given incorrect input data, such as inconsistent sample sizes or
    multi-dimensional arrays. It ensures that appropriate error messages
    are raised for these cases.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: When the input data does not meet the expected criteria.
    
    Functions Used:
    - score_funcs: A list of scoring functions to be tested.
    """

    for score_func in score_funcs:
        expected = (r'Found input variables with inconsistent numbers '
                    r'of samples: \[2, 3\]')
        with pytest.raises(ValueError, match=expected):
            score_func([0, 1], [1, 1, 1])

        expected = r"labels_true must be 1D: shape is \(2"
        with pytest.raises(ValueError, match=expected):
            score_func([[0, 1], [1, 0]], [1, 1, 1])

        expected = r"labels_pred must be 1D: shape is \(2"
        with pytest.raises(ValueError, match=expected):
            score_func([0, 1, 0], [[1, 1], [0, 0]])


def test_generalized_average():
    """
    Test the generalized average function.
    
    Args:
    None
    
    Returns:
    None
    
    Summary:
    This function tests the `_generalized_average` function with different methods ("min", "geometric", "arithmetic", "max") and inputs (a, b and c, d). It checks if the returned values are in ascending order for the first set of inputs and if all values are equal for the second set of inputs.
    """

    a, b = 1, 2
    methods = ["min", "geometric", "arithmetic", "max"]
    means = [_generalized_average(a, b, method) for method in methods]
    assert means[0] <= means[1] <= means[2] <= means[3]
    c, d = 12, 12
    means = [_generalized_average(c, d, method) for method in methods]
    assert means[0] == means[1] == means[2] == means[3]


@ignore_warnings(category=FutureWarning)
def test_perfect_matches():
    """
    Test perfect matches for various scoring functions.
    
    This function evaluates the performance of different scoring functions on
    several test cases where the inputs are perfectly matched. The scoring
    functions include:
    
    - `normalized_mutual_info_score`
    - `adjusted_mutual_info_score`
    
    The test cases cover scenarios with empty lists, single elements, and
    lists with multiple elements. The scoring functions are tested with
    different aggregation methods for calculating the mean.
    
    Parameters:
    None
    """

    for score_func in score_funcs:
        assert score_func([], []) == 1.0
        assert score_func([0], [1]) == 1.0
        assert score_func([0, 0, 0], [0, 0, 0]) == 1.0
        assert score_func([0, 1, 0], [42, 7, 42]) == 1.0
        assert score_func([0., 1., 0.], [42., 7., 42.]) == 1.0
        assert score_func([0., 1., 2.], [42., 7., 2.]) == 1.0
        assert score_func([0, 1, 2], [42, 7, 2]) == 1.0
    score_funcs_with_changing_means = [
        normalized_mutual_info_score,
        adjusted_mutual_info_score,
    ]
    means = {"min", "geometric", "arithmetic", "max"}
    for score_func in score_funcs_with_changing_means:
        for mean in means:
            assert score_func([], [], mean) == 1.0
            assert score_func([0], [1], mean) == 1.0
            assert score_func([0, 0, 0], [0, 0, 0], mean) == 1.0
            assert score_func([0, 1, 0], [42, 7, 42], mean) == 1.0
            assert score_func([0., 1., 0.], [42., 7., 42.], mean) == 1.0
            assert score_func([0., 1., 2.], [42., 7., 2.], mean) == 1.0
            assert score_func([0, 1, 2], [42, 7, 2], mean) == 1.0


def test_homogeneous_but_not_complete_labeling():
    """
    Test the homogeneity and completeness of a clustering result.
    
    This function evaluates the quality of a clustering result by calculating
    homogeneity, completeness, and V-measure scores. Homogeneity measures whether
    each cluster contains only members of a single class, while completeness
    measures whether all members of a given class are assigned to the same
    cluster. The V-measure is the harmonic mean of these two metrics.
    
    Parameters:
    - labels_true (list): True class labels for
    """

    # homogeneous but not complete clustering
    h, c, v = homogeneity_completeness_v_measure(
        [0, 0, 0, 1, 1, 1],
        [0, 0, 0, 1, 2, 2])
    assert_almost_equal(h, 1.00, 2)
    assert_almost_equal(c, 0.69, 2)
    assert_almost_equal(v, 0.81, 2)


def test_complete_but_not_homogeneous_labeling():
    """
    Calculate homogeneity, completeness, and V-measure for a given clustering.
    
    This function evaluates the quality of a clustering by computing the
    homogeneity, completeness, and V-measure metrics. Homogeneity measures
    whether each cluster contains only members of a single class, while
    completeness measures whether all members of a given class are assigned
    to the same cluster. The V-measure is the harmonic mean of these two
    metrics.
    
    Parameters:
    -----------
    true
    """

    # complete but not homogeneous clustering
    h, c, v = homogeneity_completeness_v_measure(
        [0, 0, 1, 1, 2, 2],
        [0, 0, 1, 1, 1, 1])
    assert_almost_equal(h, 0.58, 2)
    assert_almost_equal(c, 1.00, 2)
    assert_almost_equal(v, 0.73, 2)


def test_not_complete_and_not_homogeneous_labeling():
    """
    Calculate homogeneity, completeness, and V-measure for non-homogeneous and non-complete labeling.
    
    This function evaluates the quality of clustering results when the labels are neither homogeneous (all instances of a class are in the same cluster) nor complete (all clusters contain instances of the same class). It computes the homogeneity, completeness, and V-measure metrics using the `homogeneity_completeness_v_measure` function.
    
    Parameters:
    None
    
    Returns:
    None
    
    Notes:
    """

    # neither complete nor homogeneous but not so bad either
    h, c, v = homogeneity_completeness_v_measure(
        [0, 0, 0, 1, 1, 1],
        [0, 1, 0, 1, 2, 2])
    assert_almost_equal(h, 0.67, 2)
    assert_almost_equal(c, 0.42, 2)
    assert_almost_equal(v, 0.52, 2)


def test_beta_parameter():
    """
    Test the impact of the beta parameter on homogeneity, completeness, and V-measure.
    
    This function evaluates the homogeneity, completeness, and V-measure scores
    using the `homogeneity_completeness_v_measure` and `v_measure_score` functions
    with a specified beta value. The beta parameter is used to adjust the
    importance of homogeneity and completeness in the V-measure calculation.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    """

    # test for when beta passed to
    # homogeneity_completeness_v_measure
    # and v_measure_score
    beta_test = 0.2
    h_test = 0.67
    c_test = 0.42
    v_test = ((1 + beta_test) * h_test * c_test
              / (beta_test * h_test + c_test))

    h, c, v = homogeneity_completeness_v_measure(
        [0, 0, 0, 1, 1, 1],
        [0, 1, 0, 1, 2, 2],
        beta=beta_test)
    assert_almost_equal(h, h_test, 2)
    assert_almost_equal(c, c_test, 2)
    assert_almost_equal(v, v_test, 2)

    v = v_measure_score(
        [0, 0, 0, 1, 1, 1],
        [0, 1, 0, 1, 2, 2],
        beta=beta_test)
    assert_almost_equal(v, v_test, 2)


def test_non_consecutive_labels():
    """
    Test homogeneity, completeness, and V-measure for non-consecutive labels.
    
    This function evaluates the performance of clustering algorithms using
    homogeneity, completeness, and V-measure metrics on datasets with gaps in
    label values. It also calculates the Adjusted Rand Index (ARI) for
    comparison.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - homogeneity_completeness_v_measure: Computes homogeneity, completeness,
    and V-me
    """

    # regression tests for labels with gaps
    h, c, v = homogeneity_completeness_v_measure(
        [0, 0, 0, 2, 2, 2],
        [0, 1, 0, 1, 2, 2])
    assert_almost_equal(h, 0.67, 2)
    assert_almost_equal(c, 0.42, 2)
    assert_almost_equal(v, 0.52, 2)

    h, c, v = homogeneity_completeness_v_measure(
        [0, 0, 0, 1, 1, 1],
        [0, 4, 0, 4, 2, 2])
    assert_almost_equal(h, 0.67, 2)
    assert_almost_equal(c, 0.42, 2)
    assert_almost_equal(v, 0.52, 2)

    ari_1 = adjusted_rand_score([0, 0, 0, 1, 1, 1], [0, 1, 0, 1, 2, 2])
    ari_2 = adjusted_rand_score([0, 0, 0, 1, 1, 1], [0, 4, 0, 4, 2, 2])
    assert_almost_equal(ari_1, 0.24, 2)
    assert_almost_equal(ari_2, 0.24, 2)


@ignore_warnings(category=FutureWarning)
def uniform_labelings_scores(score_func, n_samples, k_range, n_runs=10,
    """
    Generate scores for random uniform cluster labelings.
    
    This function computes the scores for multiple runs of random uniform
    cluster labelings using the provided scoring function. The scores are
    averaged over the specified number of runs for each value of `k` in the
    given range.
    
    Parameters:
    -----------
    score_func : callable
    A scoring function that takes two arrays of cluster labels and returns
    a numerical score.
    n_samples : int
    The number of samples
    """

                             seed=42):
    # Compute score for random uniform cluster labelings
    random_labels = np.random.RandomState(seed).randint
    scores = np.zeros((len(k_range), n_runs))
    for i, k in enumerate(k_range):
        for j in range(n_runs):
            labels_a = random_labels(low=0, high=k, size=n_samples)
            labels_b = random_labels(low=0, high=k, size=n_samples)
            scores[i, j] = score_func(labels_a, labels_b)
    return scores


@ignore_warnings(category=FutureWarning)
def test_adjustment_for_chance():
    # Check that adjusted scores are almost zero on random labels
    n_clusters_range = [2, 10, 50, 90]
    n_samples = 100
    n_runs = 10

    scores = uniform_labelings_scores(
        adjusted_rand_score, n_samples, n_clusters_range, n_runs)

    max_abs_scores = np.abs(scores).max(axis=1)
    assert_array_almost_equal(max_abs_scores, [0.02, 0.03, 0.03, 0.02], 2)


def test_adjusted_mutual_info_score():
    # Compute the Adjusted Mutual Information and test against known values
    labels_a = np.array([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3])
    labels_b = np.array([1, 1, 1, 1, 2, 1, 2, 2, 2, 2, 3, 1, 3, 3, 3, 2, 2])
    # Mutual information
    mi = mutual_info_score(labels_a, labels_b)
    assert_almost_equal(mi, 0.41022, 5)
    # with provided sparse contingency
    C = contingency_matrix(labels_a, labels_b, sparse=True)
    mi = mutual_info_score(labels_a, labels_b, contingency=C)
    assert_almost_equal(mi, 0.41022, 5)
    # with provided dense contingency
    C = contingency_matrix(labels_a, labels_b)
    mi = mutual_info_score(labels_a, labels_b, contingency=C)
    assert_almost_equal(mi, 0.41022, 5)
    # Expected mutual information
    n_samples = C.sum()
    emi = expected_mutual_information(C, n_samples)
    assert_almost_equal(emi, 0.15042, 5)
    # Adjusted mutual information
    ami = adjusted_mutual_info_score(labels_a, labels_b)
    assert_almost_equal(ami, 0.27821, 5)
    ami = adjusted_mutual_info_score([1, 1, 2, 2], [2, 2, 3, 3])
    assert ami == 1.0
    # Test with a very large array
    a110 = np.array([list(labels_a) * 110]).flatten()
    b110 = np.array([list(labels_b) * 110]).flatten()
    ami = adjusted_mutual_info_score(a110, b110)
    assert_almost_equal(ami, 0.38, 2)


def test_expected_mutual_info_overflow():
    # Test for regression where contingency cell exceeds 2**16
    # leading to overflow in np.outer, resulting in EMI > 1
    assert expected_mutual_information(np.array([[70000]]), 70000) <= 1


def test_int_overflow_mutual_info_fowlkes_mallows_score():
    # Test overflow in mutual_info_classif and fowlkes_mallows_score
    x = np.array([1] * (52632 + 2529) + [2] * (14660 + 793) + [3] * (3271 +
                 204) + [4] * (814 + 39) + [5] * (316 + 20))
    y = np.array([0] * 52632 + [1] * 2529 + [0] * 14660 + [1] * 793 +
                 [0] * 3271 + [1] * 204 + [0] * 814 + [1] * 39 + [0] * 316 +
                 [1] * 20)

    assert_all_finite(mutual_info_score(x, y))
    assert_all_finite(fowlkes_mallows_score(x, y))


def test_entropy():
    ent = entropy([0, 0, 42.])
    assert_almost_equal(ent, 0.6365141, 5)
    assert_almost_equal(entropy([]), 1)


def test_contingency_matrix():
    labels_a = np.array([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3])
    labels_b = np.array([1, 1, 1, 1, 2, 1, 2, 2, 2, 2, 3, 1, 3, 3, 3, 2, 2])
    C = contingency_matrix(labels_a, labels_b)
    C2 = np.histogram2d(labels_a, labels_b,
                        bins=(np.arange(1, 5),
                              np.arange(1, 5)))[0]
    assert_array_almost_equal(C, C2)
    C = contingency_matrix(labels_a, labels_b, eps=.1)
    assert_array_almost_equal(C, C2 + .1)


def test_contingency_matrix_sparse():
    labels_a = np.array([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3])
    labels_b = np.array([1, 1, 1, 1, 2, 1, 2, 2, 2, 2, 3, 1, 3, 3, 3, 2, 2])
    C = contingency_matrix(labels_a, labels_b)
    C_sparse = contingency_matrix(labels_a, labels_b, sparse=True).toarray()
    assert_array_almost_equal(C, C_sparse)
    with pytest.raises(ValueError, match="Cannot set 'eps' when sparse=True"):
        contingency_matrix(labels_a, labels_b, eps=1e-10, sparse=True)


@ignore_warnings(category=FutureWarning)
def test_exactly_zero_info_score():
    # Check numerical stability when information is exactly zero
    for i in np.logspace(1, 4, 4).astype(np.int):
        labels_a, labels_b = (np.ones(i, dtype=np.int),
                              np.arange(i, dtype=np.int))
        assert normalized_mutual_info_score(labels_a, labels_b) == 0.0
        assert v_measure_score(labels_a, labels_b) == 0.0
        assert adjusted_mutual_info_score(labels_a, labels_b) == 0.0
        assert normalized_mutual_info_score(labels_a, labels_b) == 0.0
        for method in ["min", "geometric", "arithmetic", "max"]:
            assert adjusted_mutual_info_score(labels_a, labels_b,
                                              method) == 0.0
            assert normalized_mutual_info_score(labels_a, labels_b,
                                                method) == 0.0


def test_v_measure_and_mutual_information(seed=36):
    # Check relation between v_measure, entropy and mutual information
    for i in np.logspace(1, 4, 4).astype(np.int):
        random_state = np.random.RandomState(seed)
        labels_a, labels_b = (random_state.randint(0, 10, i),
                              random_state.randint(0, 10, i))
        assert_almost_equal(v_measure_score(labels_a, labels_b),
                            2.0 * mutual_info_score(labels_a, labels_b) /
                            (entropy(labels_a) + entropy(labels_b)), 0)
        avg = 'arithmetic'
        assert_almost_equal(v_measure_score(labels_a, labels_b),
                            normalized_mutual_info_score(labels_a, labels_b,
                                                         average_method=avg)
                            )


def test_fowlkes_mallows_score():
    # General case
    score = fowlkes_mallows_score([0, 0, 0, 1, 1, 1],
                                  [0, 0, 1, 1, 2, 2])
    assert_almost_equal(score, 4. / np.sqrt(12. * 6.))

    # Perfect match but where the label names changed
    perfect_score = fowlkes_mallows_score([0, 0, 0, 1, 1, 1],
                                          [1, 1, 1, 0, 0, 0])
    assert_almost_equal(perfect_score, 1.)

    # Worst case
    worst_score = fowlkes_mallows_score([0, 0, 0, 0, 0, 0],
                                        [0, 1, 2, 3, 4, 5])
    assert_almost_equal(worst_score, 0.)


def test_fowlkes_mallows_score_properties():
    # handcrafted example
    labels_a = np.array([0, 0, 0, 1, 1, 2])
    labels_b = np.array([1, 1, 2, 2, 0, 0])
    expected = 1. / np.sqrt((1. + 3.) * (1. + 2.))
    # FMI = TP / sqrt((TP + FP) * (TP + FN))

    score_original = fowlkes_mallows_score(labels_a, labels_b)
    assert_almost_equal(score_original, expected)

    # symmetric property
    score_symmetric = fowlkes_mallows_score(labels_b, labels_a)
    assert_almost_equal(score_symmetric, expected)

    # permutation property
    score_permuted = fowlkes_mallows_score((labels_a + 1) % 3, labels_b)
    assert_almost_equal(score_permuted, expected)

    # symmetric and permutation(both together)
    score_both = fowlkes_mallows_score(labels_b, (labels_a + 2) % 3)
    assert_almost_equal(score_both, expected)
