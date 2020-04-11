import os
from datetime import datetime

from flask_caching import Cache

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import pandas as pd

from layout.layout import layout
from sql.queries import SQL

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="config/my-covid-project.json"
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dset_order = ['confirmed_cases', 'active_cases', 'recovered_cases', 'deaths']
bar_color = ['#3141bd', '#2ad8db', '#32a852', '#d12626']
color_select = dict(zip(dset_order, bar_color))

sql = SQL()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.layout = layout

cache = Cache()
cache.init_app(server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})


@cache.memoize()
def get_overview_data():
    print("Getting overview data")
    overview = sql.overview_query()
    return overview.to_json(orient='split')

@cache.memoize()
def get_global_data():
    print("Getting global data")    
    global_data = pd.DataFrame()
    for dset in dset_order:
        if dset != 'active_cases':
            global_data = pd.concat([global_data, sql.global_total(dset)], axis=1)
    return global_data.to_json(orient='split')

@cache.memoize()
def get_country_overview(country):
    print("Getting {} overview data".format(country))
    country_overview = sql.country_overview(country)
    return country_overview.to_json(orient='split')

@cache.memoize()
def get_country_data(country):
    print("Getting {} data".format(country))
    country_data = sql.country_data_query2(country)
    # country_data = pd.DataFrame()
    # for dset in dset_order:
    #     data = sql.country_data_query(country, dset)
    #     country_data = pd.concat([country_data, data], axis=1)
    return country_data.to_json(orient='split')

@app.callback(
        Output('overview-graph', 'figure'),
        [Input('overview-checklist', 'value'), Input('bar-limit', 'value')],
        [State('overview-graph', 'figure')]
    )
def update_bar(dset, limit, fig):
    ctx = dash.callback_context
    # print(ctx.triggered)
    fig['data'] = []
    if dset == []:
        raise PreventUpdate
    data = pd.read_json(get_overview_data(), orient='split')
    data = data.truncate(after=limit-1)
    dset = [value for value in dset_order if value in dset and value != 'confirmed_cases']
    x = data['country'].str.title()
    for category in dset:
        fig['data'].append(dict(dict(marker=dict(color=color_select[category])), type='bar',
                                x = x, y = data[category],
                                name = category))
    return fig


@app.callback(
    [Output('global-stats', 'figure'), Output('disclaimer', 'children')],
    [Input('title', 'children')],
    [State('global-stats', 'figure')]
)
def page_load(_, fig):
    ctx = dash.callback_context
    # print(ctx.triggered)
    fig['data'] = []
    n = 0
    global_data = pd.read_json(get_global_data(), orient='split')
    for (dset, total) in global_data.iteritems():
        fig['data'].append(dict(type='indicator',
                                mode = 'number',
                                title = dict(text=dset),
                                value = int(total),
                                domain = {'x': [n, n+0.33], 'y': [0.1,0.6]})
                            )
        n += 0.33
    disclaimer = 'Data last updated: {:%d/%m/%y}'.format(datetime.strptime(sql.last_column, '_%m_%d_%y'))
    return fig, disclaimer


@app.callback(
    [Output('country-store', 'data'), Output('country-pie', 'figure'),
    Output('country-checklist', 'value'), Output('country-heading', 'children'),
    Output('choose-country', 'value')],
    [Input('select-country', 'n_clicks'), Input('overview-graph', 'clickData')],
    [State('choose-country', 'value'), State('country-pie', 'figure')]
)
def update_country(_, clickData, country, fig):
    dset = ['confirmed_cases']
    ctx = dash.callback_context
    # print(ctx.triggered)
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'select-country' and country != '':
        selected_country = country
    elif clickData is not None:
        selected_country = clickData['points'][0]['label']
    else: 
        selected_country = 'Us'
    return (selected_country, update_pie(selected_country, fig),
            dset, selected_country, selected_country)


@app.callback(
    Output('country-rates', 'figure'),
    [Input('country-checklist', 'value')],
    [State('country-store', 'data'), State('country-rates', 'figure')]
)
def update_line_dsets(dset, country, fig):
    ctx = dash.callback_context
    # print(ctx.triggered)
    if (ctx.triggered[0]['value'] is None
        or dset == []):
        raise PreventUpdate
    print("Update line called")
    return update_line(dset, country, fig)


def update_pie(country, fig):
    country = country.upper()
    data = get_pie_data(country)
    country = data.pop('country').iloc[0]
    data = data.drop('confirmed_cases', axis=1)
    labels = data.columns.values.tolist()
    fig['data'] = [dict(type='pie',
                    labels=labels,
                    values=data.iloc[0],
                    sort=False,
                    marker=dict(colors=[color_select[i] for i in labels])
                    )]
    fig['layout']['title'] = '{} Cases'.format(country.title())
    return fig

def get_pie_data(country):
    overview_data = pd.read_json(get_overview_data(), orient='split')
    if country not in overview_data['country'].values:
        print("Fetching Data...")
        result = pd.read_json(get_country_overview(country), orient='split')
        if result is None:
            print("Data not found")
            raise PreventUpdate
    else:
        result = overview_data.loc[overview_data['country'] == country]
    return result


def update_line(dsets, country, fig):
    layout = fig['layout']
    layout['title'] = "{} Cases".format(country)
    layout['xaxis']['rangeslider'] = {'visible': True}
    data = pd.read_json(get_country_data(country), orient='split')
    fig = go.Figure()
    for dset in dsets:
        y = data.loc[dset]
        y = y[y!=0]
        x = pd.to_datetime(y.index)
        fig.add_trace(go.Scatter(
                                x= x,
                                y= y,
                                name=dset,
                                line=dict(color=color_select[dset])
        ))
    fig.update_layout(layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
