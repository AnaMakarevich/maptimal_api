import googlemaps
from datetime import datetime

import requests

from route_inspector.api_keys import GOOGLE_MAPS_API_KEY, POLLUTION_API_KEY
from route_inspector.utils import get_tile_from_coordinate

ZOOM_LEVEL_TILES = 17


# default google maps directions signature for reference
def directions(client, origin, destination, mode=None,
               waypoints=None, alternatives=False, avoid=None,
               language=None, units=None, region=None,
               departure_time=None, arrival_time=None,
               optimize_waypoints=False, transit_mode=None,
               transit_routing_preference=None, traffic_model=None):
    pass


def get_air_quality_index(lon: float, lat: float) -> int:
    """Makes a request to OpenWeatherMap and gets the value of air quality at this location.
    :param lon: Longitude
    :param lat: Latitude
    :return: Air quality index: 1 - best, 5 - worst
    """
    request_link = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={POLLUTION_API_KEY}"
    response = requests.get(request_link)
    if response.status_code == 200:
        air_quality_index = response.json()['list']['main']['aqi']
        return air_quality_index
    else:
        raise Exception("Air pollution API failed")


def process_route(route: dict) -> dict:
    # extract segments
    start_location = route["legs"][0]["steps"][0]["start_location"]
    start_tile = get_tile_from_coordinate(*start_location, ZOOM_LEVEL_TILES)
    air_quality_index_at_start = get_air_quality_index(*start_location)
    tile_x_seq = [start_tile[0]]
    tile_y_seq = [start_tile[1]]
    air_quality_data = [air_quality_index_at_start]  # from air pollution data
    terrain_type = []  # from openstreetmap
    for leg in route["legs"]:
        steps = leg["steps"]
        for step in steps:
            start_location = step["start_location"]
            end_location = step["end_location"]

            # get tile coordinates
            start_tile = get_tile_from_coordinate(*start_location, ZOOM_LEVEL_TILES)
            end_tile = get_tile_from_coordinate(*end_location, ZOOM_LEVEL_TILES)

            # store tile coordinates of the end point
            tile_x_seq.append(end_tile[0])
            tile_y_seq.append(end_tile[1])

            # tile
            air_quality_index_at_end = get_air_quality_index(*end_location)
            air_quality_data.append(air_quality_index_at_end)
            # query landscape type for tiles if: only for start tile if the distance is small
    # TODO: post-processing step that merges tiles together so that small segments are ignored
    # TODO: after merging save route in cache with values for air quality, terrain
    # TODO: asses route quality
    # TODO: LATER: for each route:
    # goal -> find waypoints of interest and rebuild the route using these waypoints
    # TODO: cash segments to redis
    return {'green': 1, 'crowded': 1}


def get_google_maps_routes(google_maps_params: dict):
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    routes = gmaps.directions(**google_maps_params)
    return routes
    # how many routes?


def compute_route(input_params: dict):
    """Evaluate route and pick the best alternative according to parameters
    :param input_params:
    :return:
    """
    routes = get_google_maps_routes(input_params["gmap_params"])
    for route in routes:
        # get bounding box since we can search in this area
        bounding_box = route['bounds']
        route_quality = process_route(route)
    # TODO: choose best route
    # get base route from google maps

    green = input_params['green']
    pollution_free = input_params['pollution_free']
    less_crowded = input_params['less_crowded']
    safer = input_params['safer']
    # TODO: for greener: only evaluate bicycle and walking segments surroundings
    # safer: avoid industrial zones by default
    # TODO: grab segments matrix and get data from there
    return {'route': 'route_stub'}
