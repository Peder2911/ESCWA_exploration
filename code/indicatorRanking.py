
import pandas as pd
import sqlite3

countries = "GeoAreaCode"
years = "TimePeriod"

def nCountryYears(data):
    try: 
        countryyears = data[[countries,years,"Value"]].groupby([countries,years]).max()
        return countryyears.shape[0] 
    except KeyError:
        return None

with sqlite3.connect("data/db.sqlite") as db:
    indicators = pd.read_sql("SELECT * FROM META_indicators",db)
    indicatorData = [pd.read_sql(f"SELECT * FROM {ind}",db) for ind in indicators.SeriesCode]

indicators["Country-years"] = [nCountryYears(d) for d in indicatorData]
indicators["First year"] = [d[years].min() for d in indicatorData]
indicators["Last year"] = [d[years].max() for d in indicatorData]

indicators.to_excel("out/indicators.xlsx",index = False)
