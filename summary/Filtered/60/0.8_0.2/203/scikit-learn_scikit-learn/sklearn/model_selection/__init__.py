import typing

from ._split import BaseCrossValidator
from ._split import BaseShuffleSplit
from ._split import KFold
from ._split import GroupKFold
from ._split import StratifiedKFold
from ._split import TimeSeriesSplit
from ._split import LeaveOneGroupOut
from ._split import LeaveOneOut
from ._split import LeavePGroupsOut
from ._split import LeavePOut
from ._split import RepeatedKFold
from ._split import RepeatedStratifiedKFold
from ._split import ShuffleSplit
from ._split import GroupShuffleSplit
from ._split import StratifiedShuffleSplit
from ._split import StratifiedGroupKFold
from ._split import PredefinedSplit
from ._split import train_test_split
from ._split import check_cv

from ._validation import cross_val_score
from ._validation import cross_val_predict
from ._validation import cross_validate
from ._validation import learning_curve
from ._validation import permutation_test_score
from ._validation import validation_curve

from ._search import GridSearchCV
from ._search import RandomizedSearchCV
from ._search import ParameterGrid
from ._search import ParameterSampler

from ._plot import LearningCurveDisplay

if typing.TYPE_CHECKING:
    # Avoid errors in type checkers (e.g. mypy) for experimental estimators.
    # TODO: remove this check once the estimator is no longer experimental.
    from ._search_successive_halving import (  # noqa
        HalvingGridSearchCV,
        HalvingRandomSearchCV,
    )


__all__ = [
    "BaseCrossValidator",
    "BaseShuffleSplit",
    "GridSearchCV",
    "TimeSeriesSplit",
    "KFold",
    "GroupKFold",
    "GroupShuffleSplit",
    "LeaveOneGroupOut",
    "LeaveOneOut",
    "LeavePGroupsOut",
    "LeavePOut",
    "RepeatedKFold",
    "RepeatedStratifiedKFold",
    "ParameterGrid",
    "ParameterSampler",
    "PredefinedSplit",
    "RandomizedSearchCV",
    "ShuffleSplit",
    "StratifiedKFold",
    "StratifiedGroupKFold",
    "StratifiedShuffleSplit",
    "check_cv",
    "cross_val_predict",
    "cross_val_score",
    "cross_validate",
    "learning_curve",
    "LearningCurveDisplay",
    "permutation_test_score",
    "train_test_split",
    "validation_curve",
]


# TODO: remove this check once the estimator is no longer experimental.
def __getattr__(name):
    """
    This function is used to handle attribute access for the `sklearn` module. It checks if the requested attribute is one of the experimental classes `HalvingGridSearchCV` or `HalvingRandomSearchCV`. If so, it raises an ImportError with a detailed message indicating that these classes are experimental and require an explicit import statement. If the attribute is not recognized, it raises an AttributeError with a message indicating that the attribute does not exist in the module.
    
    Parameters:
    - name (str): The
    """

    if name in {"HalvingGridSearchCV", "HalvingRandomSearchCV"}:
        raise ImportError(
            f"{name} is experimental and the API might change without any "
            "deprecation cycle. To use it, you need to explicitly import "
            "enable_halving_search_cv:\n"
            "from sklearn.experimental import enable_halving_search_cv"
        )
    raise AttributeError(f"module {__name__} has no attribute {name}")
