"""
COVID19 Dashboard by Torran Green

All data is queried from the Johns Hopkins University open dataset on Google's BigQuery.
This dashboard is for educational use.
----------------------------------------------------------------------------------------
Module containing the SQL class which controls all queries to BigQuery.
"""
import logging as log
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
from datetime import datetime, timedelta
import platform
import pandas as pd


class SQL:
    def __init__(self):
        """Handles all queries to Google's BigQuery.
        """
        self.client = bigquery.Client()
        self.sql_overview = open("sql/sql_overview.txt", "r").read()
        self.last_column = self._get_last_db_column()

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
            try:
                sql = sql.format(date_attempt)
                self.client.query(sql).to_dataframe()
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
        # print("Making overview query")
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
        try:
            result = self.client.query(sql).to_dataframe()
        except BadRequest:
            log.error("Global Total Data Unavailable")
            return []
        result = result.pivot(index="id", columns="dset", values="totals")
        active = pd.DataFrame()
        active["active_cases"] = (
            result["confirmed_cases"] - result["deaths"] - result["recovered_cases"]
        )
        result = pd.concat([result, active], axis=1)
        return result

    def country_overview(self, country):
        """Queries a summarised overview of a selected country.

        Arguments:
            country {string} -- required country

        Returns:
            dataframe -- dataframe of country overview
        """
        sql = self.sql_overview.format(
            country.upper(), date=self.last_column, ref=self._second_last_column()
        )
        try:
            result = self.client.query(sql).to_dataframe()
        except BadRequest:
            log.error("Overview Data Unavailable")
            return []
        log.info("Collected data for: {}".format(result["country"].values))
        return result

    def country_data_query(self, country):
        """Queries all cases data for required country

        Arguments:
            country {string} -- required country

        Returns:
            dataframe -- dataframe of country data
        """
        date_list = self._get_date_list()
        date_string = ", ".join(["SUM(" + x + ") AS " + x for x in date_list])
        sql = open("sql/country_data.txt", "r").read()
        sql = sql.format(date_list=date_string, country=country.upper())
        try:
            results = self.client.query(sql).to_dataframe()
        except BadRequest:
            log.warning("Data unavailable")
            return []
        results.set_index("dset", inplace=True)
        results.columns = pd.to_datetime(results.columns, format="_%m_%d_%y")
        return results

    def _get_date_list(self):
        """Produces a correctly formatted list of all dates included in dataset;
        using known start date.

        Returns:
            list -- list of strings of dates
        """
        last_date = datetime.strptime(self.last_column, "_%m_%d_%y")
        datetime_list = pd.date_range(start="2020-01-22", end=last_date).tolist()
        datelist = [date.strftime(self._get_time_format()) for date in datetime_list]
        return datelist
