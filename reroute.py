""" Reroute Project Tracker
A front-end that works with the ReRoute database
"""

import json
import os

from flask import Flask,request
from model import Bus, Rating, User, Bus_filter, Stop, Filter, db, connect_to_db
import requests

FIVE_ELEVEN_API_KEY = os.environ.get("FIVE_ELEVEN_API_KEY")
FIVE_ELEVEN_STOP_MONITORING_URL = "http://api.511.org/transit/StopMonitoring"

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
    """Builds 511.org StopMonitoring request URLs, one per nearby stop"""

    urls = []
    for stop_id in info:
        params = {
            "api_key": FIVE_ELEVEN_API_KEY,
            "agency": "SF",
            "stopcode": stop_id,
            "format": "json",
        }
        urls.append((FIVE_ELEVEN_STOP_MONITORING_URL, params))
    return urls



def send_api(urls):
    """Fetches StopMonitoring JSON for each (url, params) pair"""

    payloads = []
    for url, params in urls:
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = json.loads(response.content.decode("utf-8-sig"))
        except (requests.RequestException, ValueError):
            continue
        payloads.append(data)

    return payloads



def get_bus_name_info(payloads):
    """Turns 511.org StopMonitoring payloads into a template-friendly dict"""

    visits = []
    for payload in payloads:
        delivery = payload.get("ServiceDelivery", {}).get("StopMonitoringDelivery", {})
        visits.extend(delivery.get("MonitoredStopVisit") or [])

    if not visits:
        return None

    stop_dict = {}

    for visit in visits:
        journey = visit.get("MonitoredVehicleJourney", {})
        call = journey.get("MonitoredCall", {})

        route_num = journey.get("LineRef", "")
        bus_dir = journey.get("DestinationName", "")
        r_name = "%s  %s" % (route_num, bus_dir)

        eta = call.get("ExpectedArrivalTime") or call.get("AimedArrivalTime")
        bus_mins = get_minutes_until(eta)

        stop_dict[r_name] = {
            "dir": (bus_dir,),
            "name": (journey.get("PublishedLineName", ""),),
            "num": (route_num,),
            "stop": (call.get("StopPointName", ""),),
            "mins": bus_mins,
        }

    return stop_dict


def get_minutes_until(iso_timestamp):
    """Minutes between now and an ISO-8601 UTC timestamp from the 511 API"""

    if not iso_timestamp:
        return "?"

    from datetime import datetime, timezone

    arrival = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    minutes = int((arrival - now).total_seconds() // 60)

    return str(max(minutes, 0))

def get_rating_sum(result_score):

    sum_list = sum(result_score)

    return sum_list











if __name__ == "__main__":

    connect_to_db(app)

    # closing our database connection

    db.session.close()
