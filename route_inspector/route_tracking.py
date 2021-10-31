import json
import time

TTL = 24 * 60 * 60


def set_route_to_pending_mode(route_id, tiles_set, route_time=60*60):
    # store route id, timestamp and tileset, TTL is global
    with open('mock_db/pending_routes.txt') as json_file:
        data = json.load(json_file)
    with open('mock_db/pending_routes.txt', 'w') as json_file:
        data.setdefault(route_id, {})["tiles"] = tiles_set
        data[route_id]["added"] = round(time.time())
        # add route time to give a better estimate of when the route should be disabled if it's activated
        data[route_id]["route_time"] = route_time
        json.dump(data, json_file)


def track_route(route_id: str):
    """Add route to routes currently in progress and increment counter for the segments
    :return:
    """
    # TODO: setup segment matrix
    # TODO: increment counters for the segments in the route
    # get the route from pending
    with open('mock_db/pending_routes.txt') as json_file:
        data = json.load(json_file)
    selected_route = data[route_id]
    # get route time (in seconds) to know when to decrement tiles counters
    route_ttl = selected_route["route_time"]
    start_time = round(time.time())
    tiles = selected_route["tiles"]
    # add tracker
    with open('mock_db/route_tracker.txt') as json_file:
        route_trackers = json.load(json_file)
        route_trackers.setdefault(route_id, {})["route_ttl"] = route_ttl
        route_trackers[route_id]["started"] = start_time
        route_trackers[route_id]["tiles"] = tiles
    with open('mock_db/route_tracker.txt', 'w') as json_file:
        json.dump(route_trackers, json_file)
        # TODO: ideally schedule removing already
    # increment tiles
    with open('mock_db/active_tiles.txt') as json_file:
        # increment tiles counters
        active_tiles = json.load(json_file)
        for tile in tiles:
            if tile in active_tiles:
                active_tiles[tile] += 1
            else:
                active_tiles[tile] = 0
    with open('mock_db/active_tiles.txt', 'w') as json_file:
        json.dump(active_tiles, json_file)


def stop_tracking(route_id: str):
    with open('mock_db/route_tracker.txt') as json_file:
        route_trackers = json.load(json_file)
        try:
            tiles = route_trackers[route_id]["tiles"]
        except KeyError:
            # TODO: logging
            print("Tracker doesn't exist")
            return
        # increment tiles counters
    with open('mock_db/active_tiles.txt') as json_file:
        active_tiles = json.load(json_file)
        for tile in tiles:
            if tile in active_tiles:
                active_tiles[tile] -= 1
            else:
                active_tiles[tile] = 0
    with open('mock_db/active_tiles.txt', 'w') as json_file:
        json.dump(active_tiles, json_file)
    # remove tracker from trackers (also to make sure we don't decrement twice
    route_trackers.pop(route_id, None)
    with open('mock_db/route_tracker.txt', 'w') as json_file:
        json.dump(route_trackers, json_file)

