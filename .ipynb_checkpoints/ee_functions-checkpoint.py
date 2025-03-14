
import ee 
import datetime


def ee_authentication():
    ee.Authenticate()
    ee.Initialize()

    return 


def convert_ee_to_datetime(YYYY_MM_DD):
    if (type(YYYY_MM_DD) != str): 
        print("Input must be a string of form YYYY-MM-DD")
        print("you have currently provided input of type " + str(type(YYYY_MM_DD)))
        
    ee_date = ee.Date(YYYY_MM_DD)
    py_date = datetime.datetime.utcfromtimestamp(ee_date.getInfo()['value']/1000.0)
    return py_date 


def convert_datetime_to_ee(py_date):
    if (type(YYYY_MM_DD) != str): 
        print("Input must be a string of form YYYY-MM-DD") 
        print("you have currently provided input of type " + str(type(py_date)))
    ee_date = ee.Date(py_date)
    return ee_date


def filter_image_collection():
    first = (
    ee.ImageCollection('COPERNICUS/S2_SR')
    .filterBounds(ee.Geometry.Point(73.8357,18.5442))
    .filterDate('2020-01-01', '2020-12-31')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    )
    return first 
