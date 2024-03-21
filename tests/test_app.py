import base64
import os
import pytest
import pandas as pd
from handprofil.app import (
    return_wagner_decile,
    get_bin_edges,
    measurements_to_bins,
    load_static_data,
    compute_plot_input_from_store,
    upload_files_to_store
)
from handprofil.utils import (
    load_background
)


def get_testfile_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory_path, relative_path)


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
    background = load_background()

    # Act
    df = get_bin_edges("violine", "m", "left", background)

    # Assert
    assert len(df.columns) == 9


def test_get_calculated_values():
    ids = [101, 103]
    values = [197, 43]
    input_series = pd.Series(values, index=ids, name="measurement")

    background = load_background()
    bin_edges = get_bin_edges("violine", "m", "left", background)

    result = measurements_to_bins(input_series, bin_edges)

    assert result.index.values[0] == 101
    assert result.index.values[1] == 103
    assert result.values[0] == 17
    assert result.values[1] == 4


def test_get_calculated_values_if_index_not_in_background():
    ids = [500]
    values = [1]
    input_series = pd.Series(values, index=ids, name="measurement")

    background = load_background()
    bin_edges = get_bin_edges("violine", "m", "left", background)

    result = measurements_to_bins(input_series, bin_edges)

    assert result.empty == True


def test_load_static_data():
    # Arrange

    # Act
    result = load_static_data("dummy")

    # Assert
    assert len(result) == 3


@pytest.mark.parametrize(
    "upload_path, sex, instrument, checkbox_background_hand, checkbox_show_all_measures",
    [("data/measurement_template_filled.xlsx", "m", "violine", True, True)],
)
def test_compute_plot_input_from_store(
    upload_path, sex, instrument, checkbox_background_hand, checkbox_show_all_measures
):
    # Arrange
    # Upload data
    path = get_testfile_path(upload_path)
    with open(path, 'rb') as data:
        content = "xslx," + base64.b64encode(data.read()).decode('UTF-8')
    contents = [content, content]
    upload_store, _, errors = upload_files_to_store(contents, {})

    # Static data
    static_store = load_static_data("dummy")

    # Hands shown
    hands_shown_values = [["left", "right"], ["left"]]
    hands_shown_ids = list(upload_store.keys())

    # Act
    compute_plot_input_from_store(
        upload_store,
        sex,
        instrument,
        checkbox_background_hand,
        checkbox_show_all_measures,
        hands_shown_values,
        hands_shown_ids,
        static_store,
    )

    # Assert
    assert True

    # dict: per id
    #     | left | right
    # id1 |  12  |  NaN
    # id2 |  3   |  4
    # id3 |  5   |  6
