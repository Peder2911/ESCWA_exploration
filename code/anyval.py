
import pandas as pd
import geopandas as gpd
import sqlite3
from matplotlib import pyplot as plt
from matplotlib import colors as colors
import os
import pickle
import random
import functools

db = sqlite3.connect("data/db.sqlite")

escwacountries = pd.read_sql("SELECT * FROM META_menacountries",db)
gaulshapes = gpd.read_file("data/gaul/gaul0_asap.shp")

escwacountries = escwacountries.rename(columns = {"iso2c":"isocode"})
escwacountries = gaulshapes.merge(escwacountries,on="isocode")

indicatorMeta = pd.read_sql("SELECT * FROM META_indicators",db)

# ========================================================

indicatorPres = []
for seriesCode in indicatorMeta.SeriesCode:
    indicatorData = pd.read_sql(f"SELECT * FROM {seriesCode}", db)
    
    covered = set(indicatorData.GeoAreaCode)
    print(covered)

    present = [cc in covered for cc in escwacountries.iso3n]
    data = pd.DataFrame({
        "isocode": escwacountries.isocode,
        "indicator": seriesCode,
        "presence": present})
    indicatorPres.append(data)

indicatorPres = pd.concat(indicatorPres)

countryProportions = indicatorPres[["isocode","presence"]].groupby("isocode").sum()
countryProportions = (countryProportions / len(set(indicatorPres.indicator))) * 100
coverageMap = escwacountries.merge(countryProportions, on = "isocode")
    
gs = gaulshapes.plot(figsize = (20,6),
    color = "white", edgecolor = "gray", linewidth = 0.3)
cm = coverageMap.plot(ax = gs, 
    column = "presence",
    edgecolor = "gray",
    legend = True, cmap = "Greens",
    vmin = 0, vmax = 100)

ax = plt.gca()
ax.set_title("Variable coverage (%)")

ax.set_xlim((-19,62))
ax.set_ylim((8,38))

plt.savefig("plots/completeness.png")
