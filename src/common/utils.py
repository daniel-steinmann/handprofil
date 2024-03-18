import os
from pathlib import Path

import pandas as pd


def get_absolute_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    src_path = Path(directory_path).parents[1]
    return os.path.join(src_path, relative_path)


def load_attributes() -> pd.DataFrame:
    df = pd.read_csv(get_absolute_path("src/common/tables/attributes.csv"))
    df = df.set_index("id", drop=True)
    return df


def load_meta_attributes() -> pd.DataFrame:
    df = pd.read_csv(get_absolute_path("src/common/tables/meta_attributes.csv"))
    df = df.set_index("id", drop=True)
    return df


def load_background() -> pd.DataFrame:
    df = pd.read_csv(get_absolute_path("src/common/tables/background.csv"))
    return df
