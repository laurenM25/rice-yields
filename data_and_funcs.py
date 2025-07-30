#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 23:12:30 2025

@author: laurendonnelly
"""

import pandas as pd
import numpy as np

#%%# load in data
data_df = pd.read_csv("FAOSTAT-production-data-1980-2023.csv")

land_area_df = pd.read_csv("https://ourworldindata.org/grapher/land-area-hectares.csv?v=1&csvType=filtered&useColumnShortNames=true&country=European+Union~CHN~IND~IDN~MMR~KOR~THA~VNM", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

employment_data = pd.read_csv("FAOSTAT-employment-data.csv")
population_data = pd.read_csv("FAOSTAT-population-data.csv")
macro_data = pd.read_csv("FAOSTAT-macroecon-data.csv")

#%% functions
def fix_country_naming(df):
    df.replace({"Viet Nam": "Vietnam", "Republic of Korea": "South Korea"},inplace=True)

#%%clean data

#drop columns not using
data_df.drop(columns=["Domain Code","Domain","Item Code (CPC)","Year Code","Note"])
#drop imputed and X flag values
data_df = data_df[(data_df["Flag"] != "X") & (data_df["Flag"]!="I")] #wrap each condition in parentheses

#renaming
land_area_df.rename(columns={"land_area__00006601__area__005110__hectares": "land_area"},inplace = True)
fix_country_naming(data_df)
fix_country_naming(employment_data)
fix_country_naming(population_data)
fix_country_naming(macro_data)


#narrow down employment indicators , keeping ones with most data and relevance
employment_data = employment_data[(employment_data["Indicator"] == "Employment in agriculture - ILO modelled estimates") | (employment_data["Indicator"] == "Share of employment in agriculture in total employment - ILO Modelled Estimates")]
#drop columns from employment df
employment_data.drop(columns=["Year Code", "Sex Code", "Sex", "Domain Code", "Domain", "Area Code (M49)"],inplace=True) #since not separating gender, remove columns
population_data.drop(columns=["Area Code (M49)","Domain Code","Domain", "Item Code","Item","Year Code"],inplace=True)


#renaming macro data
macro_data.drop(columns=["Domain Code","Domain","Area Code (M49)","Year Code"])
macro_data.replace({"China, mainland": "China"},inplace=True) #Whenever "China" appears, it is always referring to mainland

#focusing on value added as share of gdp
val_added_as_share = macro_data[(macro_data["Element Code"] == 61570) & (macro_data["Item Code"] == 22016)]
val_added_usd = macro_data[(macro_data["Element Code"] == 6110) & (macro_data["Item Code"] == 22016)]


#%% subsection data
area_harvested_df = data_df[data_df["Element"] == "Area harvested"] 

rural = population_data[population_data["Element"] == "Rural population"]
urban = population_data[population_data["Element"] == "Urban population"]

rural_urban_df = rural.groupby("Area").apply(lambda x: x['Value']).reset_index().drop(columns=["level_1"])
rural_urban_df["Year"] = rural["Year"].unique().tolist() * 7 # in ascending order of years, resets each new country
rural_urban_df.rename(columns={"Value":"Rural"},inplace=True)
rural_urban_df["Urban"] = urban.groupby("Area").apply(lambda x: x['Value']).reset_index()["Value"].tolist()
rural_urban_df["Urban:Rural"] = rural_urban_df["Urban"] / rural_urban_df["Rural"] 

#%% combining into one big dataframe
#create new df, index by Area and Year. Add Yield as first column
df = data_df.set_index(["Area","Year"])
df = df[df["Element"] == "Production"]
df = df[["Value"]]
df.rename(columns={"Value": "Yield (kg/ha)"},inplace=True)

#add population data to columns
temp_df = rural_urban_df.set_index(["Area","Year"])
temp_df["total_population"] = temp_df["Urban"] + temp_df["Rural"]
temp_df = temp_df[["Urban:Rural","total_population"]]
df = pd.merge(df,temp_df, on=["Area","Year"])

#add employment data
temp_df = employment_data.set_index(["Area","Year"])
temp_1 = temp_df[temp_df["Indicator Code"] == 21144][["Value"]]
temp_1.rename(columns={"Value":"employed_in_ag"},inplace=True)

temp_2 = temp_df[temp_df["Indicator Code"] == 21156][["Value"]]
temp_2.rename(columns={"Value":"percent_employed_in_ag"},inplace=True)

temp_df = pd.merge(temp_1, temp_2, on=["Area","Year"])
df = pd.merge(df,temp_df, on=["Area","Year"])

#add macro data
temp_df = macro_data.set_index(["Area","Year"])
temp_1 = val_added_as_share.set_index(["Area","Year"])[["Value"]]
temp_1.rename(columns={"Value":"val_added_percent_GDP"},inplace=True)

temp_2 = val_added_usd.set_index(["Area","Year"])[["Value"]]
temp_2.rename(columns={"Value":"val_added_mil_USD"},inplace=True)
temp_df = pd.merge(temp_1, temp_2, on=["Area","Year"])
df = pd.merge(df,temp_df, on=["Area","Year"])

#Add urban and rural population as columns to see correlation matrix values
df_urb_rur = rural_urban_df.set_index(["Area","Year"])
df_urb_rur = df_urb_rur[["Urban", "Rural"]]
df = pd.merge(df,df_urb_rur,on=["Area","Year"])

#Add area harvested
temp_df= data_df[data_df["Element"] == "Area harvested"] #area harvested data
temp_df = temp_df.set_index(["Area","Year"])           #multi index
temp_df = temp_df[["Value"]]
temp_df.rename(columns={"Value": "Area harvested (ha)"},inplace=True) #rename column
df = pd.merge(df,temp_df,on=["Area","Year"]) #merge with df

#### Add area harvested proportional to country surface area as column
def obtainHarvestedProp(country):

    if country not in land_area_df["Entity"].values:
        print(f"invalid country name: {country} not found in the land_area_df as an entity.")
        return
    
    #scalar land area value for country
    country_land_area = land_area_df[land_area_df["Entity"]==country]["land_area"].values[0]

    #ratio for country
    if country not in data_df["Area"].values:
        print(f"country name '{country}' was not found in the data_df 'Area' values. Ensure consistent naming across dataframes.")
        return
        
    harvested_prop = df.loc[country]["Area harvested (ha)"] / country_land_area
    return harvested_prop

#add col with data for each country. use .values to insert values
for country in data_df.Area.unique():
    df.loc[(country,), "area_harvested_prop"] = obtainHarvestedProp(country).values

#%% export

def export_data():
    unit_dict = {"Yield (kg/ha)": "kg/ha", "Yield": "kg/ha","Urban:Rural": "ratio", "total_population": "in thousands", 
                 "employed_in_ag": "in thousands", "percent_employed_in_ag": "percentage", "val_added_percent_GDP": "percentage of GDP", 
                 "val_added_mil_USD": "millions (USD)", "Area harvested (ha)": "ha", "Area harvested": "ha","area_harvested_prop": "percentage"}
    return df, unit_dict