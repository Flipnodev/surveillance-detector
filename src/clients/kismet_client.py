"""
Kismet REST API client for real wireless device monitoring.

Connects to Kismet server and fetches live WiFi/Bluetooth device data,
GPS coordinates, and signal strength information.
"""

import logging
import requests
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class KismetDevice:
    """Represents a device detected by Kismet."""
    mac: str
    device_type: str  # 'WiFi', 'Bluetooth', etc.
    first_seen: datetime
    last_seen: datetime
    signal_dbm: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    ssid: Optional[str] = None
    manuf: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'mac': self.mac,
            'device_type': self.device_type,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'signal_dbm': self.signal_dbm,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'ssid': self.ssid,
            'manuf': self.manuf,
        }


class KismetClient:
    """
    Client for Kismet wireless detection server.
    
    Provides methods to:
    - Connect to Kismet REST API
    - Fetch device list
    - Extract GPS coordinates
    - Monitor real-time detections
    - Handle errors and reconnection
    """
    
    def __init__(self, host: str = 'localhost', port: int = 2501,
                 username: str = 'kismet', password: str = 'kismet',
                 logger: logging.Logger = None):
        """
        Initialize Kismet client.
        
        Args:
            host: Kismet server host
            port: Kismet REST API port
            username: API username (if enabled)
            password: API password (if enabled)
            logger: Logger instance
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.logger = logger or logging.getLogger(__name__)
        
        self.base_url = f"http://{host}:{port}"
        self.is_connected = False
        self.last_error = None
        self.device_cache = {}
        self.last_update = None
        
        self.logger.info(f"KismetClient initialized: {self.base_url}")
    
    def connect(self) -> bool:
        """
        Test connection to Kismet server.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            # Test connection to status endpoint
            url = f"{self.base_url}/kismet/status"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                self.is_connected = True
                self.logger.info(f"Connected to Kismet at {self.base_url}")
                return True
            else:
                self.is_connected = False
                self.last_error = f"Status code: {response.status_code}"
                self.logger.warning(f"Failed to connect to Kismet: {self.last_error}")
                return False
                
        except requests.exceptions.ConnectionError as e:
            self.is_connected = False
            self.last_error = f"Connection error: {str(e)}"
            self.logger.error(f"Cannot connect to Kismet: {self.last_error}")
            return False
        except Exception as e:
            self.is_connected = False
            self.last_error = str(e)
            self.logger.error(f"Error connecting to Kismet: {self.last_error}")
            return False
    
    def get_devices(self) -> List[KismetDevice]:
        """
        Fetch all devices from Kismet.
        
        Returns:
            List of KismetDevice objects
        """
        if not self.is_connected:
            if not self.connect():
                return []
        
        try:
            url = f"{self.base_url}/devices/views/all/devices.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                self.logger.error(f"Error fetching devices: {response.status_code}")
                return []
            
            devices_data = response.json()
            devices = []
            
            for device_data in devices_data:
                try:
                    device = self._parse_device(device_data)
                    if device:
                        devices.append(device)
                        self.device_cache[device.mac] = device
                except Exception as e:
                    self.logger.debug(f"Error parsing device: {e}")
                    continue
            
            self.last_update = datetime.now()
            self.logger.debug(f"Fetched {len(devices)} devices from Kismet")
            return devices
            
        except Exception as e:
            self.logger.error(f"Error fetching devices: {e}")
            return []
    
    def _parse_device(self, device_data: Dict) -> Optional[KismetDevice]:
        """
        Parse device data from Kismet JSON.
        
        Args:
            device_data: Raw device data from Kismet
            
        Returns:
            KismetDevice object or None if parsing fails
        """
        try:
            # Get MAC address
            mac = device_data.get('kismet.device.base.macaddr', '')
            if not mac:
                return None
            
            # Get device type
            device_type = 'Unknown'
            if device_data.get('kismet.device.base.type'):
                device_type = device_data.get('kismet.device.base.type')
            elif device_data.get('kismet.device.base.subtype'):
                # Try to detect from subtype
                subtype = device_data.get('kismet.device.base.subtype')
                if 'wifi' in str(subtype).lower():
                    device_type = 'WiFi'
                elif 'bluetooth' in str(subtype).lower():
                    device_type = 'Bluetooth'
            
            # Get timestamps
            first_seen = self._parse_timestamp(
                device_data.get('kismet.device.base.first_time', 0)
            )
            last_seen = self._parse_timestamp(
                device_data.get('kismet.device.base.last_time', 0)
            )
            
            # Get signal strength
            signal_dbm = device_data.get('kismet.device.base.signal.last_dbm', -70)
            
            # Get GPS coordinates
            latitude = None
            longitude = None
            altitude = None
            
            if device_data.get('kismet.device.base.location'):
                location = device_data.get('kismet.device.base.location')
                latitude = location.get('kismet.common.location.lat')
                longitude = location.get('kismet.common.location.lon')
                altitude = location.get('kismet.common.location.alt')
            
            # Get SSID (for WiFi)
            ssid = None
            if device_data.get('kismet.device.base.commonname'):
                ssid = device_data.get('kismet.device.base.commonname')
            
            # Get manufacturer
            manuf = device_data.get('kismet.device.base.manuf')
            
            return KismetDevice(
                mac=mac,
                device_type=device_type,
                first_seen=first_seen,
                last_seen=last_seen,
                signal_dbm=signal_dbm,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                ssid=ssid,
                manuf=manuf
            )
            
        except Exception as e:
            self.logger.debug(f"Error parsing device: {e}")
            return None
    
    def _parse_timestamp(self, timestamp: int) -> datetime:
        """
        Parse Kismet timestamp (Unix time in seconds).
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            datetime object
        """
        try:
            if timestamp == 0:
                return datetime.now()
            return datetime.fromtimestamp(timestamp)
        except:
            return datetime.now()
    
    def get_device_by_mac(self, mac: str) -> Optional[KismetDevice]:
        """
        Get specific device by MAC address.
        
        Args:
            mac: Device MAC address
            
        Returns:
            KismetDevice or None if not found
        """
        # Try cache first
        if mac in self.device_cache:
            return self.device_cache[mac]
        
        # Fetch from server
        devices = self.get_devices()
        for device in devices:
            if device.mac == mac:
                return device
        
        return None
    
    def get_gps_data(self) -> Optional[Tuple[float, float]]:
        """
        Get current GPS location from Kismet.
        
        Returns:
            Tuple of (latitude, longitude) or None
        """
        if not self.is_connected:
            if not self.connect():
                return None
        
        try:
            url = f"{self.base_url}/gps/location.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            gps_data = response.json()
            
            # Extract coordinates
            if isinstance(gps_data, dict):
                lat = gps_data.get('kismet.gps.lat')
                lon = gps_data.get('kismet.gps.lon')
                
                if lat is not None and lon is not None:
                    return (lat, lon)
            elif isinstance(gps_data, list) and len(gps_data) > 0:
                first = gps_data[0]
                lat = first.get('kismet.gps.lat')
                lon = first.get('kismet.gps.lon')
                
                if lat is not None and lon is not None:
                    return (lat, lon)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error getting GPS data: {e}")
            return None
    
    def get_device_count(self) -> int:
        """Get total number of devices."""
        return len(self.device_cache)
    
    def get_status(self) -> Dict:
        """
        Get Kismet server status.
        
        Returns:
            Status dictionary
        """
        if not self.is_connected:
            if not self.connect():
                return {'connected': False, 'error': self.last_error}
        
        try:
            url = f"{self.base_url}/kismet/status"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'connected': False, 'error': f"Status code: {response.status_code}"}
                
        except Exception as e:
            return {'connected': False, 'error': str(e)}
    
    def disconnect(self):
        """Disconnect from Kismet."""
        self.is_connected = False
        self.device_cache.clear()
        self.logger.info("Disconnected from Kismet")
    
    def __repr__(self) -> str:
        """String representation."""
        status = "connected" if self.is_connected else "disconnected"
        return f"KismetClient({self.base_url}, {status})"