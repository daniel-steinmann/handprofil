from common import load_attributes, load_meta_attributes, load_background


def test_load_attributes():
    # Arrange
    # Act
    df = load_attributes()

    # Assert
    assert df.index.name == "id"
    assert len(df.columns) == 4


def test_load_meta_attributes():
    """
    Testing Upload Function
    """
    # Arrange
    # Act
    df = load_meta_attributes()

    # Assert
    assert df.index.name == "id"
    assert len(df.columns) == 1


def test_load_background():
    """
    Testing Upload Function
    """
    # Arrange
    # Act
    df = load_background()

    # Assert
    assert len(df.columns) == 13
