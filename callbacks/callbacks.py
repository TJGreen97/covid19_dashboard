from dash.dependencies import Output, Input, State


def register_callbacks(app):
    
    @app.callback(
        [Output('global-stats', 'figure'),
        Output('disclaimer', 'children')],
        [Input('title', 'children')],
        [State('global-stats', 'figure')]
    )
    def page_load(children, fig):
        fig.data = []
        n = 0
        for dset in dset_order:
            fig.add_trace(go.Indicator(
                mode = 'number',
                title = dict(text=dset),
                value = int(cq.global_query(dset).iloc[0]),
                domain = {'x': [n, n+0.33], 'y': [0.1,0.6]}
            ))
            n += 0.33
        disclaimer = 'Data last updated: {:%d/%m/%y}'.format(datetime.strptime(cq.last_column, '_%m_%d_%y'))
        return fig, disclaimer



    @app.callback(
        Output('overview-graph', 'figure'),
        [Input('overview-checklist', 'value'),
        Input('bar-limit', 'value')],
        [State('overview-graph', 'figure')]
    )
    def update_bar(dset, limit, fig):
        fig.data = []
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
        
        return fig



    @app.callback(
        [Output('country-pie', 'figure'),
        Output('country-checklist', 'value'),
        Output('country-heading', 'children'),
        Output('choose-country', 'value')],
        [Input('select-country', 'n_clicks'),
        Input('overview-graph', 'clickData')],
        [State('choose-country', 'value')]
    )
    def update_country(_, clickData, country):
        print("start of update country {}".format(cv.country))
        dset = ['confirmed_cases']
        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'select-country' and country != '':
            cv.country = country
        elif clickData is not None:
            cv.country = clickData['points'][0]['label']
        print("end of update country {}".format(cv.country))
        return cv.update_pie(), dset, cv.country.title(), cv.country.title()


    @app.callback(
        Output('country-rates', 'figure'),
        [Input('country-checklist', 'value')],
        [State('country-heading', 'children')]
    )
    def update_dset(dset, country):
        print(cv)
        print("start of update dset {}".format(cv.country))
        ctx = dash.callback_context
        print("checklist changed")
        print(ctx.triggered)
        if ctx.triggered[0]['value'] is None:
            raise PreventUpdate
        else:
            print("middle of update dset {}".format(cv.country))
            print(dset)
            cv.country = country
            print("end of update dset {}".format(cv.country))
            return cv.update_line(dset)