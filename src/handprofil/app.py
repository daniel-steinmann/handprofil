###################
### Imports ######
###################

import base64
from pathlib import Path
import plotly.graph_objects as go
import io
import json
from dash import Dash, html, dcc, callback, Output, Input, State, ALL
import numpy as np
import pandas as pd
import dash_mantine_components as dmc
import os
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_auth
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv, find_dotenv


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

hand_data = [
    {
        "value": "left",
        "label": "Links (◇)"
    },
    {
        "value": "right",
        "label": "Rechts (●)"
    }
]

###################
### Styles ########
###################

global_colors = [
    "blue",
    "red",
    "violet",
    "orange"
    "lime",
]

container_style = {
    "border": f"1px solid black",
    "borderRadius": 8,
    "padding": 20,
    "marginTop": 20,
    "marginBottom": 20,
}

###################
##### Utils #######
###################


def get_absolute_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    src_path = Path(directory_path).parents[1]
    return os.path.join(src_path, relative_path)

# To avoid typechecking error https://github.com/microsoft/pylance-release/issues/5631


def my_concat(dfs_list, axis=0): return pd.concat(dfs_list, axis=axis)

###################
# Methods #########
###################


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

    # assert len(bin_edges) == 9

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


def parse_contents(contents, filename) -> dict:
    content_type, content_string = contents.split(",")

    if content_type != 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64':
        return False, "Ungültiges Dateiformat. Unterstützt werden Dateien im .xslx Format"

    decoded = base64.b64decode(content_string)
    try:
        info = pd.read_excel(
            io.BytesIO(decoded),
            sheet_name=0,
            header=0,
            nrows=9,
            names=["id", "description", "value"],
            usecols=[0, 1, 3],
            dtype={
                "id": np.int64,
                "description": str,
            }
        )\
            .dropna()

        data = pd.read_excel(
            io.BytesIO(decoded),
            sheet_name=1,
            header=0,
            usecols=[0, 1, 2, 4, 5],
            names=["id", "device", "description", "left", "right"],
            dtype={
                "id": np.int64,
                "device": str,
                "description": str,
                "left": np.float64,
                "right": np.float64
            }
        )
    except Exception as e:
        return False, e

    if len(data.dropna(subset=["left", "right"], how="all")) == 0:
        return False, "Keine Messungen gefunden"

    return True, {"info": info.to_dict(), "data": data.to_dict(), "filename": filename}

#######################
# Plots ########*
#######################


def return_ticktext(plot_df):
    return plot_df.apply(
        lambda x: f"{f'{x.id:0.0f},':<5} {x.description} ({x.unit})", axis=1
    )


def return_trace(df: pd.DataFrame, color, linestyle, symbol):
    return go.Scatter(
        x=pd.Series(df.value),
        y=pd.Series(df.section_position),
        marker=dict(size=16, color=color, symbol=symbol),
        mode="lines+markers",
        line=go.scatter.Line(color=color, dash=linestyle, width=2),
        connectgaps=True,
    )


def return_section_figure(df: pd.DataFrame, section_id: int):

    df_per_section = df[df["section_id"] == section_id]

    labelmargin = 200

    fig = px.scatter()
    ticktext = return_ticktext(
        df_per_section[["id", "description", "unit", "section_position"]].drop_duplicates().sort_values(by="section_position").reset_index(drop=True))

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
        hovermode=False,
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

    for file_id in df_per_section["file_id"].unique():
        for hand in df_per_section["hand"].unique():
            color = global_colors[file_id]
            linestyle = "solid" if hand == "right" else "dash"
            symbol = "circle" if hand == "right" else "diamond-open"

            # Need double bracket in .loc[[]] to prevent getting series
            in_df = df_per_section.query(
                "hand ==  @hand & file_id == @file_id")

            in_df = in_df\
                .set_index("section_position", drop=False)\
                .sort_index()

            fig.add_trace(return_trace(in_df, color, linestyle, symbol))

    return fig


def wrap_figure_in_graph(title: str, figure):
    return html.Div(
        [
            dmc.Title(title, order=2),
            dcc.Graph(
                # id="_wait_time_graph",
                style={"height": "100%", "width": "100%"},
                className="wait_time_graph",
                config={
                    "staticPlot": True,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure=figure,
            )
        ],
        style={
            "page-break-before": "initial",
        }
    )


def return_subject_grid(metadata: pd.Series, switch_id: str):
    return dmc.SimpleGrid(cols=4, children=[
        dmc.Container(
            [
                dmc.Text(f"Id: {metadata.loc['M1']}"),
                dmc.Text(f"Datum: {metadata.loc['M2'].strftime('%d.%m.%Y')}"),
                dmc.Text(f"Name: {metadata.loc['M3']}"),
                dmc.Text(f"Vorname: {metadata.loc['M4']}"),
            ]
        ),
        dmc.Container(
            [
                dmc.Text(
                    f"Geburtsdatum: {metadata.loc['M5'].strftime('%d.%m.%Y')}"),
                dmc.Text(f"Geschlecht: {metadata.loc['M6']}"),
                dmc.Text(f"Händigkeit: {metadata.loc['M7']}"),
                dmc.Text(f"Instrument: {metadata.loc['M8']}"),
            ]
        ),
        dmc.Container(
            children=[
                dmc.Text("Anzeigen")
            ]),
        dmc.Container(children=[dmc.ActionIcon(
            DashIconify(icon="mdi:trash", width=20),
            size="lg",
            variant="filled",
            id="action-icon",
            n_clicks=0,
            mb=10,
        )])
    ])


###################
###### Dash #######
###################

# Path
print(os.getcwd())

# Environment
# load_dotenv does not overwrite existing environment variables
load_dotenv()

# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)
print(f"Environment: {os.getenv('ENVIRONMENT')}")

if os.getenv('ENVIRONMENT') == 'PRODUCTION':
    auth = dash_auth.BasicAuth(
        app,
        {os.getenv('USERNAME'): os.getenv('PASSWORD')}
    )

# This is used by the production server
server = app.server

# App layout
app.layout = dmc.Container(
    [
        # Stores
        dcc.Store(id='upload-store', storage_type='memory'),
        dcc.Store(id='all-measurements', storage_type='memory'),
        dcc.Store(id='decile-data-store', storage_type='memory'),
        dcc.Store(id='plot-data-store', storage_type='memory'),
        dcc.Store(id='static-store', storage_type='session'),
        html.Div(children=[], id='static-store-initializer'),
        # Layout
        dmc.Header(height=60, children=[dmc.Center(
            dmc.Title("Handlabor", order=1))]),
        dmc.Container(
            style=container_style,
            children=[
                dmc.Group(
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
                        )
                    ]),
                dmc.Container(id="upload-debug-container"),
                dmc.Container(id="upload-error-messages"),
            ]),
        dmc.Container(
            style=container_style,
            children=[
                dmc.Title("Hintergrund", order=2),
                dmc.Text(
                    "Es werde nur Metriken angezeigt, für welche Hintergrunddaten verfügbar sind.",
                ),
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
                        ),
                        dmc.Select(
                            label="Instrument",
                            searchable=True,
                            placeholder="Select one",
                            id="select-instrument",
                            value="gemischt",
                            data=instrument_data,
                        )
                    ]),
                dmc.Checkbox(
                    id="checkbox-background-hand", label="Fehlenden Hintergrund bei einer Hand durch andere Hand ersetzen.",
                    checked=True,
                    mt=10
                ),
            ]
        ),
        dmc.Container(id="all-plots", style=container_style)
    ],
    fluid=True,
)

#######################
##### Callbacks #######
#######################


@callback(
    Output('static-store', 'data'),
    Input('static-store-initializer', 'children')
)
def load_static_data(trigger):
    measure_labels = pd.read_csv(
        get_absolute_path(
            "src/handprofil/config/attributes.csv"),
        header=0,
        dtype={
            "id": np.int64,
            "device": str,
            "description": str,
            "unit": str
        }
    ).to_dict()

    info_labels = pd.read_csv(
        get_absolute_path(
            "src/handprofil/config/meta_attributes.csv"),
        header=0,
        dtype={
            "id": np.int64,
            "description": str,
        }
    ).to_dict()

    background = pd.read_csv(
        get_absolute_path(
            "src/handprofil/config/background.csv"),
        header=0,
        dtype={
            "instrument": str,
            "sex": str,
            "hand": str,
            "id": np.int64,
            "bin_edge": np.int64,
            "value": np.float64
        }
    ).to_dict()

    with open(
        get_absolute_path(
            "src/handprofil/config/plot_sections.json"), "r"
    ) as file:
        section_config = json.load(file)

    # Check if all measure labels are present in section config
    assert set(measure_labels['id'].values()) == set(
        [index for item in section_config for index in item["index_order"]])

    return {
        "measure_labels": measure_labels,
        "info_labels": info_labels,
        "background_data": background,
        "section_config": section_config
    }


@callback(
    Output('decile-data-store', 'data'),
    Input('upload-store', 'data'),
    Input('radiogroup-sex', 'value'),
    Input('select-instrument', 'value'),
    Input('checkbox-background-hand', 'checked'),
    State('static-store', 'data'),
    prevent_initial_call=True,
)
def compute_binned_values(
    upload_store: list,
    sex: str,
    instrument: str,
    checkbox_background_hand: bool,
    static_store: dict
):
    if upload_store is None:
        raise PreventUpdate

    # Background is the same for all
    background_data = pd.DataFrame.from_dict(static_store["background_data"])\
        .astype({
            "instrument": str,
            "sex": str,
            "hand": str,
            "id": np.int64,
            "bin_edge": np.int64,
            "value": np.float64
        })\
        .pivot(index=["instrument", "sex", "id", "bin_edge"], columns="hand", values="value")

    if checkbox_background_hand:
        # Fill left or right hand background value if not available
        background_data[["left", "right"]] = background_data[["left", "right"]]\
            .bfill(axis=1).ffill(axis=1)

    background_data = background_data.reset_index().melt(
        id_vars=['id', 'instrument', 'sex', 'bin_edge'])

    # Filter background
    background_data = background_data.query(
        'sex == @sex & instrument == @instrument')

    background_data = background_data\
        .set_index(["id", "hand", "bin_edge"])\
        .sort_index()\
        .dropna()

    # Parse uploaded data
    uploaded_data = [
        pd.DataFrame.from_dict(item["data"]).astype({
            "id": np.int64,
            "left": np.float64,
            "right": np.float64
        }) for item in upload_store]

    binned_data = []
    for data in uploaded_data:
        # Drop NaN values
        # Keep as dataframe to allow index access in "apply"
        data = data\
            .melt(id_vars=["id"], value_vars=["left", "right"], var_name="hand")\
            .set_index(["id", "hand"])\
            .dropna()

        # Only process IDs with available background
        data = data.loc[background_data.unstack(
            "bin_edge").index.intersection(data.index)]\
            .sort_index()\

        # Apply binning and assign to value
        if not data.empty:
            data["value"] = data.apply(
                lambda row: return_wagner_decile(
                    background_data.loc[row.name, "value"], row["value"]
                ), axis=1
            )

        data = data.reset_index()

        # Reset index for json serialization
        binned_data.append(data.to_dict())

    return binned_data


@callback(
    Output("plot-data-store", 'data'),
    Input('decile-data-store', 'data'),
    Input({"type": 'chips-hand', "index": ALL}, 'value'),
    State('static-store', 'data'),
    prevent_initial_call=True
)
def get_plot_input_data(
    decile_data_store: str,
    hands_shown_values: list,
    static_store: dict
):
    if decile_data_store is None:
        raise PreventUpdate

    decile_data_store = [
        pd.DataFrame.from_dict(item).set_index(["id", "hand"]) for item in decile_data_store
    ]

    static_store = {
        key: pd.DataFrame.from_dict(item) for key, item in static_store.items()
    }

    plot_files = []
    for i, file in enumerate(decile_data_store):
        plot = static_store['measure_labels'].set_index('id')

        # Only get specified hands
        file = file.reset_index()\

        file = file\
            .loc[file["hand"].isin(hands_shown_values[i])]\
            .set_index(["id"])

        # Add labels and flatten
        file = file\
            .merge(plot, how="left", left_index=True, right_index=True)\
            .reset_index()\

        # Easier to debug
        file = file.to_dict()

        plot_files.append(file)

    return plot_files


@callback(
    Output("all-plots", 'children'),
    Input('plot-data-store', 'data'),
    State('static-store', 'data'),
    prevent_initial_call=True
)
def create_plots(
    plot_data_store: dict,
    static_store: dict,
):
    plot_data_store = [
        pd.DataFrame.from_dict(item) for item in plot_data_store
    ]

    section_config = static_store['section_config']

    all_files = []
    for file_id, file in enumerate(plot_data_store):
        # Check here if dataframe is not empty
        if len(file) != 0:
            file = file.set_index('id')
            file.loc[:, "file_id"] = file_id
            all_files.append(file)

    # Check here if all files are empty
    if len(all_files) == 0:
        return []

    plot_input = my_concat(all_files, axis=0)\
        .reset_index()\
        .set_index("id", drop=False)
    # .melt(id_vars=["id", "device", "description", "unit", "file_id"], var_name="hand")\

    for section_id, section in enumerate(section_config):
        section_position = 0
        for index in section['index_order']:
            if index in plot_input.index:
                plot_input.loc[index, "section_id"] = section_id
                plot_input.loc[index, "section_position"] = section_position
                section_position = section_position + 1

    all_plots_children = []
    for section_id, section in enumerate(section_config):
        if len(plot_input[plot_input["section_id"] == section_id]):
            figure = return_section_figure(plot_input, section_id)
            child = wrap_figure_in_graph(section["title"], figure)
            all_plots_children.append(child)

    return all_plots_children


@callback(
    Output('upload-debug-container', 'children'),
    Input('upload-store', 'data'),
    prevent_initial_call=True,
)
def display_upload_store_content(data: list):
    children = []
    for id, value in enumerate(data):
        filename = value["filename"]
        info = pd.DataFrame.from_dict(value["info"]).set_index('id')["value"]

        try:
            measure_date = datetime.strptime(
                info.get(2), '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y')
            birth_date = datetime.strptime(
                info.get(5), '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y')
        except:
            measure_date = ""
            birth_date = ""

        child = dmc.SimpleGrid(
            style={
                "borderColor": global_colors[id],
                "border": f"4px solid {global_colors[id]}",
                "borderRadius": 16,
                "padding": 20,
                "marginTop": 20,
                "marginBottom": 20,
            },
            cols=3,
            children=[
                dmc.Container(
                    children=[
                        dmc.Text(f'Datei: {filename}'),
                        dmc.Text(f'ID: {info.get(1, " ")}'),
                        dmc.Text(f'Datum: {measure_date}')
                    ]
                ),
                dmc.Container(
                    children=[
                        dmc.Text(
                            f'{info.get(3, "")}, {info.get(4, "")} ({info.get(6,"")})'),
                        dmc.Text(f'{birth_date}'),
                        dmc.Text(f'Händigkeit: {info.get(7, "")}'),
                        dmc.Text(f'Instrument: {info.get(8, "")}'),
                    ]
                ),
                dmc.Group([
                    dmc.ChipGroup(
                        [
                            dmc.Chip(
                                x["label"],
                                value=x["value"],
                                variant="filled",
                                color=global_colors[id]
                            )
                            for x in hand_data
                        ],
                        id={"type": "chips-hand", "index": id},
                        value=["left", "right"],
                        multiple=True,
                    ), dmc.ActionIcon(
                        DashIconify(icon="mdi:trash", width=20),
                        variant="outline",
                        id={"type": "delete-file-button", "index": id},
                        n_clicks=0,
                        radius="xl",
                        color="red",
                    )])])
        children.append(child)

    return children


@callback(
    Output('upload-store', 'data', allow_duplicate=True),
    Input({"type": "delete-file-button", "index": ALL}, "n_clicks"),
    State({"type": "delete-file-button", "index": ALL}, "id"),
    State('upload-store', 'data'),
    prevent_initial_call=True,
)
def delete_file_from_store(n_clicks, id: dict, data: dict):
    for i, clicks in enumerate(n_clicks):
        if clicks > 0:
            data.pop(id[i]['index'])
            return data
    return data


@callback(
    Output('upload-store', 'data', allow_duplicate=True),
    # Workaround for https://github.com/plotly/dash-core-components/issues/816
    Output('upload-data', 'contents'),
    Output('upload-error-messages', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-store', 'data'),
    prevent_initial_call=True,
)
def upload_files_to_store(list_of_contents, list_of_filenames, store_state):
    if list_of_contents is None:
        raise PreventUpdate

    results = [
        parse_contents(c, f) for c, f in zip(list_of_contents, list_of_filenames)
    ]

    new_items = [
        data for result, data in results if result
    ]

    errors = [
        dmc.Alert(e, title="Fehler beim Upload", color="red") for result, e in results if not result
    ]

    export = store_state + new_items if store_state else new_items
    return export, None, errors


@callback(
    Output("download-xlsx", "data"),
    Input("btn_image", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file(get_absolute_path("src/handprofil/download/measurement_template.xlsx"))


#######################
####### Main ##########
#######################
# Run the App
if __name__ == "__main__":
    app.run(debug=True)
