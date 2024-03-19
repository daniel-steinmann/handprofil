import json
import pandas as pd

import common


def split_reorder_plot_df_to_sections(plot_df: pd.DataFrame, section_config: list):
    plot_df["id"] = plot_df.index.values
    output_dfs = []
    for value in section_config:
        index_data = value["index_order"]
        index = pd.Index(index_data)
        output_df = plot_df.reindex(index).dropna(axis=0).reset_index(drop=True)
        output_dfs.append(output_df)

    return output_dfs


def load_plot_section_config() -> list:
    with open(
        common.get_absolute_path("src/plotting/config/plot_sections.json"), "r"
    ) as file:
        section_config = json.load(file)
    return section_config
