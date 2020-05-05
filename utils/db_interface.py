import os
import logging as log

import pandas as pd
from sqlalchemy import create_engine


class PostgresDB:
    def __init__(self, dsets=['confirmed_cases', 'recovered_cases', 'deaths']):
        self.DATABASE_URL = os.environ['DATABASE_URL']
        # self.DATABASE_URL = "postgres://aupleyoffwsamv:3dd3df5cfa3dbdf524eae4dc1476e1041b61844bbe399e2652d30775225228ac@ec2-54-217-204-34.eu-west-1.compute.amazonaws.com:5432/da8kr727vlcqa4"
        self.engine = create_engine(self.DATABASE_URL)
        self.dsets = dsets

    def create_tables(self, url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_{}_global.csv"):
        for dset in self.dsets:
            print("Dataset: {}".format(dset))
            git_dset = dset.split("_")[0]
            print("Reading Dataset.")
            df = pd.read_csv(url.format(git_dset))
            print("Dataset Read, Formatting...")
            (df, transposed_df) = self.format_df(df)
            print("Writing {} Table".format(dset))
            df.to_sql(dset, self.engine, if_exists="replace")
            print("Writing {}_T Table".format(dset))
            transposed_df.to_sql("{}_T".format(dset), self.engine, if_exists="replace")

    def format_df(self, df):
        df.columns = df.columns.str.replace("/", "_")
        df.columns = df.columns.str.lower()
        df.columns = [("_" + col) if col[0].isnumeric() else col for col in df.columns]
        transposed_df = df.copy()
        transposed_df.drop(['province_state', 'lat', 'long'], axis=1, inplace=True)
        transposed_df = transposed_df.groupby(['country_region']).sum().T
        transposed_df = self.clean_data(transposed_df)
        return df, transposed_df

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


class PostgresQueries(PostgresDB):
    def __init__(self):
        PostgresDB.__init__(self)
        self.last_columns = self.find_last_columns()

    def find_last_columns(self):
        with open("sql/last_column_query.txt", "r") as file:
            sql = file.read()
        try:
            out = pd.read_sql_query(sql, self.engine)
            return out['column_name']
        except Exception:
            print("Last column not found")
            return ''

    def overview_query(self):
        with open("sql/sql_overview_query.txt", "r") as file:
            sql = file.read()
        sql = sql.format("%%", date=self.last_columns.iloc[0], ref=self.last_columns.iloc[1])
        try:
            overview = pd.read_sql_query(sql, self.engine)
            return overview
        except Exception:
            print("Overview Query Failed")
            return []

    def global_total(self):
        """Queries global totals from all tables.

        Returns:
            dataframe -- dataframe of global totals
        """
        with open("sql/global_total_query.txt", "r") as file:
            sql = file.read()
        sql = sql.format(date=self.last_columns.iloc[0], ref=self.last_columns.iloc[1])
        log.debug("SQL: {}".format(sql))
        try:
            result = pd.read_sql_query(sql, self.engine)
        except Exception:
            log.error("Global Total Data Unavailable")
            return []
        log.debug("Global total result: {}".format(result))
        result = result.pivot(index="id", columns="dset", values="totals")
        log.debug("Global total result pivotted: {}".format(result))
        active = pd.DataFrame()
        active["active_cases"] = (
            result["confirmed_cases"] - result["deaths"] - result["recovered_cases"]
        )
        result = pd.concat([result, active], axis=1)
        log.debug("Global total final result: {}".format(result))
        return result

    def country_query(self, country):
        with open("sql/sql_country_query.txt", "r") as file:
            sql = file.read()
        sql = sql.format(country=country.lower())
        try:
            results = pd.read_sql_query(sql, self.engine)
        except Exception:
            log.warning("Data unavailable")
            return pd.DataFrame()
        results['date'] = pd.to_datetime(results['date'], format="_%m_%d_%y")
        results.set_index("date", inplace=True)
        results.drop_duplicates(inplace=True)
        return results


if __name__ == "__main__":
    DB = PostgresDB()
    DB.create_tables()
