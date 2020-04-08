from google.cloud import bigquery
from google.api_core.exceptions import BadRequest
from datetime import datetime, timedelta
import pandas as pd
from datetime import datetime
import os
import platform

class CovidQuery:
  def __init__(self):
    self.client = bigquery.Client()
    if platform.system() == 'Windows':
      self.time_format = '_%#m_%#d_%y'
    else:
      self.time_format = '_%-m_%-d_%y'
    
    self.last_column = (datetime.now()).strftime(self.time_format)
    self.sql_overview = open("sql/sql_overview.txt", "r").read()
    self.overview = self.query_overview()
    self.country_data = dict.fromkeys(['confirmed_cases', 'recovered_cases', 'deaths'])

  def query_overview(self):
    overview = []
    n = 0
    while n < 5:
      print(self.last_column)
      try :
        sql = self.sql_overview.format("%", date=self.last_column)
        overview = self.client.query(sql).to_dataframe()
        break
        # return overview
      except BadRequest:
        self.last_column = (datetime.strptime(self.last_column, '_%m_%d_%y') - 
                            timedelta(1)).strftime(self.time_format)
        n += 1
    # self.last_column = "_4_7_20"
    # sql = self.sql_overview.format("%", date=self.last_column)
    # overview = self.client.query(sql).to_dataframe()
    return overview

  def get_country(self, country):
    sql = self.sql_overview.format(country.upper(), date=self.last_column)
    results = self.client.query(sql).to_dataframe()
    if results.empty:
      print("Data for this country does not exist. Check you have spelt it correctly.")
    else:
      print("Collected data for: {}".format(results['country'].values))
      self.overview = self.overview.append(results, ignore_index=True)
    return results

    

  def global_query(self, dset):
    sql = """
        SELECT SUM({}) AS total
        FROM `bigquery-public-data.covid19_jhu_csse_eu.{}`
        """.format(self.last_column, dset)
    result = self.client.query(sql).to_dataframe()
    return result

  def country_query(self, dset, country):
    
    sql = """
        SELECT *
        FROM `bigquery-public-data.covid19_jhu_csse_eu.{}`
        WHERE UPPER(country_region) = '{}'
        """.format(dset, country.upper())
    
    results = self.client.query(sql).to_dataframe()
    cols = [c for c in results.columns if c[0] != '_' and c[0] != 'c']
    results = results.drop(columns=cols).rename(columns={'country_region': 'country'})
    results = results.groupby('country', as_index=True).sum()
    results.columns = pd.to_datetime(results.columns, format="_%m_%d_%y")
    results = results.squeeze('rows')
    results = results.rename(results.name.title())
    self.country_data[dset] = pd.concat([self.country_data[dset], results], axis=1)
    # print(results)
    return results

