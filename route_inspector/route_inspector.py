import googlemaps
from datetime import datetime

import requests

from OSMPythonTools.overpass import Overpass, overpassQueryBuilder

from route_inspector.api_keys import GOOGLE_MAPS_API_KEY, POLLUTION_API_KEY
from route_inspector.route_tracking import set_route_to_pending_mode
from route_inspector.tile_processor import get_tile_characteristics
from route_inspector.utils import get_tile_from_coordinate, get_lat_lon_from_tile, generate_route_id

ZOOM_LEVEL_TILES = 17

overpass = Overpass()


# default google maps directions signature for reference
def directions(origin, destination, mode=None,
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
        air_quality_index = response.json()['list'][0]['main']['aqi']
        return air_quality_index
    else:
        raise Exception("Air pollution API failed")


def get_osm_details_for_tile(tile_x, tile_y):
    bbox = list(get_bbox_of_tile(tile_x, tile_y))
    tree_count_query = overpassQueryBuilder(bbox=bbox, elementType='node',
                                            selector='"natural"="tree"', out='count', includeGeometry=True)
    tree_count_result = overpass.query(tree_count_query)
    tree_count = tree_count_result.countNodes()

    industrial_count_query = overpassQueryBuilder(bbox=bbox, elementType=['node', 'way'],
                                                  selector='"landuse"="industrial"', out='count', includeGeometry=True)
    industrial_count_result = overpass.query(industrial_count_query)
    industrial_count = industrial_count_result.countNodes() + industrial_count_result.countWays()

    parks_query = overpassQueryBuilder(bbox=bbox, elementType='way',
                                       selector='"leisure"="park"', out='body', includeGeometry=True)
    parks_result = overpass.query(parks_query)
    parks = []
    for park in parks_result.toJSON()['elements']:
        park_bounds = park['bounds']
        park_bbox = [park_bounds[key] for key in ['minlat', 'minlon', 'maxlat', 'maxlon']]
        parks.append({'bbox': park_bbox})

    return {
        'tree_count': tree_count,
        'industrial_count': industrial_count,
        'park_count': len(parks),
    }


def assess_route_quality(tree_counts, industrial_counts, park_counts, air_quality_data):
    """
    :return: float - quality score
    """
    # TODO: use fancy ML model from scikit-learn
    # park and industrial are big areas, use multiplier for them
    park_industrial_score = (sum(park_counts) - sum(industrial_counts)) * 50

    # this counts separate trees, so the number can be quite big
    tree_score = sum(tree_counts)

    # mean air quality index (1 - best, 5 - worst)
    mean_air_q_index = sum(air_quality_data) / len(air_quality_data)
    air_score = (3 - mean_air_q_index) * 10  # [20, 10, 0, -10, -20]

    return park_industrial_score + tree_score + air_score


def process_route(route: dict) -> dict:
    # TODO: check if already exists based on tile
    # TODO: extract existing segments
    # TODO: store route
    # extract segments
    start_location = route["legs"][0]["steps"][0]["start_location"]
    end_location = route["legs"][-1]["steps"][-1]["end_location"]

    lat, lon = start_location["lat"], start_location["lng"]
    start_tile = get_tile_from_coordinate(lat, lon, ZOOM_LEVEL_TILES)
    air_quality_index_at_start = get_air_quality_index(lat, lon)
    tile_x_seq = [start_tile[0]]
    tile_y_seq = [start_tile[1]]
    tile_set = []
    air_quality_data = [air_quality_index_at_start]  # from air pollution data

    # from openstreetmap
    tree_counts = []
    industrial_counts = []
    park_counts = []

    # TODO: exclude non-walking and non-bicycling
    for leg in route["legs"]:
        steps = leg["steps"]
        for step in steps:
            end_location = step["end_location"]
            lat, lon = end_location["lat"], end_location["lng"]
            # get tile coordinates (mine-craftize)
            # start_tile = get_tile_from_coordinate(*start_location, ZOOM_LEVEL_TILES)
            end_tile_x, end_tile_y = get_tile_from_coordinate(lat, lon, ZOOM_LEVEL_TILES)
            # get known params about this tile based on previous evaluations
            tile_characteristics = get_tile_characteristics(end_tile_x, end_tile_y)
            # store tile coordinates of the end point if the tile changes
            # TODO: add condition of terrain change
            if not ((end_tile_x == tile_x_seq[-1]) and (end_tile_y == tile_y_seq[-1])):
                tile_x_seq.append(end_tile_x)
                tile_y_seq.append(end_tile_y)
                tile_set.append(f"{end_tile_x}-{end_tile_y}")
                # tile
                air_quality_index_at_end = get_air_quality_index(lat, lon)
                air_quality_data.append(air_quality_index_at_end)

                tile_osm_details = get_osm_details_for_tile(end_tile_x, end_tile_y)
                tree_counts.append(tile_osm_details['tree_count'])
                industrial_counts.append(tile_osm_details['industrial_count'])
                park_counts.append(tile_osm_details['park_count'])
                # query landscape type for tiles if: only for start tile if the distance is small
    # TODO: post-processing step that merges tiles together so that small segments are ignored
    # TODO: after merging merge other arrays as well
    score = assess_route_quality(tree_counts, industrial_counts, park_counts, air_quality_data)
    # TODO: LATER: for each route:
    # goal -> find waypoints of interest and rebuild the route using these waypoints
    route_id = generate_route_id()
    route['route_id'] = route_id
    set_route_to_pending_mode(route_id, tile_set)

    return {'green': 1, 'crowded': 1}


def get_bbox_of_tile(xtile, ytile, zoom=ZOOM_LEVEL_TILES):
    """ Get the bounding box of a tile

    :return: tuple(xmin, ymin, xmax, ymax)
    """
    lat1, lon1 = get_lat_lon_from_tile(xtile, ytile, zoom)
    lat2, lon2 = get_lat_lon_from_tile(xtile + 1, ytile + 1, zoom)
    max_lat = max(lat1, lat2)
    min_lat = min(lat1, lat2)
    max_lon = max(lon1, lon2)
    min_lon = min(lon1, lon2)
    return min_lat, min_lon, max_lat, max_lon


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
    default_route = routes[0]
    for route in routes:
        # get bounding box since we can search in this area
        bounding_box = route['bounds']
        # TODO: get nearby cool places from the center
        route_quality, route_id = process_route(route)
    # TODO: choose best route
    #  TODO: TRY TO BUILD BETTER BY USING VIA_WAYPOINT
    # get base route from google maps

    green = input_params['green']
    pollution_free = input_params['pollution_free']
    less_crowded = input_params['less_crowded']
    safer = input_params['safer']
    # TODO: for greener: only evaluate bicycle and walking segments surroundings
    # safer: avoid industrial zones by default
    # TODO: replace with actual route suggestion
    route = default_route
    route_evaluation_result = None
    return route, route_evaluation_result, route.get('route_id', 'crowded')
