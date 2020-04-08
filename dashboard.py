# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from sql_test import CovidQuery
# from country_data import CountryView
import pandas as pd
from datetime import datetime
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="config/my-covid-project.json"

dset_order = ['confirmed_cases', 'recovered_cases', 'deaths']
bar_color = ['#3141bd', '#32a852', '#d12626']
color_select = dict(zip(dset_order, bar_color))


cq = CovidQuery()

class CountryView:
    def __init__(self):
        self.country = 'Us'
        print("cv has been initialised")

    def update_line(self, dsets):
        fig = go.Figure()
        if dsets == []:
            return fig
        for dset in dsets:
            print("line country: {}".format(self.country))
            print(dset)
            print(cq.country_data)
            if (cq.country_data[dset] is None) or (self.country.title() not in cq.country_data[dset].columns):
                print("Fetching {}'s '{}' Data...".format(self.country, dset))
                data = cq.country_query(dset, self.country)
                print('Data Fetched')
            else:
                data = cq.country_data[dset][self.country.title()]
            data = data[data!=0]
            fig.add_trace(go.Scatter(
                x= pd.to_datetime(data.index),
                y= data,
                name=dset,
                line=dict(color=color_select[dset])))
        
        fig.update_layout(title='{} Cases'.format(data.name),
                        xaxis_title='Date',
                        yaxis_title='Number',
                        showlegend=True,
                        xaxis=dict(tickformat = '%d/%m/%y',
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
                                        visible = True
                                    ),
                        )
        )
        return fig

    def update_pie(self):
        print("pie country: {}".format(self.country))
        self.country = self.country.upper()
        data = self.get_pie_data()
        labels = data.columns.values.tolist()
        fig = go.Figure()
        fig.add_trace(go.Pie(
                        labels=labels,
                        values=data.iloc[0],
                        sort=False,
                        marker=dict(colors=[color_select[i] for i in labels])
                        ))
        fig.update_layout(title='{} Cases'.format(self.country.title()))
        return fig

    def get_pie_data(self):
        if self.country not in cq.overview['country'].values:
            print("Fetching Data...")
            result = cq.get_country(self.country)
            if result.empty:
                raise PreventUpdate
        data = cq.overview
        data = data.loc[data['country'] == self.country]
        data = data.drop('country', axis=1)
        return data






cv = CountryView()
print("does it do everything twice?")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


app.layout = html.Div(children=[
    
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
                        config={'displayModeBar': False})
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
    
    dcc.Graph(id='overview-graph'),
    
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
                                    # value=['confirmed_cases'],
                                    labelStyle=dict(display='inline-block'),
                                    style=dict(width='30%',
                                                paddingTop='10px',
                                                textAlign='right')
                                    ),
                            dcc.Loading(id="rates-loading",
                                    children=dcc.Graph(id='country-rates'),
                                    type="circle"),
                        ],
                            style=dict(width='70%')
                        ),
                        html.Div([
                            dcc.Loading(id="pie-loading",
                                        children=dcc.Graph(id='country-pie'),
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


@app.callback(
    [dash.dependencies.Output('global-stats', 'figure'),
    dash.dependencies.Output('disclaimer', 'children')],
    [dash.dependencies.Input('title', 'children')]
)
def page_load(children):
    fig = go.Figure()
    n = 0
    for dset in dset_order:
        fig.add_trace(go.Indicator(
            mode = 'number',
            title = dict(text=dset),
            value = int(cq.global_query(dset).iloc[0]),
            domain = {'x': [n, n+0.33], 'y': [0.1,0.6]}
        ))
        n += 0.33
    fig.update_layout(margin={'l':0,'r':0,'t':0,'b':0},
                    height=100,
                    paper_bgcolor = 'rgba(0,0,0,0)')
    disclaimer = 'Data last updated: {:%d/%m/%y}'.format(datetime.strptime(cq.last_column, '_%m_%d_%y'))
    return fig, disclaimer



@app.callback(
    dash.dependencies.Output('overview-graph', 'figure'),
    [dash.dependencies.Input('overview-checklist', 'value'),
     dash.dependencies.Input('bar-limit', 'value')])
def update_bar(dset, limit):
    fig = go.Figure()
    if dset == []:
        return fig
    data = cq.overview.truncate(after=limit-1)
    dset = [value for value in dset_order if value in dset]
    x = data['country'].str.title()
    for category in dset:
        fig.add_trace(go.Bar(
            x = x,
            y = data[category],
            name = category,
            marker_color=color_select[category]))
    
    fig.update_layout(title = 'Country Overview',
                      barmode='stack',
                      showlegend=True,
                      xaxis={'categoryorder':'total ascending'})
    
    return fig



@app.callback(
    [dash.dependencies.Output('country-pie', 'figure'),
    dash.dependencies.Output('country-checklist', 'value'),
    dash.dependencies.Output('country-heading', 'children'),
    dash.dependencies.Output('choose-country', 'value')],
    [dash.dependencies.Input('select-country', 'n_clicks'),
    dash.dependencies.Input('overview-graph', 'clickData')],
    [dash.dependencies.State('choose-country', 'value')]
)
def update_country(_, clickData, country):
    dset = ['confirmed_cases']
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'select-country' and country != '':
        cv.country = country
    elif clickData is not None:
        cv.country = clickData['points'][0]['label']
    print(cv.country)
    return cv.update_pie(), dset, cv.country.title(), cv.country.title()


@app.callback(
    dash.dependencies.Output('country-rates', 'figure'),
    [dash.dependencies.Input('country-checklist', 'value')]
)
def update_dset(dset):
    ctx = dash.callback_context
    print("checklist changed")
    print(ctx.triggered[0])
    if ctx.triggered[0]['value'] is None:
        raise PreventUpdate
    else:
        print("checklist country: {}".format(cv.country))
        print(dset)
        return cv.update_line(dset)





print("what does it do with this?")

if __name__ == '__main__':
    app.run_server(debug=True)
