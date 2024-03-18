# Import packages
from dash import Dash, html, dcc, callback, Output, Input, State, no_update
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import plotly.graph_objects as go
import json
import os
from flask import send_file

from calculations import get_calculated_values
from excelparser import parse_contents, validate_upload, split_metadata_data
from plotting import return_figure
from common import (
    get_absolute_path,
    load_meta_attributes,
    load_attributes,
    load_background,
)


def load_plot_section_config():
    with open(
        get_absolute_path("src/handprofil/config/plot_sections.json"), "r"
    ) as file:
        sections = json.load(file)
    return sections

# Path
print(os.getenv("DEBUG", "NONE"))
print(os.getcwd())

# Debug mode without manual uploads
DEBUG_MODE = False
if DEBUG_MODE:
    debug_df = pd.read_excel("excel_prototypes/measurement.xlsx")

# Get data
attributes = load_attributes()
meta_attributes = load_meta_attributes()
background = load_background()
sections = load_plot_section_config()

# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

initial_df = pd.DataFrame(
    {
        "id": 1,
        "device": "Handlabor",
        "hand": "Rechts",
        "description": "Handlänge",
        "unit": "mm",
        "bin": 1,
    },
    index=[0],
)

# App layout
app.layout = dmc.Container(
    [
        dmc.Title("Handlabor"),
        html.Div(
            [
                dmc.Button("Download Template (.xlsx)", id="btn_image"),
                dcc.Download(id="download-xlsx"),
            ]
        ),
        dmc.Title("Upload", order=2),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
        ),
        dmc.Container(id="upload-alerts"),
        dmc.Title("Datensätze", order=2),
        dmc.Grid(id="subject-grid"),
        dmc.Grid(
            [
                dmc.Col(
                    [
                        dmc.Card(
                            children=[
                                dmc.Title("Hintergrund", order=2),
                                dmc.RadioGroup(
                                    [
                                        dmc.Radio(l, value=k)
                                        for k, l in [
                                            ["m", "Männlich"],
                                            ["w", "Weiblich"],
                                        ]
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
                                    data=[
                                        {"value": "violine", "label": "Violine"},
                                        {
                                            "value": "violoncello",
                                            "label": "Violoncello",
                                        },
                                        {"value": "schlagzeug", "label": "Schlagzeug"},
                                        {"value": "klavier", "label": "Klavier"},
                                        {"value": "gitarre", "label": "Gitarre"},
                                        {"value": "egitarre", "label": "E-Gitarre"},
                                        {"value": "akkordeon", "label": "Akkordeon"},
                                        {"value": "gemischt", "label": "Gemischt"},
                                    ],
                                    style={"width": 200, "marginBottom": 10},
                                ),
                            ]
                        ),
                    ],
                    span="auto",
                ),
                dmc.Col(
                    [
                        dmc.Card(
                            children=[
                                dmc.Title("Hand", order=2),
                                dmc.RadioGroup(
                                    [
                                        dmc.Radio(l, value=k)
                                        for k, l in [
                                            ["right", "Rechts"],
                                            ["left", "Links"],
                                        ]
                                    ],
                                    id="radiogroup-hand",
                                    value="right",
                                    label="Hand",
                                    size="sm",
                                    mt=10,
                                ),
                            ]
                        ),
                    ],
                    span="auto",
                ),
            ]
        ),
        html.Div(id="all_plots"),
    ],
    fluid=True,
)


@callback(
    Output("all_plots", "children"),
    Output("subject-grid", "children"),
    Output("upload-alerts", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
    Input("radiogroup-hand", "value"),
    Input("radiogroup-sex", "value"),
    Input("select-instrument", "value"),
)
def display_graph(
    list_of_contents, list_of_names, list_of_dates, hand, sex, instrument
):
    # Inputs
    all_plots_children = []
    subject_grid = []
    upload_alerts = []
    if list_of_contents is None:
        return no_update, no_update, no_update

    if DEBUG_MODE:
        children = [debug_df]
    else:
        children = [
            parse_contents(c, n, d)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]

    # Get Uploaded Data (Only First Item) or load sample data
    input_df = children[0]
    result, alert = validate_upload(input_df)
    if result is False:
        upload_alerts.append(alert)
        return [], [], upload_alerts

    metadata, data_df = split_metadata_data(input_df)

    subject_grid = [
        dmc.Col(
            [
                dmc.Text(f"ID: {metadata.loc['M1','value']}"),
                dmc.Text(f"Datum: {metadata.loc['M2','value'].strftime('%d.%m.%Y')}"),
                dmc.Text(f"Name: {metadata.loc['M3','value']}"),
                dmc.Text(f"Vorname: {metadata.loc['M4','value']}"),
            ],
            span="auto",
        ),
        dmc.Col(
            [
                dmc.Text(
                    f"Geburtsdatum: {metadata.loc['M5','value'].strftime('%d.%m.%Y')}"
                ),
                dmc.Text(f"Geschlecht: {metadata.loc['M6','value']}"),
                dmc.Text(f"Händigkeit: {metadata.loc['M7','value']}"),
                dmc.Text(f"Instrument: {metadata.loc['M8','value']}"),
            ],
            span="auto",
        ),
        dmc.Switch(id="switch-subject"),
    ]

    bin_values = get_calculated_values(data_df["value"], instrument, sex, hand)
    bin_values.name = "bin"

    decile_plot_df = pd.merge(
        attributes,
        bin_values,
        "inner",
        left_on="id",
        right_index=True,
    )

    # Order by sections
    all_plots_children = []
    for section in sections:
        df = decile_plot_df.copy()

        valid_indices = [index for index in section["index_order"] if index in df.index]

        if len(valid_indices) > 0:
            df = df.loc[valid_indices, :].reset_index()
            child = html.Div(
                [
                    dmc.Title(f"{section['title']}", order=2),
                    dcc.Graph(
                        id="_wait_time_graph",
                        style={"height": "100%", "width": "100%"},
                        className="wait_time_graph",
                        config={
                            "staticPlot": False,
                            "editable": False,
                            "displayModeBar": False,
                        },
                        figure=return_figure(df),
                    ),
                ]
            )
            all_plots_children.append(child)

    # Outputs
    return all_plots_children, subject_grid, upload_alerts


@app.server.route("/download/")
def download_excel():
    return send_file(get_absolute_path("download/measurement_template.xlsx"))


@callback(
    Output("download-xlsx", "data"),
    Input("btn_image", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file(get_absolute_path("download/measurement_template.xlsx"))


# Run the App
if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run(debug=True)
