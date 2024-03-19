# Import packages
from dash import Dash, html, dcc, callback, Output, Input, State, no_update
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import plotly.graph_objects as go
import json
import os
from flask import send_file

import calculations
import excelparser
import plotting
import common


def load_plot_section_config():
    with open(
        common.get_absolute_path(
            "src/handprofil/config/plot_sections.json"), "r"
    ) as file:
        sections = json.load(file)
    return sections


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
attributes = common.load_attributes()
background = common.load_background()
sections = load_plot_section_config()

input_df = pd.read_excel(common.get_absolute_path(
    "tests/data/input_successful.xlsx"))

validation_result, alert = excelparser.validate_upload(input_df)
metadata, data_df = excelparser.split_metadata_data(input_df)

subject_grid = plotting.return_subject_grid(metadata, "switch-subject")

# Select Background with default settings
bin_edges = calculations.get_bin_edges(
    "gemischt", "m", "right", background)
measurements_to_bins = calculations.measurements_to_bins(data_df, bin_edges)

# Get Attributes for plot
decile_plot_df = plotting.join_attributes_to_measurements(
    measurements_to_bins, attributes
)

# Create plots in sections
plot_df_section_list = plotting.split_reorder_plot_df_to_sections(
    decile_plot_df, sections
)

all_plots_children = []
for index, section in enumerate(sections):
    figure = plotting.return_section_figure(plot_df_section_list[index])
    child = plotting.wrap_figure_in_graph(section["title"], figure)
    all_plots_children.append(child)

#######################
####### Layout ########
#######################

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
            children=html.Div(
                ["Drag and Drop or ", html.A("Select Files")]),
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
        dmc.Grid(subject_grid, id="subject-grid"),
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
                                    ],
                                    style={"width": 200,
                                           "marginBottom": 10},
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
        html.Div(id="all_plots", children=all_plots_children),
    ],
    fluid=True,
)

#######################
##### Callbacks #######
#######################


@app.server.route("/download/")
def download_excel():
    return send_file(common.get_absolute_path("download/measurement_template.xlsx"))


@callback(
    Output("download-xlsx", "data"),
    Input("btn_image", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file(common.get_absolute_path("download/measurement_template.xlsx"))


#######################
####### Main ##########
#######################
# Run the App
if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run(debug=True)
