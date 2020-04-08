import pandas as pd
import 
class CountryView:
    def __init__(self):
        self.country = 'Us'

    def update_line(self, dsets):
        fig = go.Figure()
        if dsets == []:
            return fig
        for dset in dsets:
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