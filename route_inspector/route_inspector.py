import googlemaps
from datetime import datetime
from route_inspector.api_keys import GOOGLE_MAPS_API_KEY


def directions(client, origin, destination, mode=None,
               waypoints=None, alternatives=False, avoid=None,
               language=None, units=None, region=None,
               departure_time=None, arrival_time=None,
               optimize_waypoints=False, transit_mode=None,
               transit_routing_preference=None, traffic_model=None):
    pass


def get_google_maps_routes(google_maps_params:dict):
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    gmaps.directions(**google_maps_params)
    # TODO: extract steps/legs -> get tiles

    # TODO: cash segments to redis

    pass


def compute_route(input_params: dict):
    """Evaluate route and pick the best alternative according to parameters
    :param input_params:
    :return:
    """
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    # get base route from google maps
    start_point = input_params['start_point']
    end_point = input_params['end_point']

    # extract alternatives if any

    start_point = input_params['start_point']
    end_point = input_params['end_point']
    green = input_params['green']
    pollution_free = input_params['pollution_free']
    less_crowded = input_params['less_crowded']
    safer = input_params['safer']
    # TODO: for greener: only evaluate bicycle and walking segments surroundings
    # safer: avoid industrial zones by default
    # TODO: grab segments matrix and get data from there
    return {'route': 'route_stub'}
