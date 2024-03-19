import pandas as pd
import pytest
from calculations import (
    return_wagner_decile,
    get_bin_edges,
    measurements_to_bins,
)
import common


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


def test_get_bin_edges():
    # Arrange
    background = common.load_background()

    # Act
    df = get_bin_edges("violine", "m", "left", background)

    # Assert
    assert len(df.columns) == 9


def test_get_calculated_values():
    ids = [101, 103]
    values = [197.0, 43.0]
    input_series = pd.Series(values, index=ids, name="measurement")

    background = common.load_background()
    bin_edges = get_bin_edges("violine", "m", "left", background)

    result = measurements_to_bins(input_series, bin_edges)

    assert result.index.values[0] == 101
    assert result.index.values[1] == 103
    assert result.values[0] == 17
    assert result.values[1] == 4


def test_get_calculated_values_if_index_not_in_background():
    ids = [500]
    values = [1.0]
    input_series = pd.Series(values, index=ids, name="measurement")

    background = common.load_background()
    bin_edges = get_bin_edges("violine", "m", "left", background)

    result = measurements_to_bins(input_series, bin_edges)

    assert result.empty == True
