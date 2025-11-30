"""
Mock client for testing without Kismet connection.

Generates realistic synthetic device detections for demonstration and testing.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple


class MockDetection:
    """Represents a mock device detection."""
    
    def __init__(self, mac: str, ssid: Optional[str] = None,
                 rssi: int = -70, latitude: float = 58.97,
                 longitude: float = 5.73, timestamp: Optional[datetime] = None):
        """Initialize mock detection."""
        self.mac = mac
        self.ssid = ssid
        self.rssi = rssi
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'mac': self.mac,
            'ssid': self.ssid,
            'rssi': self.rssi,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timestamp': self.timestamp.isoformat(),
        }


class MockClient:
    """
    Generates mock device detections for testing.
    
    Features:
    - Realistic RSSI values
    - Following behavior patterns
    - Multiple devices
    - Time-based simulation
    """
    
    # Common device MACs for testing
    MOCK_DEVICES = [
        ('AA:BB:CC:DD:EE:01', 'iPhone-1', 'smartphone'),
        ('AA:BB:CC:DD:EE:02', 'Android-Device', 'smartphone'),
        ('AA:BB:CC:DD:EE:03', 'iPad-1', 'tablet'),
        ('AA:BB:CC:DD:EE:04', 'Laptop-WiFi', 'computer'),
        ('AA:BB:CC:DD:EE:05', None, 'unknown'),  # Following device
        ('AA:BB:CC:DD:EE:06', None, 'unknown'),  # Following device
    ]
    
    # Base location (Stavanger, Norway)
    BASE_LAT = 58.9700
    BASE_LON = 5.7331
    
    def __init__(self, logger: logging.Logger = None):
        """
        Initialize mock client.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.current_time = datetime.now()
        self.device_state = {}
        self._initialize_device_state()
    
    def _initialize_device_state(self):
        """Initialize tracking state for each device."""
        for mac, ssid, device_type in self.MOCK_DEVICES:
            self.device_state[mac] = {
                'ssid': ssid,
                'type': device_type,
                'lat': self.BASE_LAT + random.uniform(-0.01, 0.01),
                'lon': self.BASE_LON + random.uniform(-0.01, 0.01),
                'rssi': random.randint(-85, -50),
                'rssi_trend': random.choice(['increasing', 'stable', 'decreasing']),
                'location_visits': random.randint(0, 3),
                'last_detection': None,
            }
    
    def generate_detections(self, count: int = 10) -> List[MockDetection]:
        """
        Generate mock detections.
        
        Args:
            count: Number of detections to generate
            
        Returns:
            List of MockDetection objects
        """
        detections = []
        
        # Generate detections for each device
        devices_to_detect = random.sample(self.MOCK_DEVICES, min(count, len(self.MOCK_DEVICES)))
        
        for _ in range(count):
            mac, ssid, device_type = random.choice(devices_to_detect)
            state = self.device_state[mac]
            
            # Update RSSI based on trend
            if state['rssi_trend'] == 'increasing':
                rssi = min(state['rssi'] + random.randint(1, 5), -50)
            elif state['rssi_trend'] == 'decreasing':
                rssi = max(state['rssi'] - random.randint(1, 5), -95)
            else:
                rssi = state['rssi'] + random.randint(-2, 2)
            
            state['rssi'] = rssi
            
            # Simulate location movement
            lat = state['lat'] + random.uniform(-0.0005, 0.0005)
            lon = state['lon'] + random.uniform(-0.0005, 0.0005)
            
            # Last 2 devices follow the observer (multiple locations)
            if mac in [self.MOCK_DEVICES[4][0], self.MOCK_DEVICES[5][0]]:
                if random.random() < 0.3:  # 30% chance to change location
                    lat = self.BASE_LAT + random.uniform(-0.005, 0.005)
                    lon = self.BASE_LON + random.uniform(-0.005, 0.005)
                    state['location_visits'] += 1
            
            state['lat'] = lat
            state['lon'] = lon
            
            detection = MockDetection(
                mac=mac,
                ssid=ssid,
                rssi=rssi,
                latitude=lat,
                longitude=lon,
                timestamp=self.current_time
            )
            
            detections.append(detection)
            self.logger.debug(f"Generated detection: {mac} RSSI={rssi} dBm")
        
        # Advance time slightly
        self.current_time += timedelta(seconds=random.randint(1, 5))
        
        return detections
    
    def generate_following_pattern(self) -> List[MockDetection]:
        """
        Generate detections showing following behavior.
        
        Returns:
            List of detections for a device following the observer
        """
        detections = []
        
        # Use one of the "following" devices
        mac = self.MOCK_DEVICES[4][0]
        state = self.device_state[mac]
        
        # Multiple location visits with high RSSI (getting closer)
        for i in range(5):
            rssi = -70 + (i * 3)  # Getting closer
            
            detection = MockDetection(
                mac=mac,
                ssid=state['ssid'],
                rssi=rssi,
                latitude=self.BASE_LAT + random.uniform(-0.002, 0.002),
                longitude=self.BASE_LON + random.uniform(-0.002, 0.002),
                timestamp=self.current_time + timedelta(seconds=i*30)
            )
            
            detections.append(detection)
        
        return detections
    
    def generate_scenario(self, scenario_type: str = 'normal') -> List[MockDetection]:
        """
        Generate detections for a specific scenario.
        
        Args:
            scenario_type: Type of scenario ('normal', 'threat', 'following')
            
        Returns:
            List of MockDetection objects
        """
        detections = []
        
        if scenario_type == 'normal':
            # Normal mixed detections
            detections = self.generate_detections(15)
        
        elif scenario_type == 'threat':
            # High detection count for one device
            mac = self.MOCK_DEVICES[0][0]
            state = self.device_state[mac]
            
            for i in range(20):
                detection = MockDetection(
                    mac=mac,
                    ssid=state['ssid'],
                    rssi=random.randint(-75, -55),
                    latitude=self.BASE_LAT + random.uniform(-0.001, 0.001),
                    longitude=self.BASE_LON + random.uniform(-0.001, 0.001),
                    timestamp=self.current_time + timedelta(seconds=i*2)
                )
                detections.append(detection)
        
        elif scenario_type == 'following':
            # Device with following behavior
            for _ in range(3):
                detections.extend(self.generate_following_pattern())
        
        return detections
    
    def get_device_info(self, mac: str) -> Optional[Dict]:
        """
        Get information about a mock device.
        
        Args:
            mac: Device MAC address
            
        Returns:
            Dictionary with device info or None
        """
        if mac not in self.device_state:
            return None
        
        state = self.device_state[mac]
        
        # Find device in MOCK_DEVICES
        device_info = None
        for m, ssid, dtype in self.MOCK_DEVICES:
            if m == mac:
                device_info = {'mac': m, 'ssid': ssid, 'type': dtype}
                break
        
        if not device_info:
            return None
        
        return {
            **device_info,
            'current_rssi': state['rssi'],
            'current_lat': state['lat'],
            'current_lon': state['lon'],
            'location_visits': state['location_visits'],
        }
    
    def list_all_devices(self) -> List[Dict]:
        """
        List all mock devices.
        
        Returns:
            List of device information dictionaries
        """
        devices = []
        for mac, ssid, dtype in self.MOCK_DEVICES:
            info = self.get_device_info(mac)
            if info:
                devices.append(info)
        return devices
    
    def reset(self):
        """Reset mock client state."""
        self.current_time = datetime.now()
        self._initialize_device_state()
        self.logger.info("Mock client reset")