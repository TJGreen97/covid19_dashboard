from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
from datetime import datetime, timedelta
import platform
import pandas as pd


class SQL:
    def __init__(self):
        self.client = bigquery.Client()
        self.sql_overview = open("sql/sql_overview.txt", "r").read()
        self.last_column = self._get_last_db_column()

    @staticmethod
    def _get_time_format():
        if platform.system() == "Windows":
            time_format = "_%#m_%#d_%y"
        else:
            time_format = "_%-m_%-d_%y"
        return time_format

    def _get_last_db_column(self):
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
        return (
            datetime.strptime(self.last_column, "_%m_%d_%y") - timedelta(1)
        ).strftime(self._get_time_format())

    def overview_query(self):
        print("Making overview query")
        overview = []
        sql = self.sql_overview.format(
            "%", date=self.last_column, ref=self._second_last_column()
        )
        try:
            overview = self.client.query(sql).to_dataframe()
        except BadRequest:
            print("Data unavailable")
            return []
        return overview

    def global_total(self):
        sql = open("sql/global_total.txt", "r").read()
        sql = sql.format(date=self.last_column, ref=self._second_last_column())
        try:
            result = self.client.query(sql).to_dataframe()
        except BadRequest:
            print("ERROR: Global Total Data Unavailable")
            return []
        result = result.pivot(index="id", columns="dset", values="totals")
        active = pd.DataFrame()
        active["active_cases"] = (
            result["confirmed_cases"] - result["deaths"] - result["recovered_cases"]
        )
        result = pd.concat([result, active], axis=1)
        return result

    def country_overview(self, country):
        sql = self.sql_overview.format(
            country.upper(), date=self.last_column, ref=self._second_last_column()
        )
        try:
            result = self.client.query(sql).to_dataframe()
        except BadRequest:
            print("ERROR: Overview Data Unavailable")
            return []
        print("Collected data for: {}".format(result["country"].values))
        return result

    def country_data_query(self, country):
        date_list = self._get_date_list()
        date_string = ", ".join(["SUM(" + x + ") AS " + x for x in date_list])
        sql = open("sql/country_data.txt", "r").read()
        sql = sql.format(date_list=date_string, country=country.upper())
        try:
            results = self.client.query(sql).to_dataframe()
        except BadRequest:
            print("Data unavailable")
            return []
        results.set_index("dset", inplace=True)
        results.columns = pd.to_datetime(results.columns, format="_%m_%d_%y")
        return results

    def _get_date_list(self):
        last_date = datetime.strptime(self.last_column, "_%m_%d_%y")
        datetime_list = pd.date_range(start="2020-01-22", end=last_date).tolist()
        datelist = [date.strftime(self._get_time_format()) for date in datetime_list]
        return datelist
