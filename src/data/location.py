# =============================================================================
# data/location.py
# =============================================================================
"""
Location data models for GPS tracking.

Represents geographic locations and clusters of detections.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import math


@dataclass
class GPSCoordinate:
    """
    Represents a GPS coordinate with metadata.
    
    Attributes:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        altitude: Altitude in meters (optional)
        timestamp: When coordinate was recorded
        accuracy: GPS accuracy in meters (optional)
    """
    
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    timestamp: Optional[datetime] = None
    accuracy: Optional[float] = None
    
    def __post_init__(self):
        """Validate coordinate values."""
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")
    
    def distance_to(self, other: 'GPSCoordinate') -> float:
        """
        Calculate distance to another coordinate using Haversine formula.
        
        Args:
            other: Target coordinate
            
        Returns:
            Distance in meters
        """
        # Earth's radius in meters
        R = 6371000
        
        # Convert to radians
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        delta_lat = math.radians(other.latitude - self.latitude)
        delta_lon = math.radians(other.longitude - self.longitude)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def to_tuple(self) -> Tuple[float, float]:
        """
        Get coordinate as (latitude, longitude) tuple.
        
        Returns:
            Tuple of lat, lon
        """
        return (self.latitude, self.longitude)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert coordinate to dictionary."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'accuracy': self.accuracy
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GPSCoordinate':
        """Create coordinate from dictionary."""
        return cls(
            latitude=data['latitude'],
            longitude=data['longitude'],
            altitude=data.get('altitude'),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None,
            accuracy=data.get('accuracy')
        )


@dataclass
class Location:
    """
    Represents a location cluster with metadata.
    
    Attributes:
        id: Unique location identifier
        centroid: Center point of location cluster
        coordinates: List of GPS coordinates in this location
        start_time: When monitoring started at this location
        end_time: When monitoring ended at this location
        device_macs: Set of device MACs detected at this location
        name: Optional human-readable location name
    """
    
    id: str
    centroid: GPSCoordinate
    coordinates: List[GPSCoordinate] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    device_macs: List[str] = field(default_factory=list)
    name: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """
        Calculate time spent at location in seconds.
        
        Returns:
            Duration in seconds or 0 if times not set
        """
        if not self.start_time or not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def device_count(self) -> int:
        """Get number of unique devices detected."""
        return len(set(self.device_macs))
    
    def add_device(self, mac: str) -> None:
        """
        Add device MAC to location.
        
        Args:
            mac: Device MAC address
        """
        if mac not in self.device_macs:
            self.device_macs.append(mac)
    
    def add_coordinate(self, coord: GPSCoordinate) -> None:
        """
        Add GPS coordinate to location.
        
        Args:
            coord: GPS coordinate to add
        """
        self.coordinates.append(coord)
        
        # Update time boundaries
        if coord.timestamp:
            if not self.start_time or coord.timestamp < self.start_time:
                self.start_time = coord.timestamp
            if not self.end_time or coord.timestamp > self.end_time:
                self.end_time = coord.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'centroid': self.centroid.to_dict(),
            'coordinates': [c.to_dict() for c in self.coordinates],
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration,
            'device_count': self.device_count,
            'device_macs': self.device_macs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """Create location from dictionary."""
        return cls(
            id=data['id'],
            centroid=GPSCoordinate.from_dict(data['centroid']),
            coordinates=[GPSCoordinate.from_dict(c) for c in data.get('coordinates', [])],
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            device_macs=data.get('device_macs', []),
            name=data.get('name')
        )