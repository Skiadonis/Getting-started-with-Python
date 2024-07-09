# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# %% import packages
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import shapely.plotting as splt
import shapely
import meteostat
from meteostat import Stations
from meteostat import Hourly
import pickle
import io
import geopandas as gpd
import requests

# %% 
# GeoJSON-Daten von der URL abrufen
url = "https://geoportal.muenchen.de/geoserver/gsm_wfs/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=gsm_wfs:vablock_stadtbezirke_opendata&outputFormat=application/json"
response = requests.get(url)
data = response.json()

# GeoDataFrame erstellen
gdf = gpd.GeoDataFrame.from_features(data["features"])

# GeoJSON in Pickle-Datei speichern
gdf.to_pickle("LVN_Gebiet.pkl")

# %%
# Laden Sie Ihr GeoDataFrame aus der Pickle-Datei
area = pd.read_pickle("LVN_Gebiet.pkl")

# Überprüfen Sie die Struktur des GeoDataFrame
print(area.head())

# Zugriff auf die geometrischen Daten
geometries = area.geometry

# Jetzt können Sie die geometrischen Daten verwenden
for geom in geometries:
    # Hier können Sie mit den geometrischen Daten arbeiten
    print(geom)

# %% load DSO area from file
fig, ax = plt.subplots(figsize=(7, 10))

for geom in geometries:
    xs, ys = geom.exterior.xy
    ax.fill(xs, ys, color='b', alpha=0.2)
del xs, ys, geom

# %%
dsoBoundsTopLeft = (area.bounds[3], area.bounds[0])
dsoBoundsBottomRight = (area.bounds[1], area.bounds[2])
stations = Stations()
stations = stations.bounds(dsoBoundsTopLeft, dsoBoundsBottomRight)
stations = stations.fetch()

# timeS = datetime(2021, 1, 1, 0, 0, 0)
timeS = datetime(2021, 1, 1, 0, 0, 0)
timeE = datetime(2023, 10, 27, 0, 0, 0)
stations = stations[(stations['hourly_start'] <= timeS) & (stations['hourly_end'] >= timeE)]

del dsoBoundsTopLeft, dsoBoundsBottomRight
# %% 

ax.scatter(x=stations["longitude"], y=stations["latitude"])
fig.savefig("test")

# %% access data from meteostat
timespanH = (timeE - timeS)
timespanH = int(divmod(timespanH.total_seconds(), 3600)[0]) + 1

# %% export meteostat data as dict in pickle
gaps = pd.DataFrame()
stationsDict = {}
for i, row in stations.iterrows():
    data = meteostat.Hourly(i, start=timeS, end=timeE).fetch().astype('float')

    gaps2 = pd.DataFrame(data=[], columns=data.columns)

    info = get_info_df(data, i)
    gaps = pd.concat([gaps, gaps2, info])
    stationsDict.update({i: (float(row["longitude"]), float(row["latitude"]), data)})
del gaps2, data, info, i, row
save_pkl_data(stationsDict, "weahterData.pkl")
gaps = gaps.astype('int')
gaps = timespanH - gaps

# %% maximum length of NaN values
maxLengthGaps = pd.DataFrame(data=[], columns=gaps.columns)

for key in stationsDict.keys():
    a = pd.DataFrame(data=stationsDict[key][2].apply(max_na)).transpose()
    a.index = [key]
    maxLengthGaps = pd.concat([maxLengthGaps, a]).astype('int')
del a
# %%
# varGaps = 
varDict = {}
weatherVars = (stationsDict[list(stationsDict.keys())[0]][2]).columns

for var in weatherVars:
    df = pd.DataFrame()
    for key in stationsDict.keys():
        df[key] = stationsDict[key][2][var]
    varDict.update({var: df})
del df, weatherVars

gapDf = pd.DataFrame()
for key in varDict.keys():
    gapDf[key] = varDict[key].isna().sum(axis=1)

# %%
# Laden Sie Ihr GeoDataFrame aus der Pickle-Datei
area = gpd.read_pickle("LVN_Gebiet.pkl")

# Überprüfen Sie die Struktur des GeoDataFrame
print(area.head())

# Zugriff auf die geometrischen Daten
geometries = area.geometry

# Jetzt können Sie die geometrischen Daten verwenden
for geom in geometries:
    # Hier können Sie mit den geometrischen Daten arbeiten
    print(geom)

