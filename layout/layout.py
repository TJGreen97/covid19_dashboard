"""
COVID19 Dashboard by Torran Green

All data is queried from the Johns Hopkins University open dataset on Google's BigQuery.
This dashboard is for educational use.
----------------------------------------------------------------------------------------
Layout module, describing the dashboard layout. The '.\assets\' directory contains CSS
scripts for further style control.
"""
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

layout = html.Div(
    className="main-div",
    children=[
        dcc.Store(id="country-store", storage_type="session"),
        html.Div(
            [
                html.Div(
                    [
                        html.H1(id="title", children="COVID19 Dashboard"),
                        html.Div(
                            children="""
                Created by Torran Green, using the Johns Hopkins University dataset.
            """
                        ),
                    ],
                    style=dict(marginLeft="20px", width="40%", padding="20px"),
                ),
                html.Div(
                    [
                        html.H3("Global Totals", style=dict(margin="0px")),
                        dcc.Graph(
                            id="global-stats",
                            config={"displayModeBar": False},
                            figure=go.Figure(
                                layout=dict(
                                    margin={"l": 0, "r": 0, "t": 0, "b": 0},
                                    height=100,
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                )
                            ),
                        ),
                    ],
                    style=dict(width="60%", textAlign="center"),
                ),
            ],
            className="header-div",
        ),
        html.Div(
            [
                html.H2(
                    id="overview-heading",
                    children="Overview Data (stacked bars)",
                    style=dict(marginTop="0px", textAlign="center"),
                ),
                dcc.Graph(
                    id="overview-graph",
                    config={"displayModeBar": False},
                    figure=go.Figure(
                        layout=dict(
                            barmode="stack",
                            legend_title="Select Data to View:",
                            legend=dict(x=0.01, y=1),
                            showlegend=True,
                            hovermode='x',
                            paper_bgcolor="rgb(45, 45, 45)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            xaxis_title="Country",
                            yaxis_title="Total Cases",
                            margin={"t": 0},
                            # dragmode=False,
                            font=dict(
                                family="Courier New, monospace",
                                size=18,
                                color="rgb(228, 241, 250)",
                            ),
                            yaxis=dict(gridcolor="rgb(121, 117, 117)", fixedrange=True),
                            xaxis=dict(
                                categoryorder="total ascending",
                                gridcolor="rgb(121, 117, 117)",
                                fixedrange=True,
                            ),
                        )
                    ),
                ),
                html.Div(
                    [
                        html.H5(children="Number of Countries in View:",
                                style=dict(marginLeft='60px')
                                ),
                        html.Div(
                            [
                                dcc.Slider(
                                    id="bar-limit",
                                    min=2,
                                    max=20,
                                    step=1,
                                    value=10,
                                    marks={
                                        2: "2",
                                        4: "4",
                                        6: "6",
                                        8: "8",
                                        10: "10",
                                        12: "12",
                                        14: "14",
                                        16: "16",
                                        18: "18",
                                        20: "20",
                                    },
                                )
                            ],
                            style=dict(width="60%", marginTop="10px"),
                        ),
                    ],
                    style=dict(display="flex"),
                ),
            ],
            className="full-bar-div",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    children="Search for Country:", style=dict(width="50%")
                                ),
                                dcc.Input(
                                    id="choose-country",
                                    type="text",
                                    value="US",
                                    debounce=True,
                                    style=dict(width="50%", marginRight="20px"),
                                ),
                                html.Button(
                                    "SELECT",
                                    id="select-country",
                                    style=dict(color="rgb(228, 241, 250)"),
                                ),
                            ],
                            style=dict(
                                textAlign="left", marginBottom="1%", width="31%"
                            ),
                        ),
                        html.H1(
                            id="country-heading",
                            children="Country View",
                            style=dict(
                                textAlign="center", width="40%", marginTop="30px"
                            ),
                        ),
                    ],
                    style=dict(display="flex"),
                ),
                dcc.Loading(
                    type="dot",
                    children=html.Div(
                        [
                            dcc.Graph(
                                id="country-stats",
                                config={"displayModeBar": False},
                                figure=go.Figure(
                                    layout=dict(
                                        margin={"l": 0, "r": 0, "t": 0, "b": 0},
                                        height=100,
                                        paper_bgcolor="rgba(0,0,0,0)",
                                        plot_bgcolor="rgba(0,0,0,0)",
                                    )
                                ),
                            )
                        ],
                        className="country-indicator",
                    ),
                ),
                html.Div(
                        [
                            dcc.Loading(
                                id="total-loading",
                                style=dict(backgroundColor="rgb(60,60,60)"),
                                children=[
                                    dcc.Graph(
                                        id="country-total",
                                        style=dict(height="100%"),
                                        config={"displayModeBar": False},
                                        figure=go.Figure(
                                            layout=dict(
                                                xaxis_title="Date",
                                                yaxis_title="Total Cases",
                                                legend_title="Select Data to View:",
                                                title=dict(
                                                    text="Cumulative Number of Cases",
                                                    xanchor="center",
                                                    x=0.5,
                                                    yref="container",
                                                    yanchor="top",
                                                    y=1,
                                                ),
                                                legend=dict(x=0.01, y=1),
                                                showlegend=True,
                                                margin={"t": 50, "b": 0},
                                                paper_bgcolor="rgb(60, 60, 60)",
                                                plot_bgcolor="rgb(60, 60, 60)",
                                                dragmode="pan",
                                                font=dict(
                                                    family="Courier New, monospace",
                                                    size=18,
                                                    color="rgb(228, 241, 250)",
                                                ),
                                                yaxis=dict(
                                                    gridcolor="rgb(121, 117, 117)",
                                                    fixedrange=True,
                                                ),
                                                xaxis=dict(
                                                    gridcolor="rgb(121, 117, 117)",
                                                    tickformat="%d/%m/%y",
                                                    tickangle=45,
                                                    type="date",
                                                    rangeselector=dict(
                                                        buttons=list(
                                                            [
                                                                dict(
                                                                    count=7,
                                                                    label="1w",
                                                                    step="day",
                                                                    stepmode="backward",
                                                                ),
                                                                dict(
                                                                    count=1,
                                                                    label="1m",
                                                                    step="month",
                                                                    stepmode="backward",
                                                                ),
                                                                dict(
                                                                    count=3,
                                                                    label="3m",
                                                                    step="month",
                                                                    stepmode="backward",
                                                                ),
                                                                dict(step="all"),
                                                            ]
                                                        ),
                                                        bgcolor="rgb(55,55,55)",
                                                        activecolor="rgb(95, 95, 95)",
                                                        x=1,
                                                        y=1,
                                                        xanchor="right",
                                                    ),
                                                ),
                                            )
                                        ),
                                    )
                                ],
                                type="dot",
                            )
                        ],
                        className="cases-line-div",
                        ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Loading(
                                    id="rates-loading",
                                    style=dict(backgroundColor="rgb(60,60,60)"),
                                    children=[
                                        dcc.Graph(
                                            id="country-rates",
                                            style=dict(height="100%"),
                                            config={"displayModeBar": False},
                                            figure=go.Figure(
                                                layout=dict(
                                                    barmode="overlay",
                                                    xaxis_title="Date",
                                                    yaxis_title="New Cases",
                                                    legend_title="Select Data to View:",
                                                    title=dict(
                                                        text="Daily New Cases (overlaid bars)",
                                                        xanchor="center",
                                                        x=0.5,
                                                        yref="container",
                                                        yanchor='top',
                                                        y=1,
                                                    ),
                                                    legend=dict(x=0.01, y=1),
                                                    showlegend=True,
                                                    margin={"t": 50, "b": 0},
                                                    paper_bgcolor="rgb(60, 60, 60)",
                                                    plot_bgcolor="rgb(60, 60, 60)",
                                                    dragmode="pan",
                                                    font=dict(
                                                        family="Courier New, monospace",
                                                        size=18,
                                                        color="rgb(228, 241, 250)",
                                                    ),
                                                    yaxis=dict(
                                                        gridcolor="rgb(121, 117, 117)",
                                                        fixedrange=True,
                                                    ),
                                                    xaxis=dict(
                                                        gridcolor="rgb(121, 117, 117)",
                                                        tickformat="%d/%m/%y",
                                                        tickangle=45,
                                                        type="date",
                                                        rangeselector=dict(
                                                            buttons=list(
                                                                [
                                                                    dict(
                                                                        count=7,
                                                                        label="1w",
                                                                        step="day",
                                                                        stepmode="backward",
                                                                    ),
                                                                    dict(
                                                                        count=1,
                                                                        label="1m",
                                                                        step="month",
                                                                        stepmode="backward",
                                                                    ),
                                                                    dict(
                                                                        count=3,
                                                                        label="3m",
                                                                        step="month",
                                                                        stepmode="backward",
                                                                    ),
                                                                    dict(step="all"),
                                                                ]
                                                            ),
                                                            bgcolor="rgb(55,55,55)",
                                                            activecolor="rgb(95, 95, 95)",
                                                            x=1,
                                                            y=1,
                                                            xanchor="right",
                                                        ),
                                                    ),
                                                )
                                            ),
                                        )
                                    ],
                                    type="dot",
                                )
                            ],
                            className="cases-line-div2",
                        ),
                        html.Div(
                            [
                                dcc.Loading(
                                    id="pie-loading",
                                    style=dict(backgroundColor="rgb(60,60,60)"),
                                    children=[
                                        dcc.Graph(
                                            id="country-pie",
                                            config={"displayModeBar": False},
                                            figure=go.Figure(
                                                layout=dict(
                                                    title=dict(
                                                        text="Current Distribution of Cases",
                                                        xanchor="center",
                                                        x=0.5,
                                                        y=1,
                                                        yref="container",
                                                        yanchor="top"
                                                    ),
                                                    legend=dict(
                                                        x=0.5,
                                                        y=0,
                                                        xanchor='center'),
                                                    legend_orientation='h',
                                                    margin={
                                                        "l": 0,
                                                        "r": 0,
                                                        "t": 50,
                                                        "b": 0,
                                                    },
                                                    font=dict(
                                                        family="Courier New, monospace",
                                                        size=18,
                                                        color="rgb(228, 241, 250)",
                                                    ),
                                                    paper_bgcolor="rgb(60, 60, 60)",
                                                    plot_bgcolor="rgb(60, 60, 60)",
                                                )
                                            ),
                                        ),
                                    ],
                                    type="dot",
                                ),
                            ],
                            className="pie-div",
                        ),
                    ],
                    style=dict(display="flex"),
                ),
            ],
            className="country-div",
        ),
        html.H4(
            id="disclaimer",
            style=dict(
                padding="50px",
                borderBottom="solid 20px rgb(15, 15, 15)",
                margin="0",
                textAlign="right",
                textSize="1.6em",
                backgroundColor="rgb(43, 33, 53)",
            ),
        ),
    ],
    style=dict(height="100%"),
)
