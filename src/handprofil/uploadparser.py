from dash import html
import pandas as pd
import dash_mantine_components as dmc
import base64
import io
import numpy as np


def parse_contents(contents) -> dict:
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        info = pd.read_excel(
            io.BytesIO(decoded),
            header=0,
            skiprows=3,
            nrows=9,
            names=["id", "description", "value"],
            usecols=[0, 1, 2],
            dtype={
                "id": np.int64,
                "description": str,
            }
        )
        data = pd.read_excel(
            io.BytesIO(decoded),
            header=0,
            skiprows=14,
            usecols=[0, 1, 2, 5, 6],
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

    return True, {"info": info.to_dict(), "data": data.to_dict()}


def parse_and_validate_uploads(
    upload_contents: list
):
    uploaded_files = [
        parse_contents(c) for c in upload_contents
    ]

    return uploaded_files
