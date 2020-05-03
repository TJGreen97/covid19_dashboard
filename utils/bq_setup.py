import pandas_gbq
import pandas as pd
import os
from datetime import datetime
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/my-covid-project.json"


class BQ:
    def __init__(self):
        self.dsets = ['confirmed_cases', 'recovered_cases', 'deaths']

    def create_bq(self):
        for dset in self.dsets:
            df = pandas_gbq.read_gbq("""SELECT *
                                    FROM jhu_covid_dset.{}
                                    """.format(dset))
            df.drop(['province_state', 'lat', 'long'], axis=1, inplace=True)
            df = df.groupby(['country_region']).sum().T
            df = self.clean_data(df)
            # df.drop(df.tail(1).index, inplace=True)
            pandas_gbq.to_gbq(df, 'torran_covid_dset.{}'.format(dset), if_exists='replace')
        return

    # def update_bq(self, last_column):
    #     public_date = datetime.strptime(last_column, "_%m_%d_%y")
    #     for dset in self.dsets:
            
    #         index_date = pandas_gbq.read_gbq("""SELECT index, date
    #                                     FROM torran_covid_dset.{}
    #                                     ORDER BY index DESC
    #                                     limit 1""".format(dset))
    #         # print(index_date.loc[0, 'date'])
    #         # print(last_column)
    #         private_date = datetime.strptime(index_date['date'].iloc[0], "_%m_%d_%y")
    #         if private_date >= public_date:
    #             print("{} Up to date".format(dset))
    #             continue
        
    #         new_confirmed = pandas_gbq.read_gbq("""
    #                                             SELECT country_region, SUM({date}) as {date}
    #                                             FROM jhu_covid_dset.{dset}
    #                                             GROUP BY country_region
    #                                             """.format(date=last_column, dset=dset))
    #         # print(new_confirmed)
    #         new_confirmed = new_confirmed.set_index('country_region').T
    #         df = self.clean_data(new_confirmed)
    #         df.loc[0, 'index'] = index_date.loc[0, 'index'] + 1
    #         # print(df)
    #         pandas_gbq.to_gbq(df, 'torran_covid_dset.{}'.format(dset), if_exists='append')
    #     return

    @staticmethod
    def clean_data(df):
        df.columns = [name.strip().replace(' ', '_').replace('-', '_').replace("'", '_').replace('*', '').lower() for name in df.columns]
        df.rename(columns={
            'congo_(brazzaville)': 'congo',
            'congo_(kinshasa)': 'congo',
            'korea,_south': 'south_korea',
            }, inplace=True)
        df = df.groupby(df.columns, axis=1).sum()
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'date'}, inplace=True)
        df.reset_index(inplace=True)
        return df

    def github_dataset(self):
        url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_{}_global.csv"
        for dset in self.dsets:
            git_dset = dset.split("_")[0]
            df = pd.read_csv(url.format(git_dset))
            df.columns = df.columns.str.replace("/", "_")
            df.columns = df.columns.str.lower()
            df.columns = [("_" + col) if col[0].isnumeric() else col for col in df.columns]
            pandas_gbq.to_gbq(df, 'jhu_covid_dset.{}'.format(dset), if_exists='replace')
        return


if __name__ == '__main__':
    bq = BQ()
    bq.github_dataset()
    bq.create_bq()
