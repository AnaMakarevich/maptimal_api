import json
from typing import Union


def get_tile_characteristics(tile_x: int, tile_y: int, zoom: int = 17) -> Union[dict, None]:
    """Get tile characteristics based on previous assessments
    :param tile_x:
    :param tile_y:
    :param zoom:
    :return:
    """
    tile_id = f"{tile_x}-{tile_y}"
    try:
        with open(f'mock_db/tiles_eval_data_{zoom}.txt') as json_file:
            data = json.load(json_file)
            try:
                # avoid aliasing
                tile = data[tile_id].copy()
                count = tile['counter']
                try:
                    for key in tile.keys():
                        if key != "counter":
                            tile[key] /= count
                    tile.pop('counter', None)
                    return tile
                except KeyError:
                    print("Data was stored improperly")
                    return None
            except KeyError:
                print("No information about the tile yet")
                return None
    except FileNotFoundError:
        print("System was not initialized")
        return None
