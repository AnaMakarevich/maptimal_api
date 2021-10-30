import json


def get_tiles_set_by_temp_route_id(route_id: str) -> list:
    """Get tiles set from temporary memory that keeps track of routes currently in use
    :param route_id:
    :return:
    """
    # try to update the system, in case of problems -> log the problem but let the system keep functioning
    try:
        with open('mock_db/route_tracker.txt') as json_file:
            data = json.load(json_file)
            tiles_set = data[route_id]["tiles"]
            # TODO: ideally remove the route already from tracker
            return tiles_set
    except KeyError:
        # TODO: log error in logging system
        print("Route tracker was lost")
        return []
    except FileNotFoundError:
        # TODO: log error in logging system
        print("Tracking system was not initalized")
        return []


def update_tile_params(tile_id: str, user_feedback: dict) -> None:
    # TODO: replace files with DB
    # get values, one of: -1, 0, 1
    try:
        safe = user_feedback['safe']
        green = user_feedback['green']
        crowded = user_feedback['crowded']
        calm = user_feedback["calm"]
    except KeyError:
        # TODO: log error in logging system
        print("Invalid request from the client")
        return

    try:
        with open('mock_db/tiles_eval_data_17.txt') as json_file:
            data = json.load(json_file)
        if tile_id not in data:
            data[tile_id] = {'counter': 0, 'safe': 0, 'crowded': 0, 'green': 0, 'calm': 0}
        tile = data[tile_id]
        # update tiles params
        tile['counter'] += 1
        tile['safe'] += safe
        tile['crowded'] += crowded
        tile['green'] += green
        tile['calm'] += calm
        # save update
        with open('mock_db/tiles_eval_data_17.txt', 'w') as json_file:
            json.dump(data, json_file)
    except FileNotFoundError:
        # TODO: log error in logging system
        print("DB was not initialized")


def store_evaluation(user_feedback: dict) -> None:
    """Update tiles parameters based on user feedback.
    :param user_feedback: feedback dictionary from the user. MUST contain temporary route id, so that
        can extract tiles set.
    :return:
    """
    route_id = user_feedback["route_id"]
    # get tiles set from the tracking system
    tiles_set = get_tiles_set_by_temp_route_id(route_id)
    # update tile parameters
    for tile_id in tiles_set:
        update_tile_params(tile_id, user_feedback)
    return
