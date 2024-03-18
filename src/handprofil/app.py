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
        common.get_absolute_path("src/handprofil/config/plot_sections.json"), "r"
    ) as file:
        sections = json.load(file)
    return sections


# Path
print(os.getenv("DEBUG", "NONE"))
print(os.getcwd())

# Get data
attributes = common.load_attributes()
background = common.load_background()
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
app.layout = plotting.get_layout()


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
    upload_contents, upload_filenames, upload_dates, hand, sex, instrument
):
    # Inputs
    if upload_contents is None:
        return no_update, no_update, no_update

    result, metadata, data, alert = excelparser.parse_and_validate_uploads(
        upload_contents, upload_filenames, upload_dates
    )

    if not result:
        return [], [], alert

    subject_grid = plotting.return_subject_grid(metadata, "switch-subject")
    bin_values = calculations.get_calculated_values(data, instrument, sex, hand)
    decile_plot_df = plotting.return_decile_plot_df(bin_values)

    # Order by sections
    all_plots_children = []
    for section in sections:
        df = decile_plot_df.copy()

        valid_indices = [index for index in section["index_order"] if index in df.index]

        if len(valid_indices) > 0:
            df = df.loc[valid_indices, :].reset_index()
            figure = plotting.return_section_figure(df)
            child = plotting.wrap_figure_in_graph(section["title"], figure)
            all_plots_children.append(child)

    # Outputs
    return all_plots_children, subject_grid, []


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


# Run the App
if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run(debug=True)
