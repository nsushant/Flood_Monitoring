# TO GET LIST OF STATIONS
# this uses Environment Agency flood and river level data from the real-time data API (Beta)
# import statements
import requests
import matplotlib.pyplot as plt
import os
import pandas as pd 
import datetime 
import numpy as np
from tabulate import tabulate
import folium 
from IPython.display import display

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
    
    
print("\n")
print("This app will help you find a station and plot its recorded values over the last 24 hours.")
print("If a station reference is alrady known, please enter it below in the [Enter Station Reference] input field below to see plots of all available params")
print("\n")   
print("If you would like to find your station reference using filters, please leave the Enter Station Reference input field empty and press enter to continue") 
print("\n")   
print("To instead view a map with station references marked and exit for now please type out MAP in the Enter Station Reference input field below")
print("\n") 
    
in_station_ref = input("Enter Station Reference, If unknown leave blank and press enter:")
    
    
if len(in_station_ref) != 0: 
    
    if in_station_ref == "MAP": 
        lats_map,longs_map,station_refs_map  = get_coords()
        
        Cambridge_coords = (52.1951, 0.1313)
        Map_view = folium.Map(location=Cambridge_coords, zoom_start=12)

        for l in range(len(lats_map)):     

            folium.CircleMarker(
            [float(lats_map[l]), float(longs_map[l])],
            radius=2,
            fill=True,
            popup=folium.Popup(f"Station Ref. {station_refs_map[l]}"),
            ).add_to(Map_view)

        Map_view.show_in_browser()
        
    else: 
        station_reference = str(in_station_ref)

        available_params,param_units = list_parameters(station_reference)

        print(available_params)

        if len(available_params)>1:

            fig, ax1 = plt.subplots(len(available_params),1,figsize=(20,5*len(available_params)))
            fig.suptitle(f"Station {station_reference}", fontsize=20)

        for i in range(len(available_params)):

            df = get_data_for_station(station_reference,available_params[i])

            if type(df) == type(None):

                print(f"skipping param {available_params[i]} because no data was found")
                continue

            if len(available_params)>1:    
                create_plot_from_data(df,available_params[i],param_units[i],axt=ax1[i])
            else:
                create_plot_from_data(df,available_params[i],param_units[i])
                plt.suptitle(f"Station {station_reference}")

        plt.show()
    
if len(in_station_ref) == 0: 
    
    available_filters =["search","parameterName","parameter","qualifier","label","town","catchmentName","riverName","stationReference","RLOIid","type","status"]    
    
    selected_filters = []
    
    selected_filter_values = []
    
    selected_station_ref = None
    
    stop_mark = 0 
    
    while ((len(selected_filters) < len(available_filters)) and (type(selected_station_ref) == type(None))):
        
        stop_mark+=1 
        
        print("To help you find a station reference, the following filters are available\n")
        print("\n")
        print(f"{available_filters}")
        print("\n")                
        print("In the field below, please enter the name of one filter you would like to use.")
        print("The field will appear again if you would like to add more filters later")
        print("If you want to try and enter a station reference directly, please press enter and leave fields blank")
        print("\n")

        filter_name_in = input("Filter Name (e.g.parameter):")
        
        filter_value = input("Filter Value (e.g.level):")
        
        
        if len(filter_name_in) == 0:
            selection_for_this_it = input("Enter Station Reference, If unknown leave blank and press enter:")
            
            if str(selection_for_this_it) not in list_stations(): 
                print("The station reference is invalid please try again")
                        
                continue

        
        if filter_name_in not in available_filters:
            
            print("This filter is not available, please choose one from the provided list")
                
            continue 
            
            
        selected_filters.append(str(filter_name_in))
        
        selected_filter_values.append(str(filter_value))
        
        available_filters.remove(str(filter_name_in))
  
        station_ids_this_it = list_stations(filter_names=selected_filters,values=selected_filter_values)
        
        print("The stations that satisfy the provided filters are:")
        
        print(station_ids_this_it)
        
        print("\n")
        
        print("If you're ready to make a selection enter a station reference below")
        print("otherwise if you would like to add filters press enter and leave the field blank")
        print(f"You have so far added filters: {selected_filters} with values {selected_filter_values}")
        print("\n")
        print("to erase all filters and start again please enter the word RESTART (all caps) in the station reference field below")
        selection_for_this_it = input("Enter Station Reference: ")
        
        if str(selection_for_this_it) == "RESTART":
            exit()
        
        if str(selection_for_this_it) not in list_stations():
            
            print("The station reference is invalid please try again")
                        
            continue
        
        if len(selection_for_this_it) > 0: 
           
            selected_station_ref=str(selection_for_this_it)
           
         
        if stop_mark > 100: 
            
            print("The application has timed out, please restart")
            
            exit()
            
    
    station_reference = str(selected_station_ref)
    
    available_params,param_units = list_parameters(station_reference)
    
    print(available_params)
    
    if len(available_params)>1:
        
        fig, ax1 = plt.subplots(len(available_params),1,figsize=(20,5*len(available_params)))
        fig.suptitle(f"Station {station_reference}", fontsize=20)

    for i in range(len(available_params)):
    
        df = get_data_for_station(station_reference,available_params[i])
        
        if type(df) == type(None):
            
            print(f"skipping param {available_params[i]} because no data was found")
            continue
        
        print(f"Table for param {available_params[i]}")
        print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
        print("\n")
        if len(available_params)>1:    
            create_plot_from_data(df,available_params[i],param_units[i],axt=ax1[i])
        else:
            create_plot_from_data(df,available_params[i],param_units[i])
            plt.suptitle(f"Station {station_reference}")

    
    plt.show()

    
    
    
    
    
    
    
    
    
    