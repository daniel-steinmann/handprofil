from dash import html
import pandas as pd
import dash_mantine_components as dmc
import base64
import io
import numpy as np

import utils


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


def validate_upload_format(df) -> dmc.Alert:
    # Necessary Assertions
    # 1. Correct Input Format (All required indices must be present in id - column)
    # 2. At least one value field must have a value
    attributes = utils.load_attributes()
    meta_attributes = utils.load_meta_attributes()

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

    meta_attributes = utils.load_meta_attributes()

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

    if df.loc["M6", "value"] not in ["F", "M", "O"]:
        msg = f"Invalid gender value. Valid: F,M,O"
        alert.children = msg
        return False, alert

    if df.loc["M7", "value"] not in ["R", "L", "B"]:
        msg = f"Invalid handiness. Valid: R,L,B"
        alert.children = msg
        return False, alert

    return True, None


def validate_upload(df) -> dmc.Alert:

    result, alert = validate_upload_format(df)
    if result == False:
        return False, alert

    result, alert = validate_meta_attributes(df)
    if result == False:
        return False, alert

    return True, None


def split_metadata_data(df):
    attributes = utils.load_attributes()
    meta_attributes = utils.load_meta_attributes()

    df = df.set_index("id", drop=True)

    return df.loc[meta_attributes.index, "value"], df.loc[attributes.index, "value"]


def parse_and_validate_uploads(
    upload_contents: list, upload_filenames: list, upload_dates: list
):
    uploaded_files = [
        parse_contents(c, n, d)
        for c, n, d in zip(upload_contents, upload_filenames, upload_dates)
    ]

    input_df = uploaded_files[0]

    validation_result, alert = validate_upload(input_df)
    if not validation_result:
        return False, None, None, alert

    metadata, data_df = split_metadata_data(input_df)
    return True, metadata, data_df, None
