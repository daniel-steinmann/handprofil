# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State, no_update

from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import plotly.graph_objects as go
import base64
import datetime as dt
import io
import json
import numpy as np
import os
from flask import send_file


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


def summation(num1: int, num2: int) -> int:
    """
    Calculate the summation of two number
    """
    return num1 + num2


def return_trace(df: pd.DataFrame, color="black"):
    return go.Scatter(
        x=df.bin,
        y=df.index,
        marker=dict(size=16, color=color),
        mode="lines+markers",
        line=dict(dash="solid", width=2, color=color),
        connectgaps=True,
    )

    return dcc.Graph(
        id="_wait_time_graph",
        style={"height": "100%", "width": "100%"},
        className="wait_time_graph",
        config={
            "staticPlot": False,
            "editable": False,
            "displayModeBar": False,
        },
        figure=figure,
    )


def return_figure(df: pd.DataFrame):
    """Return figure and add trace.

    Dataframe columns:
    id: int
    device: string
    hand: string
    description: string
    unit: string
    bin: string
    """

    input_schema = pd.DataFrame(
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

    assert df.dtypes.equals(input_schema.dtypes)

    labelmargin = 200

    fig = px.scatter()
    ticktext = return_ticktext(df)

    fig.update_layout(
        width=1000,
        height=30 * len(ticktext) + 50,
        xaxis=dict(
            constrain="domain",
            gridcolor="black",
            linecolor="black",
            linewidth=2,
            minor=dict(dtick="L1", tick0="-0.5", gridcolor="black"),
            mirror=False,
            range=[0.5, 19.5],
            showgrid=False,
            showline=False,
            showticklabels=True,
            tickfont=dict(family="Arial", color="black", size=14),
            ticks="outside",
            tickvals=[2, 4, 6, 8, 10, 12, 14, 16, 18],
            ticktext=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
            title="Dezil",
            zeroline=False,
        ),
        yaxis=dict(
            anchor="free",
            constrain="domain",
            gridcolor="black",
            minor=dict(dtick="L1", tick0="-0.5", gridcolor="black"),
            mirror=True,
            range=[len(ticktext) - 0.5, -0.5],
            scaleanchor="x",
            scaleratio=1,
            shift=-200,
            showgrid=False,
            showline=True,
            showticklabels=True,
            side="right",
            title=None,
            zeroline=False,
        ),
        autosize=False,
        margin=dict(autoexpand=False, l=labelmargin, r=0, t=0, b=50),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    fig.add_shape(
        # Rectangle with reference to the plot
        type="rect",
        xref="x domain",
        yref="y domain",
        x0=0,
        y0=0,
        x1=1.0,
        y1=1.0,
        line=dict(
            color="black",
            width=1,
        ),
    )

    fig.update_layout(
        yaxis=dict(
            tickfont=dict(family="Arial", color="black", size=14),
            tickmode="array",
            ticktext=ticktext,
            tickvals=ticktext.index,
        )
    )

    fig.add_trace(return_trace(df))

    return fig


def return_ticktext(plot_df):
    return plot_df.apply(
        lambda x: f"{f'{x.id},':<5} {x.description} ({x.unit})", axis=1
    )


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")), sep="|", index_col=False
            )
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(
                io.BytesIO(decoded),
            )
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return df


def get_absolute_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory_path, relative_path)


def upload_is_valid(df) -> dmc.Alert:
    # Necessary Assertions
    # 1. Correct Input Format (All required indices must be present in id - column)
    # 2. At least one value field must have a value
    attributes = pd.read_csv(
        get_absolute_path("tables/attributes.csv"), header=0, index_col=False
    )
    meta_attributes = pd.read_csv(
        get_absolute_path("tables/meta_attributes.csv"), header=0, index_col=False
    )

    validation_set = set(
        np.concatenate([attributes.id.values, meta_attributes.id.values])
    )

    upload_set = set(df.id.values)

    missing = validation_set.difference(upload_set)
    unknown = upload_set.difference(validation_set)

    alert = dmc.Alert(title="Validation error", color="red")

    if missing and unknown:
        msg = f"Missing IDs: {missing}, Unknown IDs: {unknown}"
        alert.children = msg
        return False, alert

    if missing:
        msg = f"Missing IDs: {missing}"
        alert.children = msg
        return False, alert

    if unknown:
        msg = f"Unknown IDs: {unknown}"
        alert.children = msg
        return False, alert

    if df.value.isna().all():
        msg = f"No values found"
        alert.children = msg
        return False, alert

    return True, None


# Path
print(os.getenv("DEBUG", "NONE"))
print(os.getcwd())

# Debug mode without manual uploads
DEBUG_MODE = False
if DEBUG_MODE:
    debug_df = pd.read_excel("excel_prototypes/measurement.xlsx")

# Get data
attributes = pd.read_csv(
    get_absolute_path("tables/attributes.csv"), header=0, index_col=False
)
attributes = attributes.set_index("id", drop=True)
meta_attributes = pd.read_csv(
    get_absolute_path("tables/meta_attributes.csv"), header=0, index_col=False
)
meta_attributes = meta_attributes.set_index("id", drop=True)
background = pd.read_csv(get_absolute_path("tables/background.csv"), index_col=0)
with open(get_absolute_path("config/plot_sections.json"), "r") as file:
    sections = json.load(file)

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
    result, alert = upload_is_valid(input_df)
    if result is False:
        upload_alerts.append(alert)
        return [], [], upload_alerts

    input_df = input_df.set_index("id", drop=True)

    # Get Metadata
    metadata = pd.merge(
        meta_attributes, input_df["value"], "inner", left_on="id", right_on="id"
    )

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

    # Get background
    background_filtered = background.query(
        "instrument == @instrument & sex == @sex & hand == @hand"
    )

    # Merge measurements and background
    merged_values = pd.merge(
        background_filtered, input_df["value"], "inner", left_on="id", right_on="id"
    )

    # Apply binning
    merged_values["bin"] = merged_values.apply(
        lambda row: return_wagner_decile(row.iloc[3:12], row.iloc[12]), axis=1
    )

    decile_plot_df = pd.merge(
        attributes,
        merged_values[["id", "bin"]],
        "inner",
        left_on="id",
        right_on="id",
    )

    # Order by sections
    all_plots_children = []
    for section in sections:
        df = decile_plot_df.copy()

        df.set_index("id", inplace=True)
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
    app.run_server(debug=False)
    # app.run(debug=True)
