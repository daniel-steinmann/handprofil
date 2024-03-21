import base64
from io import StringIO
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


def test_load_static_data():
    # Arrange

    # Act
    result = load_static_data("dummy")

    # Assert
    assert len(result) == 3


@pytest.mark.parametrize(
    "checkbox_background_hand",
    [(True), (False)],
)
def test_compute_plot_input_from_store(
    checkbox_background_hand
):
    # background_choice
    sex = "m"
    instrument = "violine"

    # There is no background for id=8
    upload_store = [
        {
            "data": {
                "id": {0: 1, 1: 8},
                "device": {0: "dummy", 1: "dummy"},
                "description": {0: "dummy", 1: "dummy"},
                "left": {0: 178.0, 1: 94.0},
                "right": {0: 181.0, 1: 95.0}
            }
        },
        {
            "data": {
                "id": {0: 1, 1: 8},
                "device": {0: "dummy", 1: "dummy"},
                "description": {0: "dummy", 1: "dummy"},
                "left": {0: 178.0, 1: 94.0},
                "right": {0: 181.0, 1: 95.0}
            }
        }
    ]

    static_store = {
        "background_data": {
            "instrument": {0: "violine", 1: "violine", 2: "egitarre"},
            "sex": {0: "m", 1: "m", 2: "m"},
            "hand": {0: "left", 1: "left", 2: "right"},
            "id": {0: 1, 1: 1, 2: 1},
            "bin_edge": {0: 1, 1: 2, 2: 1},
            "value": {0: 177.0, 1: 181.0, 2: 160}
        }
    }

    # Act
    result = compute_plot_input_from_store(
        upload_store,
        sex,
        instrument,
        checkbox_background_hand,
        # hands_shown_values,
        # hands_shown_ids,
        static_store,
    )

    # Assert
    result_dfs = [
        pd.read_json(StringIO(df)).set_index(["id", "hand"]) for df in result
    ]

    assert result_dfs[0].loc[(1, "left")].value == 3

    if checkbox_background_hand:
        assert result_dfs[0].loc[(1, "right")].value == 4
    else:
        # Right hand value should not be part of result
        # if values were not imputed
        assert ((1, "right") in list(result_dfs[0].index)) == False
