import pandas as pd
import pytest
from calculations import (
    return_wagner_decile,
    get_bin_edges,
    get_calculated_values,
)


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


def test_get_filtered_background():
    df = get_bin_edges("violine", "m", "left")
    assert len(df.columns) == 9


def test_get_calculated_values():
    ids = [101, 103]
    values = [197, 43]
    input_series = pd.Series(values, index=ids, name="measurement")

    result = get_calculated_values(input_series, "violine", "m", "left")

    assert result.index.values[0] == 101
    assert result.index.values[1] == 103
    assert result.values[0] == 17
    assert result.values[1] == 4


def test_get_calculated_values_if_index_not_in_background():
    ids = [500]
    values = [1]
    input_series = pd.Series(values, index=ids, name="measurement")

    result = get_calculated_values(input_series, "violine", "m", "left")

    assert result.empty == True
