from math import asinh, pi, radians, tan
from typing import Tuple


def get_tile_from_coordinate(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[float, float]:
    """ Get tile coordinates from latitude and longitude
    :param lat_deg:
    :param lon_deg:
    :param zoom:
    :return:
    """
    lat_rad = radians(lat_deg)
    n = 2.0 ** zoom
    x_tile = int((lon_deg + 180.0) / 360.0 * n)
    y_tile = int((1.0 - asinh(tan(lat_rad)) / pi) / 2.0 * n)
    return x_tile, y_tile