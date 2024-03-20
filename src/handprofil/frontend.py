import html
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import html, dcc
import json
import pandas as pd

from .utils import (
    get_absolute_path,
    load_plot_section_config
)


def __return_ticktext(plot_df):
    return plot_df.apply(
        lambda x: f"{f'{x.id:0.0f},':<5} {x.description} ({x.unit})", axis=1
    )


def __return_trace(df: pd.DataFrame, color="black"):
    return go.Scatter(
        x=df.value,
        y=df.index,
        marker=dict(size=16, color=color),
        mode="lines+markers",
        line=dict(dash="solid", width=2, color=color),
        connectgaps=True,
    )


def return_section_figure(df: pd.DataFrame):
    labelmargin = 200

    fig = px.scatter()
    ticktext = __return_ticktext(df)

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

    fig.add_trace(__return_trace(df))

    return fig


def wrap_figure_in_graph(title: str, figure):
    return html.Div(
        [
            dmc.Title(title, order=2),
            dcc.Graph(
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
        ],
        style={
            # "padding-left": "20px",
        }
    )


def return_subject_grid(metadata: pd.Series, switch_id: str):
    return [
        dmc.Col(
            [
                dmc.Text(f"ID: {metadata.loc['M1']}"),
                dmc.Text(f"Datum: {metadata.loc['M2'].strftime('%d.%m.%Y')}"),
                dmc.Text(f"Name: {metadata.loc['M3']}"),
                dmc.Text(f"Vorname: {metadata.loc['M4']}"),
            ],
            span="auto",
        ),
        dmc.Col(
            [
                dmc.Text(
                    f"Geburtsdatum: {metadata.loc['M5'].strftime('%d.%m.%Y')}"),
                dmc.Text(f"Geschlecht: {metadata.loc['M6']}"),
                dmc.Text(f"Händigkeit: {metadata.loc['M7']}"),
                dmc.Text(f"Instrument: {metadata.loc['M8']}"),
            ],
            span="auto",
        ),
        dmc.Switch(id=switch_id),
    ]

def get_plot_sections(values, attributes, section_config):
    merged = attributes.merge(values.rename(
        'value'), left_index=True, right_index=True)
    data_per_section = split_reorder_plot_df_to_sections(
        merged, section_config)

    all_plots_children = []
    for index, section in enumerate(section_config):
        figure = return_section_figure(data_per_section[index])
        child = wrap_figure_in_graph(section["title"], figure)
        all_plots_children.append(child)

    return all_plots_children


def split_reorder_plot_df_to_sections(plot_df: pd.DataFrame, section_config: list):
    plot_df["id"] = plot_df.index.values
    output_dfs = []
    for value in section_config:
        index_data = value["index_order"]
        index = pd.Index(index_data)
        output_df = plot_df.reindex(index).dropna(
            axis=0).reset_index(drop=True)
        output_dfs.append(output_df)

    return output_dfs
