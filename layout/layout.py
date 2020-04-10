import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import plotly.graph_objects as go

layout = html.Div(children=[

    dcc.Store(id='country-store', storage_type='session'),

    html.Div([
        html.Div([
            html.H1(id='title', children='COVID19 Dashboard'),

            html.Div(children='''
                Created by Torran Green, using Johns Hopkins University dataset.
            ''')
        ],
            style=dict(marginRight='10%')    
        ),
        html.Div([
            dcc.Loading(type='circle', 
                        children= dcc.Graph(id='global-stats',
                                            config={'displayModeBar': False},
                                            figure=go.Figure(layout=dict(margin={'l':0,'r':0,'t':0,'b':0},
                                                                height=100,
                                                                paper_bgcolor = 'rgba(0,0,0,0)',
                                                                plot_bgcolor = 'rgba(0,0,0,0)'))
                                            )
            )
        ],
            style=dict(width='60%')
        )
    ],
        style=dict(display='flex', backgroundColor='lightblue')
    ),
    html.Div([
        dcc.Checklist(
        id='overview-checklist',
        options=[
            dict(label='Confirmed Cases', value='confirmed_cases'),
            dict(label='Recovered Cases', value='recovered_cases'),
            dict(label='Deaths', value='deaths')
        ],
        value=['confirmed_cases'],
        labelStyle=dict(display='inline-block'),
        style=dict(width='20%',
                    paddingTop='10px')
        ),
        html.H6(children='Number of Countries: ',
                style=dict(
                    width='10%'
                )),
        daq.NumericInput(
            id='bar-limit',
            min=2,
            max=20,
            value=10,
            style=dict(
                width='5%',
                textAlign='left',
                paddingTop='4px'
            )
        )
    ],
        style=dict(display='flex',
                    textAlign='center',
                    marginTop='1%')
    ),
    
    dcc.Graph(id='overview-graph',
            figure=go.Figure(layout=dict(title = 'Country Overview',
                                        barmode='stack',
                                        showlegend=True,
                                        xaxis={'categoryorder':'total ascending'})
                    )
    ),
    
    html.Div([
        html.H2(id='country-heading', children='Country View', style=dict(textAlign='center')),
        html.Div([
            html.H4(children='Select Country:', style=dict(width='50%')),
            dcc.Input( 
                            id="choose-country",
                            type="text",
                            value="US",
                            debounce=True,
                            style=dict(width='20%')
                            ),
            html.Button('SELECT', id='select-country')
        ],
            style=dict(textAlign='left', marginBottom='1%')
        ),
        dcc.Loading(id='country-loading',
                    type='circle',
                    children=
                    [html.Div([
                        html.Div([
                            dcc.Checklist(
                                    id='country-checklist',
                                    options=[
                                        dict(label='Confirmed Cases', value='confirmed_cases'),
                                        dict(label='Recovered Cases', value='recovered_cases'),
                                        dict(label='Deaths', value='deaths')
                                    ],
                                    value=['confirmed_cases'],
                                    labelStyle=dict(display='inline-block'),
                                    style=dict(width='30%',
                                                paddingTop='10px',
                                                textAlign='right')
                                    ),
                            dcc.Loading(id="rates-loading",
                                    children=dcc.Graph(id='country-rates',
                                                        figure=go.Figure(layout=dict(xaxis_title='Date', yaxis_title='Number',
                                                                                    showlegend=True, xaxis=dict(
                                                                                                tickformat = '%d/%m/%y',
                                                                                                type ='date',
                                                                                                rangeselector=dict(
                                                                                                    buttons=list([
                                                                                                        dict(count=7,
                                                                                                            label='1w',
                                                                                                            step='day',
                                                                                                            stepmode='backward'),
                                                                                                        dict(count=1,
                                                                                                            label='1m',
                                                                                                            step='month',
                                                                                                            stepmode='backward'),
                                                                                                        dict(count=3,
                                                                                                            label='3m',
                                                                                                            step='month',
                                                                                                            stepmode='backward'),
                                                                                                        dict(step='all')
                                                                                                    ])
                                                                                                ),
                                                                                                rangeslider=dict(
                                                                                                    visible=True
                                                                                                ),
                                                                                    )
                                                                    ))
                                    
                                    ),
                                    type="circle"),
                        ],
                            style=dict(width='70%')
                        ),
                        html.Div([
                            dcc.Loading(id="pie-loading",
                                        children=dcc.Graph(id='country-pie',
                                                            figure=go.Figure(layout=dict(
                                                                                paper_bgcolor = 'rgba(0,0,0,0)',
                                                                                plot_bgcolor = 'rgba(0,0,0,0)'))
                                        ),
                                        type="circle")
                        ],
                            style=dict(width='30%')
                        ),
                    ],
                        style=dict(display='flex')
                    )
        ])
    ],
        style=dict(border='2px black solid', padding='10px')
    ),
    html.H4(id='disclaimer', style=dict(padding='5%',
                                textAlign='right',
                                textSize=100))
])