import json
import os
from pathlib import Path

import pandas as pd


def get_absolute_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    src_path = Path(directory_path).parents[1]
    return os.path.join(src_path, relative_path)


def load_attributes() -> pd.DataFrame:
    df = pd.read_csv(get_absolute_path("src/handprofil/config/attributes.csv"))
    df = df.set_index("id", drop=True)
    return df


def load_meta_attributes() -> pd.DataFrame:
    df = pd.read_csv(get_absolute_path(
        "src/handprofil/config/meta_attributes.csv"))
    df = df.set_index("id", drop=True)
    return df


def load_background() -> pd.DataFrame:
    df = pd.read_csv(get_absolute_path("src/handprofil/config/background.csv"))
    return df


def load_plot_section_config() -> list:
    with open(
        get_absolute_path("src/handprofil/config/plot_sections.json"), "r"
    ) as file:
        section_config = json.load(file)
    return section_config
