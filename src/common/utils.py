import os
from pathlib import Path


def get_absolute_path(relative_path):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    src_path = Path(directory_path).parents[1]
    return os.path.join(src_path, relative_path)
