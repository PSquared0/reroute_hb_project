""" Reroute Project Tracker
A front-end for a databse that works with the ReRoute database
"""

from flask import Flask,request
from model import Bus, Rating, User, Bus_filter, Stop, Filter, db, connect_to_db
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)



def get_bus_list():
    """Gets list of buses from database"""

    buses = db.session.query(Bus.bus_name).all()

    return buses 

def get_bus_details():
    """Shows ratings for bus"""

    bus_detail = db.session.query(Bus.bus_name == (Bus.bus_name)).one()


    return bus_detail

def get_stop_ids(bus_stop_id):

    results = [ item['stop_id'] for item in bus_stop_id ]


    return results

def get_stop_info(info):
    """Shows info per bus stop"""
    api_url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=sf-muni&stopId='
    
    urls = []
    for stop_id in info:
        url = api_url + str(stop_id)
        urls.append(url)
    return urls



def send_api(urls):
    xmls = []
    for url in urls:
        response = requests.get(url)
        unparsed_xml = response.text
        xml = BeautifulSoup(unparsed_xml, 'xml')
        xmls.append(xml)

    return xmls



def get_bus_name_info(xmls):


    stop_dict = {}

    for xml in xmls:

        xml_infos = xml.find_all('predictions')
        for xml_info in xml_infos:
            bus_dir = ''
            bus_mins =''
            if xml.predictions.direction is None:
                bus_dir = xml.predictions['dirTitleBecauseNoPredictions']
                bus_mins = '10025600'
            else:
                bus_dir = xml.predictions.direction['title']
                bus_mins = xml.predictions.prediction['minutes']


            r_name = xml_info['routeTag'] + '  ' + bus_dir
            # d_name = xml.predictions.direction['title']
            # info = xml_info['routeTag']

            stop_dict[r_name] = {}


            stop_dict[r_name]['dir'] = bus_dir,
            stop_dict[r_name]['name'] = xml_info['routeTitle'],
            stop_dict[r_name]['num'] = xml_info['routeTag'],
            stop_dict[r_name]['stop'] = xml_info['stopTitle'],
            stop_dict[r_name]['mins'] = bus_mins

    return stop_dict

def get_bus_stops(xml):

    xml_infos = xml.find_all('predictions')


    for xml_info in xml_infos:
        stop_info = xml_info['stopTitle']

    return stop_info

def get_bus_mins(xml):

    mins_xml_infos = xml.predictions.prediction['minutes']


    for mins_xml_info in mins_xml_infos:
        return mins_xml_info

    return mins_xml_info

def get_rating_sum(result_score):

    sum_list = sum(result_score)

    return sum_list











if __name__ == "__main__":
    
    connect_to_db(app)

    # closing our database connection

    db.session.close()