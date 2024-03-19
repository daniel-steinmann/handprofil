import json
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Index

import common

data_and_attributes_schema = DataFrameSchema({
    "id": Column(int),
    "device": Column(str),
    "hand": Column(str),
    "description": Column(str),
    "unit": Column(str),
    "value": Column(int)
},
    index=Index(int))

split_out_schema = DataFrameSchema(
    {
        "id": Column(int),
        "device": Column(str),
        "hand": Column(str),
        "description": Column(str),
        "unit": Column(str),
        "value": Column(int),
    }
)


@pa.check_output(split_out_schema, 0)
@pa.check_output(split_out_schema, 1)
@pa.check_output(split_out_schema, 2)
def split_reorder_plot_df_to_sections(plot_df: pd.DataFrame, section_config: list):
    plot_df["id"] = plot_df.index
    output_dfs = []
    for value in section_config:
        index_data = value["index_order"]
        index = pd.Index(index_data)
        output_df = plot_df.reindex(index).dropna(
            axis=0).reset_index(drop=True)
        output_df["id"] = output_df["id"].astype(int)
        output_df["value"] = output_df["value"].astype(int)
        output_dfs.append(output_df)

    return output_dfs


def load_plot_section_config() -> list:
    with open(
        common.get_absolute_path("src/plotting/config/plot_sections.json"), "r"
    ) as file:
        section_config = json.load(file)
    return section_config
