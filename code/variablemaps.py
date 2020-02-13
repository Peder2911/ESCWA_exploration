import pandas as pd
import geopandas as gpd
import sqlite3
from matplotlib import pyplot as plt
import os
import pickle
import random
import functools

db = sqlite3.connect("data/db.sqlite")

escwacountries = pd.read_sql("SELECT * FROM META_menacountries",db)
gaulshapes = gpd.read_file("data/gaul/gaul0_asap.shp")

escwacountries = escwacountries.rename(columns = {"iso2c":"isocode"})
escwacountries = gaulshapes.merge(escwacountries,on="isocode")

data = escwacountries[["iso3n","geometry"]].copy() 

indMeta = pd.read_sql("SELECT * FROM META_indicators",db)
if "countryData.pickle" in os.listdir("cache"):
    maxyears = []
    for seriesCode in indMeta.SeriesCode:

        indicatorData= pd.read_sql(f"SELECT * FROM {seriesCode}", db)
        maxYear = indicatorData.TimePeriod.max()
        maxyears.append(maxYear)

        indicatorData = indicatorData[indicatorData.TimePeriod == maxYear]

        indicatorData = indicatorData.rename(columns = {
            "Value":seriesCode,"GeoAreaCode":"iso3n"}
            )

        indicatorData.year = maxYear 
        indicatorData = data.copy().merge(indicatorData,on="iso3n",how="left")
        indicatorData.groupby("iso3n").mean()
        indicatorData["iso3n"] = indicatorData.index

        data[seriesCode] = indicatorData[seriesCode]
    
    indMeta["maxyear"] = maxyears
    with open("cache/countryData.pickle","wb") as f:
        pickle.dump(data,f)

else:
    with open("cache/countryData.pickle","rb") as f:
        data = pickle.load(f)

def plotVariable(var,dest = None):
    meta = indMeta[indMeta.SeriesCode == var]

    base = gaulshapes.plot(
        figsize = (20,10),
        color = "white", edgecolor="gray", linewidth = 0.3
        )
    memb = escwacountries.plot(ax=base,
        color = "lightgray", edgecolor = "darkgray")
    data[pd.notnull(data[var])].plot(ax=base,column = var,legend=True,
        edgecolor= "darkgray")

    ax = plt.gca()
    ax.set_title(f"{var} ({int(meta.maxyear)})\n{meta['SeriesDescription'].values[0]}")
    ax.set_xlim((-19,62))
    ax.set_ylim((8,38))

    if dest is None:
        dest = "/tmp/map.png"

    plt.savefig(dest)
    plt.clf()
    plt.close()

plotVariable(random.choice(indMeta.SeriesCode))
#for var in indMeta.SeriesCode:
    #plotVariable(var,dest = f"plots/variables/{var}.png")
