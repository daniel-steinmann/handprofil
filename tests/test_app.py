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
    compute_binned_values,
    upload_files_to_store,
    get_plot_input_data,
    create_plots
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


@pytest.mark.parametrize(
    "checkbox_background_hand",
    [(True), (False)],
)
def test_compute_binned_values(
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
    result = compute_binned_values(
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


def test_compute_plot_input_data():
    # Arrange
    # TODO: Test with empty
    decile_data_store = [
        {
            "id": {
                "0": 1,
                "1": 1,
            },
            "hand": {
                "0": "left",
                "1": "right",
            },
            "value": {
                "0": 12,
                "1": 14,
            }
        },
        {
            "id": {
                "0": 1,
                "1": 1,
            },
            "hand": {
                "0": "left",
                "1": "right",
            },
            "value": {
                "0": 7,
                "1": 15,
            }
        }
    ]
    decile_data_store = [
        pd.DataFrame.from_dict(item).to_json() for item in decile_data_store
    ]

    static_store = {
        "measure_labels": {
            "id": {
                "0": 1,
                "1": 2,
                "2": 3,
            },
            "device": {
                "0": "Handlabor",
                "1": "Handlabor",
                "2": "Handlabor",
            },
            "description": {
                "0": "Handlänge",
                "1": "Handbreite",
                "2": "Handindex 2:1",
            },
            "unit": {
                "0": "mm",
                "1": "mm",
                "2": "keine",
            }
        }
    }

    hands_shown_values = [["right", "left"], ["right"]]
    hands_shown_ids = [1, 2]

    # Act
    results = get_plot_input_data(
        decile_data_store, hands_shown_values, hands_shown_ids, static_store
    )

    # Assert
    dataframes = [
        pd.DataFrame.from_dict(item) for item in results
    ]

    for df in dataframes:
        assert 'id' in df.columns
        assert 'hand' in df.columns
        assert 'value' in df.columns
        assert 'device' in df.columns
        assert 'description' in df.columns
        assert 'unit' in df.columns
        assert len(df.columns) == 6

    assert dataframes[0].set_index(
        ["id", "hand"]).loc[(1, "right"), "value"] == 14
    assert dataframes[0].set_index(
        ["id", "hand"]).loc[(1, "left"), "value"] == 12
    assert dataframes[1].set_index(
        ["id", "hand"]).loc[(1, "right"), "value"] == 15


def test_create_plots():
    # Arrange
    static_store = {
        "section_config":
            [
                {
                    "title": "Handform",
                    "index_order": [2, 1]
                },
                {
                    "title": "Aktive Beweglichkeit",
                    "index_order": [
                        3
                    ]
                },
            ]
    }

    plot_data_store = [{
        "id": {
            "0": 1,
            "1": 2,
            "2": 3,
            "3": 1,
            "4": 2,
            "5": 3
        },
        "hand": {
            "0": "right",
            "1": "right",
            "2": "right",
            "3": "left",
            "4": "left",
            "5": "left"
        },
        "value": {
            "0": 14,
            "1": 2,
            "2": 2,
            "3": 12,
            "4": 4,
            "5": 10
        },
        "device": {
            "0": "Handlabor",
            "1": "Handlabor",
            "2": "Handlabor",
            "3": "Handlabor",
            "4": "Handlabor",
            "5": "Handlabor"
        },
        "description": {
            "0": "Handlänge",
            "1": "Handbreite",
            "2": "Fingerlänge",
            "3": "Handlänge",
            "4": "Handbreite",
            "5": "Fingerlänge"
        },
        "unit": {
            "0": "mm",
            "1": "mm",
            "2": "mm",
            "3": "mm",
            "4": "mm",
            "5": "mm"
        }
    },
        {
        "id": {
            "0": 1,
            "1": 2,
            "2": 1,
            "3": 2
        },
        "hand": {
            "0": "right",
            "1": "right",
            "2": "left",
            "3": "left"
        },
        "value": {
            "0": 2,
            "1": 10,
            "2": 3,
            "3": 6
        },
        "device": {
            "0": "Handlabor",
            "1": "Handlabor",
            "2": "Handlabor",
            "3": "Handlabor"
        },
        "description": {
            "0": "Handlänge",
            "1": "Handbreite",
            "2": "Handlänge",
            "3": "Handbreite"
        },
        "unit": {
            "0": "mm",
            "1": "mm",
            "2": "mm",
            "3": "mm"
        }
    }]

    # Act
    result = create_plots(plot_data_store, static_store)

    # Assert
    x = result
