"""
COVID19 Dashboard by Torran Green

All data is queried from the Johns Hopkins University open dataset on Google's BigQuery.
This dashboard is for educational use.
----------------------------------------------------------------------------------------
Module containing the SQL class which controls all queries to BigQuery.
"""
import logging as log
from google.cloud import bigquery
import pandas_gbq
from google.api_core.exceptions import BadRequest
from datetime import datetime, timedelta
import platform
import pandas as pd
from utils.bq_setup import BQ


class SQL(BQ):
    def __init__(self):
        """Handles all queries to Google's BigQuery.
        """
        self.dsets = ['confirmed_cases', 'recovered_cases', 'deaths']
        self.client = bigquery.Client()
        self.sql_overview = open("sql/sql_overview.txt", "r").read()
        self.last_column = self._get_last_db_column()
        self.update_bq(self.last_column)

    @staticmethod
    def _get_time_format():
        """Determines which time formatting to use based on OS.
        """
        if platform.system() == "Windows":
            time_format = "_%#m_%#d_%y"
        else:
            time_format = "_%-m_%-d_%y"
        return time_format

    def _get_last_db_column(self):
        """Determines the last row of the database by attempting queries starting with
        the current date.

        Returns:
            string -- column value of last column in database
        """
        date_attempt = (datetime.now()).strftime(self._get_time_format())
        sql = open("sql/test_query.txt", "r").read()
        n = 0
        while n < 5:
            log.debug("Date attempt: {}".format(date_attempt))
            sql_attempt = sql.format(date_attempt)
            log.debug("Formatted SQL Test: {}".format(sql_attempt))
            try:
                self.client.query(sql_attempt).to_dataframe()
                break
            except BadRequest:
                date_attempt = (
                    datetime.strptime(date_attempt, "_%m_%d_%y") - timedelta(1)
                ).strftime(self._get_time_format())
            n += 1
        # TO DO: raise an error
        return date_attempt

    def _second_last_column(self):
        """Determines second last column in database for referencing recent daily changes.
        """
        return (
            datetime.strptime(self.last_column, "_%m_%d_%y") - timedelta(1)
        ).strftime(self._get_time_format())

    def overview_query(self):
        """Queries for an overview of the top 20 countries.

        Returns:
            dataframe -- overview of top 20 countries
        """
        log.info("Making overview query")
        overview = []
        sql = self.sql_overview.format(
            "%", date=self.last_column, ref=self._second_last_column()
        )
        try:
            overview = self.client.query(sql).to_dataframe()
        except BadRequest:
            log.warning("Data unavailable")
            return []
        return overview

    def global_total(self):
        """Queries global totals from all datasets.

        Returns:
            dataframe -- dataframe of global totals
        """
        sql = open("sql/global_total.txt", "r").read()
        sql = sql.format(date=self.last_column, ref=self._second_last_column())
        log.debug("SQL: {}".format(sql))
        try:
            result = self.client.query(sql).to_dataframe()
        except BadRequest:
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
        sql = open("sql/sql_country.txt", "r").read()
        sql = sql.format(country=country.lower())
        try:
            results = self.client.query(sql).to_dataframe()
        except BadRequest:
            log.warning("Data unavailable")
            return pd.DataFrame()
        results['date'] = pd.to_datetime(results['date'], format="_%m_%d_%y")
        results.set_index("date", inplace=True)
        results.drop_duplicates(inplace=True)
        return results
