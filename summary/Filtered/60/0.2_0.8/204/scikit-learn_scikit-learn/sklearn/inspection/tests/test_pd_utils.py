import numpy as np
import pytest

from sklearn.utils._testing import _convert_container

from sklearn.inspection._pd_utils import _check_feature_names, _get_feature_index


@pytest.mark.parametrize(
    "feature_names, array_type, expected_feature_names",
    [
        (None, "array", ["x0", "x1", "x2"]),
        (None, "dataframe", ["a", "b", "c"]),
        (np.array(["a", "b", "c"]), "array", ["a", "b", "c"]),
    ],
)
def test_check_feature_names(feature_names, array_type, expected_feature_names):
    """
    Validate feature names for a given array-like object.
    
    Parameters:
    feature_names (list or None): List of feature names to be validated. If None, the function will use the column names of the input array.
    array_type (str): The type of the input array, used for conversion.
    expected_feature_names (list): The expected list of feature names after validation.
    
    Returns:
    list: The validated list of feature names.
    
    Raises:
    ValueError: If the feature names do not match
    """

    X = np.random.randn(10, 3)
    column_names = ["a", "b", "c"]
    X = _convert_container(X, constructor_name=array_type, columns_name=column_names)
    feature_names_validated = _check_feature_names(X, feature_names)
    assert feature_names_validated == expected_feature_names


def test_check_feature_names_error():
    """
    Function to check if the provided feature names contain duplicates.
    
    Parameters:
    X (numpy.ndarray): A 2D numpy array representing the input features.
    feature_names (list): A list of strings representing the names of the features.
    
    Raises:
    ValueError: If the feature_names list contains duplicate entries.
    
    This function is used to validate the feature names before further processing. It ensures that each feature name is unique, which is a requirement for many machine learning algorithms.
    """

    X = np.random.randn(10, 3)
    feature_names = ["a", "b", "c", "a"]
    msg = "feature_names should not contain duplicates."
    with pytest.raises(ValueError, match=msg):
        _check_feature_names(X, feature_names)


@pytest.mark.parametrize("fx, idx", [(0, 0), (1, 1), ("a", 0), ("b", 1), ("c", 2)])
def test_get_feature_index(fx, idx):
    feature_names = ["a", "b", "c"]
    assert _get_feature_index(fx, feature_names) == idx


@pytest.mark.parametrize(
    "fx, feature_names, err_msg",
    [
        ("a", None, "Cannot plot partial dependence for feature 'a'"),
        ("d", ["a", "b", "c"], "Feature 'd' not in feature_names"),
    ],
)
def test_get_feature_names_error(fx, feature_names, err_msg):
    with pytest.raises(ValueError, match=err_msg):
        _get_feature_index(fx, feature_names)
