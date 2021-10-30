from math import asinh, pi, radians, tan, degrees, atan, sinh
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


def get_lat_lon_from_tile(x_tile: int, y_tile: int, zoom: int) -> Tuple[float, float]:
    n = 2.0 ** zoom
    lon_deg = x_tile / n * 360.0 - 180.0
    lat_rad = atan(sinh(pi * (1 - 2 * y_tile / n)))
    lat_deg = degrees(lat_rad)
    return lat_deg, lon_deg


def generate_route_id() -> int:
    """Generates temporary root id
    :return:
    """
    pass
