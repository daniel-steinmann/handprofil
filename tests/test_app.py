import base64
import os
import pytest
import pandas as pd
from handprofil.app import (
    return_wagner_decile,
    load_static_data,
    compute_binned_values,
    get_plot_input_data,
    create_plots,
    upload_files_to_store,
    parse_contents
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


def test_parse_contents():
    filename = "measurement_template_filled.xlsx"
    content_type = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64'
    path = get_testfile_path(f"data/{filename}")
    data = open(path, 'rb').read()
    base64_encoded = base64.b64encode(data).decode('UTF-8')

    content = content_type + ',' + base64_encoded

    is_success, result = parse_contents(content, filename)

    assert result['info']['value'][0] == 'TM24'
    assert result['data']['left'][0] == 194.0


@pytest.mark.parametrize(
    "checkbox_background_hand, instrument, sex",
    [(True, "violine", "m"), (False, "violine", "w"),
     (False, "schlagzeug", "w"), (False, "schlagzeug", "m")]
)
def test_compute_binned_values(
    checkbox_background_hand,
    instrument,
    sex
):
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
        pd.DataFrame.from_dict(df).set_index(["id", "hand"]) for df in result
    ]

    # First parametrized test
    if instrument == 'violine' and sex == 'm':
        assert result_dfs[0].loc[(1, "left")].value == 3

        if checkbox_background_hand:
            assert result_dfs[0].loc[(1, "right")].value == 4
        else:
            # Right hand value should not be part of result
            # if values were not imputed
            assert ((1, "right") in list(result_dfs[0].index)) == False


@pytest.mark.parametrize(
    "no_data",
    [(False), (True)]
)
def test_compute_plot_input_data(no_data):
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

    if no_data:
        decile_data_store = [
            {
                "id": {},
                "hand": {},
                "value": {}
            },
            {
                "id": {},
                "hand": {},
                "value": {}
            }
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
        decile_data_store, hands_shown_values, static_store
    )

    # Assert
    dataframes = [
        pd.DataFrame.from_dict(item) for item in results
    ]

    if not no_data:
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


@pytest.mark.parametrize(
    "no_data",
    [(False), (True)]
)
def test_create_plots(no_data):
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
        },
    },
        {
            "id": {},
            "hand": {},
            "value": {},
            "device": {},
            "description": {},
            "unit": {}
    }]

    if no_data:
        plot_data_store = [{
            "id": {},
            "hand": {},
            "value": {},
            "device": {},
            "description": {},
            "unit": {}
        },
            {
            "id": {},
            "hand": {},
            "value": {},
            "device": {},
            "description": {},
            "unit": {}
        }]

    # Act
    result = create_plots(plot_data_store, static_store)

    # Assert
    x = result


def get_testfile_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory_path, relative_path)


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("measurement_template_filled.xlsx", True),
    ],
)
def test_validate_meta_attributes(filename, expected):
    # Arrange
    path = get_testfile_path(f"data/{filename}")
    content_type = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64'

    with open(path, 'rb') as data:
        content = content_type + ',' + \
            base64.b64encode(data.read()).decode('UTF-8')

    contents = [content, content]

    # Act
    data, _, _ = upload_files_to_store(contents, [filename, filename], {})

    # Assert
    pd.DataFrame.from_dict({})
    assert len(data) == 2
    first_content = data[0]
    info = pd.DataFrame.from_dict(first_content['info'])
    data = pd.DataFrame.from_dict(first_content['data'])
