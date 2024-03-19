import json
import pandas as pd

import common
import plotting


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


def load_plot_section_config() -> list:
    with open(
        common.get_absolute_path("src/plotting/config/plot_sections.json"), "r"
    ) as file:
        section_config = json.load(file)
    return section_config


def get_plot_sections(values, attributes, section_config):

    attributes["value"] = values
    data_per_section = split_reorder_plot_df_to_sections(
        attributes, section_config)

    all_plots_children = []
    for index, section in enumerate(section_config):
        figure = plotting.return_section_figure(data_per_section[index])
        child = plotting.wrap_figure_in_graph(section["title"], figure)
        all_plots_children.append(child)

    return all_plots_children
