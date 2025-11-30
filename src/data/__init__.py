"""Data models and structures."""

from .device import Device, DeviceType
from .location import Location, GPSCoordinate

__all__ = ['Device', 'DeviceType', 'Location', 'GPSCoordinate']
