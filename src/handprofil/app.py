
###################
### Imports ######
###################

from dash import Dash, html, dcc, callback, Output, Input, State, ALL, MATCH
import pandas as pd
import dash_mantine_components as dmc
import os
from flask import send_file
from dash.exceptions import PreventUpdate
import uuid
from dash_iconify import DashIconify

import uploadparser
import utils
import frontend

###################
# Constants #
###################

plot_style_data = [
    {"value": "decile", "label": "Dezile"}
]

instrument_data = [
    {"value": "violine",
     "label": "Violine"},
    {
        "value": "violoncello",
        "label": "Violoncello",
    },
    {
        "value": "schlagzeug",
        "label": "Schlagzeug",
    },
    {"value": "klavier",
     "label": "Klavier"},
    {"value": "gitarre",
     "label": "Gitarre"},
    {"value": "egitarre",
     "label": "E-Gitarre"},
    {
        "value": "akkordeon",
        "label": "Akkordeon",
    },
    {"value": "gemischt",
     "label": "Gemischt"},
]

sex_data = [
    ["m", "Männlich"],
    ["w", "Weiblich"],
]

###################
### Styles ########
###################

container_style = {
    "border": f"1px solid black",
    "borderRadius": 8,
    "padding": 20,
    "marginTop": 20,
    "marginBottom": 20,
}

###################
# Methods #
###################


def get_bin_edges(
    instrument: str, sex: str, hand: str, background: pd.DataFrame
) -> pd.DataFrame:

    assert instrument in background["instrument"].unique()
    assert hand in background["hand"].unique()
    assert sex in background["sex"].unique()

    background_filtered = background.query(
        "instrument == @instrument & sex == @sex & hand == @hand"
    ).set_index("id", drop=True)

    bin_edges = background_filtered[
        [
            "bin_edge_1",
            "bin_edge_2",
            "bin_edge_3",
            "bin_edge_4",
            "bin_edge_5",
            "bin_edge_6",
            "bin_edge_7",
            "bin_edge_8",
            "bin_edge_9",
        ]
    ]

    return bin_edges


def measurements_to_bins(
    measurements_schema: pd.Series,
    bin_edges: pd.DataFrame,
) -> pd.Series:

    output = pd.Series(dtype=pd.Int64Dtype)
    for index, measurement in measurements_schema.items():
        if index in bin_edges.index:
            bin = return_wagner_decile(bin_edges.loc[index], measurement)
            output.loc[index] = bin

    return output


def return_wagner_decile(bin_edges: list, value: float) -> int:
    """Return custom decile bin.

    Returns bin position of value with respect to
    bin_edges. If value is equal to one of the bin
    edges, this is also a bin. Below the mapping between
    bins and edges (with monospace font):
    Edges:   1   2   3   4   5     6     7     8     9
    Bins:  1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
    """
    #   1   2   3   4   5     6     7     8     9
    # 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19

    assert len(bin_edges) == 9

    bin = 1
    for i, edge in enumerate(bin_edges):
        if value < edge:
            break
        if value == edge:
            bin = bin + 1
            break
        else:
            bin = bin + 2
    return bin

###################
###### Dash #######
###################


# Path
print(os.getenv("DEBUG", "NONE"))
print(os.getcwd())

# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

###################
# Data Processing #
###################

attributes = utils.load_attributes()
background = utils.load_background()
section_config = utils.load_plot_section_config()

input_df = pd.read_excel(utils.get_absolute_path(
    "tests/data/input_successful.xlsx"))

validation_result, alert = uploadparser.validate_upload(input_df)
metadata, data_df = uploadparser.split_metadata_data(input_df)

bin_edges = get_bin_edges(
    "gemischt", "m", "right", background)
binned_measurements = measurements_to_bins(data_df, bin_edges)

####################################
### Create Dynamic Plot Elements ###
####################################

# Subject Grid
subject_grid = frontend.return_subject_grid(metadata, "switch-subject")

# Measurement Plots
plot_sections = frontend.get_plot_sections(
    binned_measurements, attributes, section_config)

#######################
####### Layout ########
#######################

# App layout
app.layout = dmc.Container(
    [
        dmc.Header(height=60, children=[dmc.Center(
            dmc.Title("Handlabor", order=1))]),
        dmc.Container(
            style=container_style,
            children=[
                dmc.SimpleGrid(
                    cols=3,
                    children=[
                        dcc.Upload(
                            id="upload-data",
                            children=dmc.Button('Datei hochladen'),
                            multiple=True,
                        ),
                        html.Div(
                            [
                                dmc.Button("Vorlage herunterladen (.xlsx)",
                                           id="btn_image"),
                                dcc.Download(id="download-xlsx"),
                            ]
                        ),
                        dmc.Button("Druckansicht",
                                   id="btn_printview")
                    ])
            ]
        ),
        dmc.Container(
            style=container_style,
            children=[
                dmc.Center(
                    children=[
                        dmc.Select(
                            label="Darstellung",
                            searchable=True,
                            placeholder="Select one",
                            id="select-plotstyle",
                            value="decile",
                            data=plot_style_data,
                            style={"width": 200,
                                   "marginBottom": 10},
                        )
                    ]
                )
            ]
        ),
        dmc.Container(
            style=container_style,
            children=[
                dcc.Store(id='store', storage_type='memory'),
                dmc.Title(dmc.Text("Uploads Debugger"), order=2),
                dmc.Container(id="upload-debug-container"),
            ]),
        dmc.Container(
            style=container_style,
            children=[
                dmc.Title(dmc.Text("Uploads"), order=2),
                dmc.Container(id="upload-alerts"),
                subject_grid
            ]),
        dmc.Container(
            style=container_style,
            children=[
                dmc.Title("Vergleichsgruppe (Hintergrund)", order=2),
                dmc.SimpleGrid(
                    cols=3,
                    children=[
                        dmc.RadioGroup(
                            [
                                dmc.Radio(l, value=k)
                                for k, l in sex_data
                            ],
                            id="radiogroup-sex",
                            value="m",
                            label="Geschlecht",
                            size="sm",
                            mt=10,
                        ),
                        dmc.Select(
                            label="Instrument",
                            searchable=True,
                            placeholder="Select one",
                            id="select-instrument",
                            value="gemischt",
                            data=instrument_data,
                            style={"width": 200,
                                   "marginBottom": 10},
                        )
                    ])
            ]
        ),
        dmc.Container(id="all_plots", style=container_style,
                      children=plot_sections)
    ],
    fluid=True,
)

#######################
##### Callbacks #######
#######################


@callback(
    Output('store', 'data', allow_duplicate=True),
    # Workaround for https://github.com/plotly/dash-core-components/issues/816
    Output('upload-data', 'contents'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
    State('store', 'data'),
    prevent_initial_call=True,
)
def upload_files_to_store(list_of_contents, list_of_names, list_of_dates, store_state):
    if list_of_contents is None:
        raise PreventUpdate

    dataframes = [
        uploadparser.parse_contents(c, n, d) for c, n, d in
        zip(list_of_contents, list_of_names, list_of_dates)]

    new_items = {
        str(uuid.uuid4()): df.to_dict() for df in dataframes
    }

    export = store_state | new_items if store_state else new_items
    return export, None


@callback(
    Output('upload-debug-container', 'children'),
    Input('store', 'data'),
    prevent_initial_call=True,
)
def process_uploaded(data: dict):
    return [dmc.Container([
        html.Div(f"File-UUID: {id} "),
        dmc.ActionIcon(
            DashIconify(icon="mdi:trash", width=20),
            size="lg",
            variant="filled",
            id={"type": "delete-file-button", "index": id},
            n_clicks=0,
            mb=10,
        )]) for id, value in data.items()]


@callback(
    Output('store', 'data', allow_duplicate=True),
    Input({"type": "delete-file-button", "index": ALL}, "n_clicks"),
    State({"type": "delete-file-button", "index": ALL}, "id"),
    State('store', 'data'),
    prevent_initial_call=True,
)
def delete_file_from_store(n_clicks, id: dict, data: dict):
    for i, clicks in enumerate(n_clicks):
        if clicks > 0:
            data.pop(id[i]['index'])
            return data
    return data


@callback(
    Output("download-xlsx", "data"),
    Input("btn_image", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file(utils.get_absolute_path("src/handprofil/download/measurement_template.xlsx"))


#######################
####### Main ##########
#######################
# Run the App
if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run(debug=True)
