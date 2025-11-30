import math
from typing import List, Tuple
from data.location import GPSCoordinate


class GPSUtils:
    """GPS coordinate utilities and calculations."""
    
    EARTH_RADIUS_METERS = 6371000
    
    @staticmethod
    def calculate_distance(coord1: GPSCoordinate, coord2: GPSCoordinate) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            coord1: First coordinate
            coord2: Second coordinate
            
        Returns:
            Distance in meters
        """
        return coord1.distance_to(coord2)
    
    @staticmethod
    def calculate_centroid(coordinates: List[GPSCoordinate]) -> GPSCoordinate:
        """
        Calculate centroid (average) of coordinates.
        
        Args:
            coordinates: List of GPS coordinates
            
        Returns:
            Centroid coordinate
        """
        if not coordinates:
            return GPSCoordinate(0, 0)
        
        avg_lat = sum(c.latitude for c in coordinates) / len(coordinates)
        avg_lon = sum(c.longitude for c in coordinates) / len(coordinates)
        
        return GPSCoordinate(avg_lat, avg_lon)
    
    @staticmethod
    def calculate_bearing(from_coord: GPSCoordinate, 
                         to_coord: GPSCoordinate) -> float:
        """
        Calculate bearing (direction) from one point to another.
        
        Args:
            from_coord: Starting coordinate
            to_coord: Destination coordinate
            
        Returns:
            Bearing in degrees (0-360)
        """
        lat1 = math.radians(from_coord.latitude)
        lon1 = math.radians(from_coord.longitude)
        lat2 = math.radians(to_coord.latitude)
        lon2 = math.radians(to_coord.longitude)
        
        dlon = lon2 - lon1
        
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.atan2(x, y)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360
        
        return bearing
    
    @staticmethod
    def is_within_radius(coord: GPSCoordinate, center: GPSCoordinate,
                        radius_meters: float) -> bool:
        """
        Check if coordinate is within radius of center.
        
        Args:
            coord: Coordinate to check
            center: Center coordinate
            radius_meters: Search radius in meters
            
        Returns:
            True if within radius
        """
        distance = GPSUtils.calculate_distance(coord, center)
        return distance <= radius_meters