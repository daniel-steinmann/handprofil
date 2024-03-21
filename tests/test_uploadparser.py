import base64
import os
import pytest
import pandas as pd
from handprofil.app import (
    upload_files_to_store,
)


def get_testfile_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory_path, relative_path)


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("measurement_template_filled.xlsx", True),
    ],
)
def test_validate_meta_attributes(filename, expected):
    # Arrange
    path = get_testfile_path(f"data/{filename}")

    with open(path, 'rb') as data:
        content = "xslx," + base64.b64encode(data.read()).decode('UTF-8')

    contents = [content, content]

    # Act
    data, _, _ = upload_files_to_store(contents, {})

    # Assert
    pd.DataFrame.from_dict({})
    assert len(data) == 2
    first_content = data[0]
    info = pd.DataFrame.from_dict(first_content['info'])
    data = pd.DataFrame.from_dict(first_content['data'])
