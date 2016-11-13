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


def get_stop_info(stops):
	"""Shows info per bus stop"""
	api_url = 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=sf-muni&stopId='
	"""Stop_dict = {bus_name:'38',
					minutes: 7,
					stop_location: 'Geary & Leavenworth'}"""
	for stop in stops:
		url = api_url + str(stop)
	return url


def send_api(url):
	response = requests.get(url)
	unparsed_xml = response.text
	xml = BeautifulSoup(unparsed_xml, 'xml')

	
	return xml


def get_bus_name_info(xml):

	xml_infos = xml.find_all('predictions')


	for xml_info in xml_infos:
		name_info = xml_info['routeTag']
	
		
		return name_info

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