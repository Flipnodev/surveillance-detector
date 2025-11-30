# =============================================================================
# data/device.py
# =============================================================================
"""
Device data models for surveillance detection.

Represents wireless devices detected during monitoring sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class DeviceType(Enum):
    """Types of wireless devices."""
    WIFI_CLIENT = "wifi_client"
    WIFI_AP = "wifi_ap"
    BLUETOOTH = "bluetooth"
    UNKNOWN = "unknown"


@dataclass
class Device:
    """
    Represents a detected wireless device.
    
    Attributes:
        mac: MAC address (primary identifier)
        device_type: Type of device (WiFi, Bluetooth, etc.)
        first_seen: Timestamp of first detection
        last_seen: Timestamp of most recent detection
        detection_count: Number of times detected
        ssid: Associated SSID (for WiFi devices)
        manufacturer: Device manufacturer (from MAC OUI)
        rssi_values: List of RSSI signal strength values
        location_ids: List of location IDs where device was seen
    """
    
    mac: str
    device_type: DeviceType
    first_seen: datetime
    last_seen: datetime
    detection_count: int = 1
    ssid: Optional[str] = None
    manufacturer: Optional[str] = None
    rssi_values: List[int] = field(default_factory=list)
    location_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize device data."""
        # Normalize MAC address to uppercase with colons
        self.mac = self.mac.upper().replace('-', ':').replace('.', ':')
        
        # Ensure device_type is enum
        if isinstance(self.device_type, str):
            try:
                self.device_type = DeviceType(self.device_type)
            except ValueError:
                self.device_type = DeviceType.UNKNOWN
    
    @property
    def dwell_time(self) -> float:
        """
        Calculate dwell time in seconds.
        
        Returns:
            Time difference between first and last seen
        """
        return (self.last_seen - self.first_seen).total_seconds()
    
    @property
    def average_rssi(self) -> Optional[float]:
        """
        Calculate average RSSI value.
        
        Returns:
            Mean RSSI or None if no values
        """
        if not self.rssi_values:
            return None
        return sum(self.rssi_values) / len(self.rssi_values)
    
    @property
    def rssi_trend(self) -> Optional[str]:
        """
        Determine RSSI trend (getting closer or farther).
        
        Returns:
            'increasing' (getting closer), 'decreasing' (moving away), or 'stable'
        """
        if len(self.rssi_values) < 3:
            return 'stable'
        
        # Compare first third vs last third of readings
        third = len(self.rssi_values) // 3
        early_avg = sum(self.rssi_values[:third]) / third
        late_avg = sum(self.rssi_values[-third:]) / third
        
        diff = late_avg - early_avg
        
        if diff > 5:  # Getting closer (higher RSSI)
            return 'increasing'
        elif diff < -5:  # Moving away (lower RSSI)
            return 'decreasing'
        else:
            return 'stable'
    
    def update_detection(self, 
                        timestamp: datetime, 
                        rssi: Optional[int] = None,
                        location_id: Optional[str] = None) -> None:
        """
        Update device with new detection event.
        
        Args:
            timestamp: Detection timestamp
            rssi: Signal strength value
            location_id: Location where detected
        """
        self.last_seen = timestamp
        self.detection_count += 1
        
        if rssi is not None:
            self.rssi_values.append(rssi)
        
        if location_id and location_id not in self.location_ids:
            self.location_ids.append(location_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert device to dictionary representation.
        
        Returns:
            Dictionary with device data
        """
        return {
            'mac': self.mac,
            'device_type': self.device_type.value,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'detection_count': self.detection_count,
            'dwell_time_seconds': self.dwell_time,
            'ssid': self.ssid,
            'manufacturer': self.manufacturer,
            'average_rssi': self.average_rssi,
            'rssi_trend': self.rssi_trend,
            'rssi_values': self.rssi_values,
            'location_count': len(self.location_ids),
            'location_ids': self.location_ids
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Device':
        """
        Create device from dictionary.
        
        Args:
            data: Dictionary with device data
            
        Returns:
            Device instance
        """
        return cls(
            mac=data['mac'],
            device_type=DeviceType(data['device_type']),
            first_seen=datetime.fromisoformat(data['first_seen']),
            last_seen=datetime.fromisoformat(data['last_seen']),
            detection_count=data.get('detection_count', 1),
            ssid=data.get('ssid'),
            manufacturer=data.get('manufacturer'),
            rssi_values=data.get('rssi_values', []),
            location_ids=data.get('location_ids', [])
        )