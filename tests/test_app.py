import pytest
import pandas as pd
import os
from handprofil.app import summation, return_wagner_decile, upload_is_valid


def get_absolute_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory_path, relative_path)


def test_summation():
    """
    Testing Summation function
    """
    assert summation(2, 10) == 12
    assert summation(3, 5) == 8
    assert summation(4, 6) == 10


@pytest.mark.parametrize(
    "value, expected",
    [(12, 3), (12.5, 4), (12.7, 5), (13, 6), (20, 19)],
)
def test_return_wagner_decile(value, expected):
    """
    Testing decile function
    """

    bin_edges = [11, 12.5, 13, 14, 15.3, 16, 17, 18, 19]

    result = return_wagner_decile(bin_edges, value)
    assert result == expected


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("input_successful.xlsx", True),
        ("input_missing_indices.xlsx", False),
        ("input_empty.xlsx", False),
        ("input_too_many_indices.xlsx", False),
    ],
)
def test_validate_upload(filename, expected):
    """
    Testing Upload Function
    """
    # Arrange
    df = pd.read_excel(get_absolute_path(f"data/{filename}"))

    result, _ = upload_is_valid(df)
    assert result == expected
