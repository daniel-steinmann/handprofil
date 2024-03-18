from dash import html
import pandas as pd
import dash_mantine_components as dmc
import base64
import re
import io
import numpy as np

from common import load_attributes, load_meta_attributes


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


def upload_is_valid(df) -> dmc.Alert:
    # Necessary Assertions
    # 1. Correct Input Format (All required indices must be present in id - column)
    # 2. At least one value field must have a value
    attributes = load_attributes()
    meta_attributes = load_meta_attributes()

    validation_set = set(
        np.concatenate([attributes.index.values, meta_attributes.index.values])
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


def validate_meta_attributes(df) -> dmc.Alert:
    # Necessary Assertions
    # 1. All metadata attributes have values
    # 2. Metadata attributes make sense
    # TODO: Metadata should not be configurable, part of application

    meta_attributes = load_meta_attributes()

    df = df.set_index("id", drop=True)

    alert = dmc.Alert(title="Validation error", color="red")
    missing_values = []

    for field in meta_attributes.index.values:
        if df.isna().loc[field, "value"]:
            missing_values.append(field)

    if len(missing_values) > 0:
        msg = f"No values found for {missing_values}"
        alert.children = msg
        return False, alert

    # ID: Can be anything

    date_pattern = r"^[0-9]{2}.[0-9]{2}.[0-9]{4}$"
    if not re.match(date_pattern, df.loc["M2", "value"]):
        msg = f"Invalid date format."
        alert.children = msg
        return False, alert

    return True, None
