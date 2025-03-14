import requests
import matplotlib.pyplot as plt
import os
import pandas as pd 
import datetime 
import numpy as np
from tabulate import tabulate
import folium 
from IPython.display import display
import ee
from API_access_functions import *
from ee_functions import *


def get_coords():
    url_weather_stations = "https://environment.data.gov.uk/flood-monitoring/id/stations"
    response = requests.get(url_weather_stations)
    json_response_items = response.json()["items"]
    
    station_refs = np.array([])
    lats = np.array([])
    longs = np.array([])
    
    for i in json_response_items:
        try:
            lats = np.append(lats,float(i["lat"]))
            longs = np.append(longs,float(i["long"]))
            station_refs = np.append(station_refs,i["notation"])
        except:
            continue 
            
            
    return lats,longs,station_refs 



def list_stations(filter_names=None,values=None):
    
    if type(filter_names)==type(None): 
        url_weather_stations = "https://environment.data.gov.uk/flood-monitoring/id/stations"
 
    if type(filter_names) == str: 
        url_weather_stations = f"https://environment.data.gov.uk/flood-monitoring/id/stations?{filter_names}={values}"
    
    if type(filter_names) == list:
        url_weather_stations = f"https://environment.data.gov.uk/flood-monitoring/id/stations?{filter_names[0]}={values[0]}"
        
        if len(filter_names)>1: 
            for queryid in range(1,len(filter_names)):
            
                add_query = f"&{filter_names[queryid]}={values[queryid]}"
            
                url_weather_stations = url_weather_stations+add_query
        
    print(url_weather_stations)
    
    
    
    response = requests.get(url_weather_stations)
    json_response_items = response.json()["items"]

    notations = []

    for i in json_response_items:
        notations.append(i["notation"])
    
    return notations

# TO GET LIST OF Parameters
def list_parameters(station_ref): 
        
    url_measures = "https://environment.data.gov.uk/flood-monitoring/id/measures?stationReference="+str(station_ref)

    response = requests.get(url_measures)
    dict_measures = response.json()
    
    params = []
    
    units = []

    for i in dict_measures["items"]:
        params.append(i["parameter"])
        units.append(i["unitName"])
        
     
    unique_params = np.asarray(list(set(params)))
    
    unique_units = np.asarray([units[params.index(p)] for p in unique_params])
    
    return unique_params,unique_units
    

# TO GET Data from station
def get_data_for_station(station_notation,param,date=None):
        
    if type(date)==type(None): 
        today = datetime.datetime.now()

    else: 
        today = date
        
    end = today-datetime.timedelta(hours=24)

    data_url = f"http://environment.data.gov.uk/flood-monitoring/id/stations/"

    station_url = os.path.join(data_url,station_notation)
    
    readings_url = os.path.join(station_url,"readings.csv")
    
    readings_url = readings_url+"?since="+str(end.strftime("%Y-%m-%dT%H:%M:%SZ"))+f"&parameter={param}"

    try: 
        df = pd.read_csv(readings_url)
        df["dateTime"] = pd.to_datetime(df["dateTime"])
    
        df = df.sort_values(by=["dateTime"])
    
        return df

    
    except Exception as no_data_error: 
        
        print(f"Data for parameter {param} for station {station_notation} is unavailable")
        
        return None



def create_plot_from_data(data,param,unit,axt=None):
    
    
    if type(axt)==type(None):
        
        
        plt.figure(figsize=(20,5))     

        plt.title(f"Plotting {param}")
    
            
        plt.xlabel("Dates and Times")
        plt.ylabel(f"{param} in units {unit}")
        plt.plot(data['dateTime'],data["value"])
        
    else: 
        
        axt.set_title(f"Plotting {param}")

        axt.set_xlabel("Dates and Times")
        axt.set_ylabel(f"{param} in units {unit}")
        axt.plot(data['dateTime'],data["value"])
        

    return
    
