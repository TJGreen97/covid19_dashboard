"""COVID19 Dashboard by Torran Green

All data is sourced from the Johns Hopkins University open dataset on GitHub.
This dashboard is for educational use.
----------------------------------------------------------------------------------------
Module handles all Postgres DB tasks.
    Creates and queries tables.

Returns:
    [type] -- [description]
"""
import os
import logging as log

import pandas as pd
from sqlalchemy import create_engine


class PostgresDB:
    def __init__(self, dsets=["confirmed_cases", "recovered_cases", "deaths"]):
        self.DATABASE_URL = os.environ["DATABASE_URL"]
        self.engine = create_engine(self.DATABASE_URL)
        self.dsets = dsets

    def create_tables(
        self,
        url="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_{}_global.csv",
    ):
        """Creates the tables within the Postgres DB.
           Heroku is scheduled to call this function at 3am every day.

        Keyword Arguments:
            url {str} -- source of raw data
        """
        for dset in self.dsets:
            log.info("Dataset: {}".format(dset))
            git_dset = dset.split("_")[0]
            log.info("Reading Dataset.")
            df = pd.read_csv(url.format(git_dset))
            log.info("Dataset Read, Formatting...")
            (df, transposed_df) = self.format_df(df)
            log.info("Writing {} Table".format(dset))
            df.to_sql(dset, self.engine, if_exists="replace")
            log.info("Writing {}_T Table".format(dset))
            transposed_df.to_sql("{}_T".format(dset), self.engine, if_exists="replace")

    def format_df(self, df):
        df.columns = df.columns.str.replace("/", "_")
        df.columns = df.columns.str.lower()
        df.columns = [("_" + col) if col[0].isnumeric() else col for col in df.columns]
        transposed_df = df.copy()
        transposed_df.drop(["province_state", "lat", "long"], axis=1, inplace=True)
        transposed_df = transposed_df.groupby(["country_region"]).sum().T
        transposed_df = self.clean_data(transposed_df)
        return df, transposed_df

    @staticmethod
    def clean_data(df):
        df.columns = [
            name.strip()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("'", "_")
            .replace("*", "")
            .lower()
            for name in df.columns
        ]
        df.rename(
            columns={
                "congo_(brazzaville)": "congo",
                "congo_(kinshasa)": "congo",
                "korea,_south": "south_korea",
            },
            inplace=True,
        )
        df = df.groupby(df.columns, axis=1).sum()
        df.reset_index(inplace=True)
        df.rename(columns={"index": "date"}, inplace=True)
        df.reset_index(inplace=True)
        return df


class PostgresQueries(PostgresDB):
    def __init__(self):
        PostgresDB.__init__(self)
        self.last_columns = self.find_last_columns()
        print(self.last_columns)

    def find_last_columns(self):
        """Determines the last columns added to the tables.

        Returns:
            Series -- two most recent dates.
        """
        with open("sql/last_column_query.txt", "r") as file:
            sql = file.read()
        try:
            out = pd.read_sql_query(sql, self.engine)
            out = out['column_name'].str.split(pat='_', expand=True).drop([0], axis=1)
            out = out.loc[out[3] == out[3].max()]
            out = out.loc[out[1] == out[1].max()]
            out[2] = out[2].astype(int)
            out = out.sort_values(by=[2], ascending=False)[0:2].astype(str).reset_index()
            out['column_name'] = '_' + out[1] + '_' + out[2] + '_' + out[3]
            return out["column_name"]
        except Exception:
            log.error("Last column not found")
            return ""

    def overview_query(self):
        """Query to retrieve the data of the 20 worst affected countries.

        Returns:
            dataframe -- overview data
        """
        with open("sql/overview_query.txt", "r") as file:
            sql = file.read()
        sql = sql.format(
            "%%", date=self.last_columns.iloc[0], ref=self.last_columns.iloc[1]
        )
        try:
            overview = pd.read_sql_query(sql, self.engine)
            return overview
        except Exception:
            log.error("Overview Query Failed")
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
        """Queries all time series data for a specified country.

        Arguments:
            country {string} -- country to query

        Returns:
            dataframe -- dataframe of country data
        """
        with open("sql/country_query.txt", "r") as file:
            sql = file.read()
        sql = sql.format(country=country.lower())
        try:
            results = pd.read_sql_query(sql, self.engine)
        except Exception:
            log.error("Data unavailable")
            return pd.DataFrame()
        results["date"] = pd.to_datetime(results["date"], format="_%m_%d_%y")
        results.set_index("date", inplace=True)
        results.drop_duplicates(inplace=True)
        return results


if __name__ == "__main__":
    DB = PostgresDB()
    DB.create_tables()
