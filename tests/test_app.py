import pytest
import pandas as pd
from src.app import summation, return_wagner_decile, validate_upload


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
    attributes = pd.read_csv("../lib/tables/attributes.csv", header=0, index_col=False)
    meta_attributes = pd.read_csv(
        "../lib/tables/meta_attributes.csv", header=0, index_col=False
    )

    df = pd.read_excel(f"test_data/{filename}")

    assert validate_upload(df, attributes, meta_attributes) == expected
