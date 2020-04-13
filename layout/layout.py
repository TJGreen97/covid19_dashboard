import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

layout = html.Div(className= 'main-div',
    children=[

    dcc.Store(id='country-store', storage_type='session'),

    html.Div([
        html.Div([
            html.H1(id='title', children='COVID19 Dashboard'),

            html.Div(children='''
                Created by Torran Green, using the Johns Hopkins University dataset.
            ''')
        ],
            style=dict(marginLeft='20px', width='40%', padding='20px')    
        ),
        html.Div([html.H3('Global Totals', style=dict(margin='0px')),
                    dcc.Graph(id='global-stats',
                            config={'displayModeBar': False},
                            figure=go.Figure(layout=dict(margin={'l':0,'r':0,'t':0,'b':0},
                                                height=100,
                                                paper_bgcolor = 'rgba(0,0,0,0)',
                                                plot_bgcolor = 'rgba(0,0,0,0)'))
                            )
        ],
            style=dict(width='60%', textAlign='center')
        )
    ],
        className='header-div'
    ),
    html.Div([
        html.Div([
            html.Div([
                html.H5(children='Number of Countries: ', style=dict(marginRight='8px')),
                dcc.Input(id="bar-limit", type="number", #placeholder="input with range",
                            min=2, max=20, value=10, style={'width': '10%'})
            ], 
            style=dict(display='flex', width='40%')
            ),
            html.H2(id='overview-heading', children='Overview Data', style=dict(marginTop='0px', width='20%')),
            html.H6('Select data view using the legends.', style=dict(marginTop='0px', width='40%', textAlign='right'))
            # dcc.Checklist(
            #     id='overview-checklist',
            #     options=[
            #         dict(label='Active Cases', value='active_cases'),
            #         dict(label='Recovered Cases', value='recovered_cases'),
            #         dict(label='Deaths', value='deaths'),
            #     ],
            #     value=['active_cases'],
            #     labelStyle=dict(display='inline-block', fontSize='1.5em', paddingRight='20px'),
            #     inputStyle=dict(height=15, width=15),
            #     style=dict(width='40%',
            #                 # paddingTop='10px'
            #                 )
            # ),
        ],
            className='bar-select-div'
        ),
        
        dcc.Graph(id='overview-graph',
                config={'displayModeBar': False},
                figure=go.Figure(layout=dict(barmode='stack',
                                            showlegend=True,
                                            xaxis={'categoryorder':'total ascending', 'gridcolor': 'rgb(121, 117, 117)'},
                                            paper_bgcolor = 'rgba(0,0,0,0)',
                                            plot_bgcolor = 'rgba(0,0,0,0)',
                                            xaxis_title="Country",
                                            yaxis_title="Number of Cases",
                                            margin={'t':0},
                                            font=dict(family="Courier New, monospace",
                                                        size=18,color='rgb(228, 241, 250)'),
                                            yaxis=dict(gridcolor='rgb(121, 117, 117)'))
                        )
        )],
        className='full-bar-div'
    ),
    
    html.Div([
        html.Div([
            html.Div([
                html.H4(children='Select Country', style=dict(width='50%')),
                dcc.Input( 
                                id="choose-country",
                                type="text",
                                value="US",
                                debounce=True,
                                style=dict(width='50%', marginRight='20px')
                                ),
                html.Button('SELECT', id='select-country', style=dict(color='rgb(228, 241, 250)')),
                
            ],
                style=dict(textAlign='left', marginBottom='1%', width='31%')
            ),
            html.H1(id='country-heading', children='Country View', style=dict(textAlign='center', width='40%', marginTop='30px'))
        ],
            style=dict(display='flex')
        ),
        dcc.Loading( type='dot', #style=dict(backgroundColor='rgb(60,60,60)'),
            children=
            html.Div([
                dcc.Graph(id='country-stats', 
                            config={'displayModeBar': False},
                            figure=go.Figure(layout=dict(margin={'l':0,'r':0,'t':0,'b':0},
                                                height=100,
                                                paper_bgcolor = 'rgba(0,0,0,0)',
                                                plot_bgcolor = 'rgba(0,0,0,0)'))
                            )
            ], className='country-indicator')
        ),
        html.Div([
            html.Div([
                dcc.Loading(id="rates-loading", style=dict(backgroundColor='rgb(60,60,60)'),
                            children=
                    html.Div([
                        # dcc.Checklist(
                        #         id='country-checklist',
                        #         options=[
                        #             dict(label='Confirmed Cases', value='confirmed_cases'),
                        #             dict(label='Recovered Cases', value='recovered_cases'),
                        #             dict(label='Deaths', value='deaths')
                        #         ],
                        #         value=['confirmed_cases'],
                        #         labelStyle=dict(display='inline-block', fontSize='1.3em', paddingRight='16px'),
                        #         inputStyle=dict(height=13, width=13),
                        #         style=dict(width='90%', textAlign='right', backgroundColor='rgba(0,0,0,0)')
                        #         ),
                        html.H6('Select data view using the legends.', style=dict(marginTop='0px', width='100%', textAlign='right')),
                        dcc.Graph(id='country-rates',
                                                    config={'displayModeBar': False},
                                                    figure=go.Figure(
                                                        layout=dict(
                                                            xaxis_title='Date', yaxis_title='Number of Cases',
                                                            showlegend=True, margin={'t':0},
                                                            paper_bgcolor = 'rgb(60, 60, 60)',
                                                            plot_bgcolor = 'rgb(60, 60, 60)',
                                                            font=dict(family="Courier New, monospace",
                                                                        size=18,color='rgb(228, 241, 250)'),
                                                            yaxis=dict(gridcolor='rgb(121, 117, 117)'),
                                                            xaxis=dict(gridcolor='rgb(121, 117, 117)',
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
                                                                                ]),bgcolor='rgb(55,55,55)',
                                                                                activecolor='rgb(95, 95, 95)',
                                                                                ),
                                                                        )
                                                                ))
                                
                                ),
                    ],
                        style=dict(backgroundColor='rgb(60,60,60)')
                    ),
                        type="dot"
                )
            ],
                className='cases-line-div'
            ),
            html.Div([
                dcc.Loading(id="pie-loading", style=dict(backgroundColor='rgb(60,60,60)'),
                            children=[dcc.Graph(id='country-pie',
                                                figure=go.Figure(layout=dict(
                                                                    margin={'l':0,'r':0,'t':0,'b':10},
                                                                    font=dict(family="Courier New, monospace",
                                                                    size=18,color='rgb(228, 241, 250)'),
                                                                    paper_bgcolor = 'rgb(60, 60, 60)',
                                                                    plot_bgcolor = 'rgb(60, 60, 60)'))
                            ),
                                html.H6('Current Distribution of Cases',
                                    style=dict(backgroundColor='rgb(60,60,60)', margin=0))
                            ],
                            type="dot"),
                
            ],
                className='pie-div'
            ),
        ],
            style=dict(display='flex')
        )
    ],
        className='country-div'
    ),
    html.H4(id='disclaimer', style=dict(padding='50px', textAlign='right', textSize='1.6em', backgroundColor='rgb(43, 33, 53)'))
])