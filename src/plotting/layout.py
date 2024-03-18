import dash_mantine_components as dmc
from dash import html, dcc


def get_layout():
    return dmc.Container(
        [
            dmc.Title("Handlabor"),
            html.Div(
                [
                    dmc.Button("Download Template (.xlsx)", id="btn_image"),
                    dcc.Download(id="download-xlsx"),
                ]
            ),
            dmc.Title("Upload", order=2),
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                # Allow multiple files to be uploaded
                multiple=True,
            ),
            dmc.Container(id="upload-alerts"),
            dmc.Title("Datensätze", order=2),
            dmc.Grid(id="subject-grid"),
            dmc.Grid(
                [
                    dmc.Col(
                        [
                            dmc.Card(
                                children=[
                                    dmc.Title("Hintergrund", order=2),
                                    dmc.RadioGroup(
                                        [
                                            dmc.Radio(l, value=k)
                                            for k, l in [
                                                ["m", "Männlich"],
                                                ["w", "Weiblich"],
                                            ]
                                        ],
                                        id="radiogroup-sex",
                                        value="m",
                                        label="Geschlecht",
                                        size="sm",
                                        mt=10,
                                    ),
                                    dmc.Select(
                                        label="Instrument",
                                        searchable=True,
                                        placeholder="Select one",
                                        id="select-instrument",
                                        value="gemischt",
                                        data=[
                                            {"value": "violine", "label": "Violine"},
                                            {
                                                "value": "violoncello",
                                                "label": "Violoncello",
                                            },
                                            {
                                                "value": "schlagzeug",
                                                "label": "Schlagzeug",
                                            },
                                            {"value": "klavier", "label": "Klavier"},
                                            {"value": "gitarre", "label": "Gitarre"},
                                            {"value": "egitarre", "label": "E-Gitarre"},
                                            {
                                                "value": "akkordeon",
                                                "label": "Akkordeon",
                                            },
                                            {"value": "gemischt", "label": "Gemischt"},
                                        ],
                                        style={"width": 200, "marginBottom": 10},
                                    ),
                                ]
                            ),
                        ],
                        span="auto",
                    ),
                    dmc.Col(
                        [
                            dmc.Card(
                                children=[
                                    dmc.Title("Hand", order=2),
                                    dmc.RadioGroup(
                                        [
                                            dmc.Radio(l, value=k)
                                            for k, l in [
                                                ["right", "Rechts"],
                                                ["left", "Links"],
                                            ]
                                        ],
                                        id="radiogroup-hand",
                                        value="right",
                                        label="Hand",
                                        size="sm",
                                        mt=10,
                                    ),
                                ]
                            ),
                        ],
                        span="auto",
                    ),
                ]
            ),
            html.Div(id="all_plots"),
        ],
        fluid=True,
    )
