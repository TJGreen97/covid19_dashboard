"""
COVID19 Dashboard by Torran Green

All data is queried from the Johns Hopkins University open dataset on Google's BigQuery.
This dashboard is for educational use.
----------------------------------------------------------------------------------------
Main module, including all callbacks and cached functions.
"""
import os
import logging as log
from datetime import datetime
from flask_caching import Cache

import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import pandas as pd

from layout.layout import layout
from sql.queries import SQL

# log.getLogger().setLevel(log.INFO)
log.basicConfig(filename='logs\\covid-dash.log', level=log.DEBUG)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/my-covid-project.json"
dset_order = ["confirmed_cases", "active_cases", "recovered_cases", "deaths"]
bar_color = ["#7B4D80", "#3D8EDE", "#84CA72", "#D8555C"]
color_select = dict(zip(dset_order, bar_color))

sql = SQL()

app = dash.Dash(__name__)
server = app.server
app.layout = layout
app.title = "COVID19-Torran"
cache = Cache()
cache.init_app(
    server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "cache-directory"}
)


@cache.memoize()
def get_overview_data():
    """Cached function to fetch summarised data of the top 20 countries.
    Summarised data: confirmed_cases, recovered_cases, deaths, active_cases

    Returns:
        json -- dataframe of top 20 countries overview data, stored in json for cache.
    """
    log.info("Getting overview data")
    # print("Getting overview data")
    overview = sql.overview_query()
    return overview.to_json(orient="split")


@cache.memoize()
def get_global_data():
    """Cached function to fetch summarised global data of all countries.

    Returns:
        json -- dataframe of summarised global data
    """
    log.info("Getting global data")
    # print("Getting global data")
    global_data = sql.global_total()
    return global_data.to_json(orient="split")


@cache.memoize()
def get_country_data(country):
    country_data = sql.country_query(country)
    return country_data.to_json(orient="split")

# @cache.memoize()
# def get_country_overview(country):
#     """Cached function to retrieve summarised data for a specific country.

#     Arguments:
#         country {string}

#     Returns:
#         json -- dataframe of summarised data
#     """
#     log.info("Getting {} overview data".format(country))
#     # print("Getting {} overview data".format(country))
#     country_overview = sql.country_overview(country)
#     return country_overview.to_json(orient="split")


# @cache.memoize()
# def get_country_data(country):
#     """Cached function to retrieve all data on a specific country.

#     Arguments:
#         country {string}

#     Returns:
#         json -- dataframe of country data
#     """
#     log.info("Getting {} data".format(country))
#     # print("Getting {} data".format(country))
#     country_data = sql.country_data_query(country)
#     return country_data.to_json(orient="split")


@app.callback(
    Output("overview-graph", "figure"),
    [Input("bar-limit", "value")],
    [State("overview-graph", "figure")],
)
def update_bar(limit, fig):
    """Callback to update the bar chart when the slider input is changed.

    Arguments:
        limit {int} -- slider valued between 2 and 20 inclusive
        fig {dict} -- current bar chart; used to determine layout

    Raises:
        PreventUpdate: Prevents the bar chart update if limit is out of bounds

    Returns:
        dict -- figure dict for the updated bar chart
    """
    fig["data"] = []
    if limit is None or limit < 2 or limit > 20:
        raise PreventUpdate
    data = pd.read_json(get_overview_data(), orient="split")
    data = data.truncate(after=limit - 1)
    dset = [value for value in dset_order if value != "confirmed_cases"]
    x = data["country"].str.title()
    for category in dset:
        fig["data"].append(
            dict(
                dict(marker=dict(color=color_select[category], line={"width": "0"})),
                type="bar",
                x=x,
                y=data[category],
                name=category,
                hovertext="Click for more information.",
                hoverinfo="y+name",
            )
        )
    return fig


@app.callback(
    [Output("global-stats", "figure"), Output("disclaimer", "children")],
    [Input("title", "children")],
    [State("global-stats", "figure")],
)
def page_load(_, fig):
    """Callback called on page load, updates the global statistics and footer

    Arguments:
        _ {string} -- necessary to fire callback
        fig {dict} -- figure dict of current global stats; used for layout

    Returns:
        dict -- figure dict of global statistics indicators
        string -- footer information/disclaimer
    """
    fig["data"] = []
    n = 0
    global_data = pd.read_json(get_global_data(), orient="split")
    for dset in dset_order:
        fig["data"].append(
            dict(
                type="indicator",
                mode="number+delta",
                title=dict(text=dset, font={"color": "#83B7EA"}),
                value=int(global_data.iloc[1][dset]),
                number=dict(font={"color": "#83B7EA"}),
                delta={
                    "reference": int(global_data.iloc[0][dset]),
                    "increasing": {"color": "rgb(228, 241, 250)"},
                    "decreasing": {"color": "rgb(228, 241, 250)"},
                },
                domain={"x": [n, n + 0.25], "y": [0.1, 0.6]},
            )
        )
        n += 0.25
    disclaimer = "Data last updated: {:%d/%m/%y}".format(
        datetime.strptime(sql.last_column, "_%m_%d_%y")
    )
    return fig, disclaimer


@app.callback(
    [
        Output("country-heading", "children"),
        Output("choose-country", "value"),
        Output("country-store", "data"),
        Output("country-stats", "figure"),
        Output("country-total", "figure"),
        Output("country-rates", "figure"),
        Output("country-pie", "figure"),
    ],
    [Input("select-country", "n_clicks"), Input("overview-graph", "clickData")],
    [
        State("choose-country", "value"),
        State("country-stats", "figure"),
        State("country-total", "figure"),
        State("country-rates", "figure"),
        State("country-pie", "figure")
    ],
)
def update_country(_, clickData, country, stats_fig, total_fig, rates_fig, pie_fig):
    """Callback to update the country displayed in the country view.

    Arguments:
        _ {int} -- fires callback on submit button press
        clickData {dict} -- bar chart click data for selected country
        country {string} -- input text box value
        pie_fig {dict} -- figure dict of current pie chart
        stats_fig {dict} -- figure dict of current indicator chart
        total_fig {dict} -- figure dict of current line chart

    Returns:
        tuple -- necessary updates for new country, calls functions to update figures
    """
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"].split(".")[0] == "select-country" and country != "":
        if country.title() == "Uk":
            selected_country = "United Kingdom"
        else:
            selected_country = country.title()
    elif clickData is not None:
        selected_country = clickData["points"][0]["label"]
    else:
        selected_country = "US"

    if selected_country == 'Korea, South':
        selected_country = "south korea"
    country_display = selected_country.title()
    if country_display == "Us":
        country_display = "US"

    selected_country = selected_country.strip().replace(' ', '_').replace('-', '_').replace("'", '_').replace('*', '').lower()
    data = pd.read_json(get_country_data(selected_country), orient="split")
    return (
        country_display,
        country_display,
        selected_country,
        update_country_stats(data, stats_fig),
        update_line(data, total_fig),
        update_rates_bar(data, rates_fig),
        update_pie(data, pie_fig),
    )


def update_pie(data, fig):
    """function to update the cases distribution pie chart

    Arguments:
        data {dataframe} -- dataframe generated by get_country_totals()
        fig {dict} -- figure dict for current pie chart; used for layout

    Returns:
        dict -- updated figure dict
    """
    labels = ["active_cases", "recovered_cases", "deaths"]
    
    data = data[labels]
    fig["data"] = [
        dict(
            type="pie",
            labels=labels,
            values=data.iloc[-1],
            sort=False,
            marker=dict(colors=[color_select[i] for i in labels]),
            outsidetextfont=dict(color="rgb(228, 241, 250)"),
            insidetextfont=dict(color="rgb(228, 241, 250)"),
            hoverlabel={
                "bordercolor": "rgb(228,241,250)",
                "font": {"color": "rgb(228, 241, 250)"},
            },
        )
    ]
    return fig


# def get_country_totals(country):
#     """Retrieves overviews of desired country by checking cached functions.

#     Arguments:
#         country {string} -- required country

#     Raises:
#         PreventUpdate: prevents figure updates if data retrieval fails

#     Returns:
#         dataframe -- dataframe of overview data of required country
#     """
#     overview_data = pd.read_json(get_overview_data(), orient="split")
#     if country not in overview_data["country"].values:
#         log.info("Fetching {} totals.".format(country))
#         # print("Fetching Data...")
#         result = pd.read_json(get_country_overview(country), orient="split")
#         if result is None:
#             log.error("{} data not found".format(country))
#             raise PreventUpdate
#     else:
#         result = overview_data.loc[overview_data["country"] == country]
#     return result


def update_line(data, fig):
    """Updates cummulative line graph.

    Arguments:
        country {string} -- required country
        fig {dict} -- figure dict of current line chart; used for layout

    Returns:
        dict -- figure dict of updated line chart
    """
    layout = fig["layout"]
    fig = go.Figure()
    for dset in dset_order:
        y = data[dset]
        y = y[y != 0]
        x = y.index
        fig.add_trace(
            go.Scatter(
                x=x, y=y, name=dset, line=dict(color=color_select[dset], width=4)
            )
        )
    fig.update_layout(layout)
    return fig


def update_country_stats(data, fig):
    """Updates country specific overview statistics

    Arguments:
        country {string} -- required country
        data {dataframe} -- dataframe of country overview data
        fig {dict} -- figure dict of current indicator; used for layout

    Returns:
        dict -- figure dict of updated indicator chart
    """
    fig["data"] = []
    n = 0
    for dset in dset_order:
        fig["data"].append(
            dict(
                type="indicator",
                mode="number+delta",
                title=dict(text=dset, font={"color": "#83B7EA"}),
                value=int(data.loc[data.index[-1], dset]),
                number=dict(font={"color": "#83B7EA"}),
                delta={
                    "reference": int(data.loc[data.index[-2], dset]),
                    "increasing": {"color": "rgb(228, 241, 250)"},
                    "decreasing": {"color": "rgb(228, 241, 250)"},
                },
                domain={"x": [n, n + 0.25], "y": [0.1, 0.6]},
            )
        )
        n += 0.25
    return fig


def update_rates_bar(data, fig):
    fig["data"] = []

    for dset in dset_order:
        y = data[dset].diff()
        y = y[y != 0]
        y.dropna(inplace=True)
        x = y.index
        fig["data"].append(
            dict(
                dict(marker=dict(color=color_select[dset], line={"width": "0"})),
                type="bar",
                opacity='0.75',
                x=x,
                y=y,
                name=dset,
                hoverinfo="x+y",
            )
        )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
