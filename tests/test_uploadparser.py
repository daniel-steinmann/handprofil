import os
import pytest
import pandas as pd
from handprofil.uploadparser import (
    split_metadata_data,
    validate_meta_attributes,
    validate_upload_format
)


def get_testfile_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory_path, relative_path)


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("input_successful.xlsx", True),
        ("input_missing_indices.xlsx", False),
        ("input_empty.xlsx", False),
        ("input_too_many_indices.xlsx", False),
    ],
)
def test_upload_is_valid(filename, expected):
    """
    Testing Upload Function
    """
    # Arrange
    df = pd.read_excel(get_testfile_path(f"data/{filename}"))

    # Act
    result, _ = validate_upload_format(df)

    # Assertk
    assert result == expected


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("input_successful.xlsx", True),
        ("input_empty_metadata.xlsx", False),
        ("input_errors_in_metadata.xlsx", False),
    ],
)
def test_validate_meta_attributes(filename, expected):
    # Arrange
    df = pd.read_excel(get_testfile_path(f"data/{filename}"))

    # Act
    result, _ = validate_meta_attributes(df)

    # Assert
    assert result == expected


def test_split_metadata_data():
    # Arrange
    df = pd.read_excel(get_testfile_path(f"data/input_successful.xlsx"))

    # Act
    metadata_df, data_df = split_metadata_data(df)

    # Assert
    assert "M1" not in data_df.index
    assert "1" not in metadata_df.index
