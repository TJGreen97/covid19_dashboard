from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
from datetime import datetime, timedelta
import platform
import pandas as pd
import numpy as np

class SQL:
    def __init__(self):
        self.client = bigquery.Client()
        self.sql_overview = open("sql/sql_overview.txt", "r").read()
        self.last_column = self._get_last_db_column()
    
    @staticmethod
    def _get_time_format():
        if platform.system() == 'Windows':
            time_format = '_%#m_%#d_%y'
        else:
            time_format = '_%-m_%-d_%y'
        return time_format

    def _get_last_db_column(self):
        date_attempt = (datetime.now()).strftime(self._get_time_format())
        sql_template = """SELECT {} FROM `bigquery-public-data.covid19_jhu_csse_eu.confirmed_cases`"""
        n = 0
        while n < 5:
            try :
                sql = sql_template.format(date_attempt)
                self.client.query(sql).to_dataframe()
                break
            except BadRequest:
                date_attempt = (datetime.strptime(date_attempt, '_%m_%d_%y') - 
                                    timedelta(1)).strftime(self._get_time_format())
            n += 1
        # TO DO: raise an error
        return date_attempt

    def overview_query(self):
        print("Making overview query")
        overview = []
        sql = self.sql_overview.format("%", date=self.last_column)
        try:
            overview = self.client.query(sql).to_dataframe()
        except BadRequest:
            print("Data unavailable")   
            return []     
        return overview

    def global_total(self, dset):
        sql = """
                SELECT SUM({}) AS {dset}
                FROM `bigquery-public-data.covid19_jhu_csse_eu.{dset}`
            """.format(self.last_column, dset=dset)
        try:
            result = self.client.query(sql).to_dataframe()
        except BadRequest:
            print("Data unavailable")
            return []
        return result
    
    def country_overview(self, country):
        sql = self.sql_overview.format(country.upper(), date=self.last_column)
        try:
            result = self.client.query(sql).to_dataframe()
        except BadRequest:
            print("Data unavailable")
            return []
        print("Collected data for: {}".format(result['country'].values))
        # print(result)
        return result

    def country_data_query(self, country, dset):

        
        sql = """
            SELECT *
            FROM `bigquery-public-data.covid19_jhu_csse_eu.{}`
            WHERE UPPER(country_region) = '{}'
            """.format(dset, country.upper())
        try:
            results = self.client.query(sql).to_dataframe()
        except BadRequest:
            print("Data unavailable")
            return []
        cols = [c for c in results.columns if c[0] != '_' and c[0] != 'c']
        results = results.drop(columns=cols).rename(columns={'country_region': 'country'})
        results = results.groupby('country', as_index=True).sum()
        results.columns = pd.to_datetime(results.columns, format="_%m_%d_%y")
        results = results.squeeze('rows')
        results = results.rename(dset)
        return results

    def country_data_query2(self, country):
        date_list = self._get_date_list()
        date_string = ', '.join(['SUM(' + x + ') AS ' + x for x in date_list])
        sql = """
            SELECT {date_list}, 'confirmed_cases' dset FROM `bigquery-public-data.covid19_jhu_csse_eu.confirmed_cases`
            WHERE UPPER(country_region) = '{country}'
            UNION ALL
            SELECT {date_list}, 'recovered_cases' FROM `bigquery-public-data.covid19_jhu_csse_eu.recovered_cases`
            WHERE UPPER(country_region) = '{country}'
            UNION ALL
            SELECT {date_list}, 'deaths' FROM `bigquery-public-data.covid19_jhu_csse_eu.deaths`
            WHERE UPPER(country_region) = '{country}'
            """.format(date_list=date_string, country=country.upper())
        try:
            results = self.client.query(sql).to_dataframe()
        except BadRequest:
            print("Data unavailable")
            return []
        results.set_index('dset', inplace=True)
        results.columns = pd.to_datetime(results.columns, format="_%m_%d_%y")
        return results

    def _get_date_list(self):
        last_date = datetime.strptime(self.last_column, '_%m_%d_%y')
        datetime_list = pd.date_range(start="2020-01-22", end=last_date).tolist()
        datelist = [date.strftime(self._get_time_format()) for date in datetime_list]
        return datelist