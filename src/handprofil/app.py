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
)
def file_uploaded_callback(upload_contents, upload_filenames, upload_dates):
    # Inputs
    if upload_contents is None:
        return no_update, no_update, no_update

    result, metadata, data, alert = excelparser.parse_and_validate_uploads(
        upload_contents, upload_filenames, upload_dates
    )

    if not result:
        return [], [], alert

    subject_grid = plotting.return_subject_grid(metadata, "switch-subject")

    # Select Background with default settings
    bin_edges = calculations.get_bin_edges("gemischt", "m", "right", background)
    measurements_to_bins = calculations.measurements_to_bins(data, bin_edges)

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

    # Outputs
    return all_plots_children, subject_grid, []


# @callback(
#     Output("all_plots", "children"),
#     Input("radiogroup-hand", "value"),
#     Input("radiogroup-sex", "value"),
#     Input("select-instrument", "value"),
# )
# def selectors_updated_callback(hand, sex, instrument):
#     return None


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
