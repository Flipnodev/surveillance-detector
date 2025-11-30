"""
Core detection engine for surveillance monitoring.

Processes device detections, tracks locations, calculates threat scores,
and identifies following behavior patterns.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import random

from data.device import Device, DeviceType
from data.location import Location, GPSCoordinate


@dataclass
class ThreatScore:
    """Represents a threat assessment for a device."""
    device_mac: str
    score: float  # 0-100
    level: str  # low, medium, high
    detection_count: int
    dwell_time: float
    rssi_trend: str
    location_count: int
    is_following: bool
    confidence: float


class DetectorEngine:
    """
    Core detection and analysis engine.
    
    Tracks devices, calculates threat scores, detects following behavior,
    and manages time-window analysis.
    """
    
    def __init__(self, config, logger: logging.Logger):
        """
        Initialize detection engine.
        
        Args:
            config: Application configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # Storage
        self.devices: Dict[str, Device] = {}
        self.locations: Dict[str, Location] = {}
        self.threat_scores: Dict[str, ThreatScore] = {}
        
        # Session tracking
        self.session_start = datetime.now()
        self.detection_count = 0
        self.is_running = False
        
        # Time windows for analysis (in minutes)
        self.time_windows = config.detection.time_windows
        
        # Threat scoring weights
        self.weights = {
            'detection_count': config.detection.scoring.detection_count_weight,
            'dwell_time': config.detection.scoring.dwell_time_weight,
            'rssi_trend': config.detection.scoring.rssi_trend_weight,
            'location_count': config.detection.scoring.location_count_weight,
        }
        
        # Threat level thresholds
        self.threat_levels = config.detection.threat_levels
        
        self.logger.info("DetectorEngine initialized")
    
    def start(self):
        """Start the detection engine."""
        self.is_running = True
        self.session_start = datetime.now()
        self.logger.info("Detection engine started")
    
    def stop(self):
        """Stop the detection engine."""
        self.is_running = False
        self.logger.info("Detection engine stopped")
    
    def process_detection(self, mac: str, ssid: Optional[str] = None,
                        rssi: int = -70, latitude: Optional[float] = None,
                        longitude: Optional[float] = None,
                        timestamp: Optional[datetime] = None) -> Optional[Device]:
        """
        Process a device detection event.
        
        Args:
            mac: Device MAC address
            ssid: Associated SSID (WiFi only)
            rssi: Signal strength in dBm
            latitude: Current latitude
            longitude: Current longitude
            timestamp: Detection timestamp
            
        Returns:
            Updated Device object or None if error
        """
        if not self.is_running:
            return None
        
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            # Normalize MAC
            mac = mac.upper().replace('-', ':').replace('.', ':')
            
            # Get or create device
            if mac not in self.devices:
                self.devices[mac] = Device(
                    mac=mac,
                    device_type=DeviceType.WIFI_CLIENT,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    ssid=ssid
                )
                self.logger.debug(f"New device detected: {mac}")
            
            device = self.devices[mac]
            device.update_detection(timestamp, rssi=rssi)
            self.detection_count += 1
            
            # Process GPS location if provided
            if latitude is not None and longitude is not None:
                self._process_location(device, latitude, longitude, timestamp)
            
            return device
            
        except Exception as e:
            self.logger.error(f"Error processing detection: {e}")
            return None
    
    def _process_location(self, device: Device, latitude: float,
                         longitude: float, timestamp: datetime):
        """
        Process GPS location for a device detection.
        
        Args:
            device: Device object
            latitude: Location latitude
            longitude: Location longitude
            timestamp: Detection timestamp
        """
        try:
            coord = GPSCoordinate(latitude, longitude, timestamp=timestamp)
            
            # Find nearest location cluster (simple proximity check)
            nearest_loc = None
            min_distance = self.config.clustering.eps_meters
            
            for loc in self.locations.values():
                dist = loc.centroid.distance_to(coord)
                if dist < min_distance:
                    nearest_loc = loc
                    min_distance = dist
            
            # Use nearest location or create new one
            if nearest_loc:
                nearest_loc.add_coordinate(coord)
                nearest_loc.add_device(device.mac)
                device.update_detection(timestamp, location_id=nearest_loc.id)
            else:
                # Create new location
                loc_id = f"loc_{len(self.locations):04d}"
                location = Location(
                    id=loc_id,
                    centroid=coord,
                    name=f"Location {len(self.locations)}"
                )
                location.add_coordinate(coord)
                location.add_device(device.mac)
                self.locations[loc_id] = location
                device.update_detection(timestamp, location_id=loc_id)
                
        except Exception as e:
            self.logger.error(f"Error processing location: {e}")
    
    def calculate_threat_scores(self) -> Dict[str, ThreatScore]:
        """
        Calculate threat scores for all tracked devices.
        
        Returns:
            Dictionary of device MAC -> ThreatScore
        """
        self.threat_scores = {}
        
        for mac, device in self.devices.items():
            score = self._calculate_device_threat(device)
            self.threat_scores[mac] = score
        
        return self.threat_scores
    
    def _calculate_device_threat(self, device: Device) -> ThreatScore:
        """
        Calculate threat score for a single device.
        
        Args:
            device: Device object
            
        Returns:
            ThreatScore object
        """
        now = datetime.now()
        
        # Detection count score (0-30)
        min_detections = self.config.detection.min_detections
        detection_score = min(
            (device.detection_count / max(min_detections, 1)) * 30,
            30
        )
        
        # Dwell time score (0-30)
        min_dwell = self.config.detection.min_dwell_time
        dwell_seconds = device.dwell_time
        dwell_score = min(
            (dwell_seconds / max(min_dwell, 1)) * 30,
            30
        )
        
        # RSSI trend score (0-20)
        rssi_trend = device.rssi_trend or 'stable'
        rssi_score = {
            'increasing': 20,  # Getting closer = more threatening
            'stable': 10,
            'decreasing': 5,   # Moving away = less threatening
        }.get(rssi_trend, 10)
        
        # Location count score (0-20)
        location_score = min(
            (len(device.location_ids) / 3) * 20,
            20
        )
        
        # Combined score
        total_score = (
            detection_score * self.weights['detection_count'] +
            dwell_score * self.weights['dwell_time'] +
            rssi_score * self.weights['rssi_trend'] +
            location_score * self.weights['location_count']
        )
        
        # Check for following behavior
        is_following = self._detect_following_behavior(device)
        if is_following:
            total_score *= 1.5  # Boost score for following behavior
            total_score = min(total_score, 100)
        
        # Determine threat level
        if total_score >= self.threat_levels.high:
            level = 'high'
        elif total_score >= self.threat_levels.medium:
            level = 'medium'
        elif total_score >= self.threat_levels.low:
            level = 'low'
        else:
            level = 'none'
        
        confidence = min(device.detection_count / 10, 1.0)
        
        return ThreatScore(
            device_mac=device.mac,
            score=total_score,
            level=level,
            detection_count=device.detection_count,
            dwell_time=dwell_seconds,
            rssi_trend=rssi_trend,
            location_count=len(device.location_ids),
            is_following=is_following,
            confidence=confidence
        )
    
    def _detect_following_behavior(self, device: Device) -> bool:
        """
        Detect if a device is following the observer.
        
        Following behavior indicators:
        - Multiple location visits
        - Increasing RSSI trend
        - High detection count
        - Consistent proximity
        
        Args:
            device: Device object
            
        Returns:
            True if following behavior detected
        """
        # Need multiple detections
        if device.detection_count < self.config.detection.min_detections:
            return False
        
        # Need multiple locations
        if len(device.location_ids) < 2:
            return False
        
        # Check RSSI trend (getting closer)
        if device.rssi_trend == 'increasing':
            rssi_score = 1
        else:
            rssi_score = 0
        
        # Check time between locations (should be recent)
        if device.dwell_time < 3600:  # Within 1 hour
            time_score = 1
        else:
            time_score = 0
        
        # Check detection count
        if device.detection_count > self.config.detection.min_detections * 2:
            detection_score = 1
        else:
            detection_score = 0
        
        # Following if 2+ indicators present
        following_indicators = rssi_score + time_score + detection_score
        return following_indicators >= 2
    
    def get_threats(self, level: Optional[str] = None,
                   min_score: float = 0) -> List[ThreatScore]:
        """
        Get threat scores, optionally filtered.
        
        Args:
            level: Filter by threat level ('low', 'medium', 'high')
            min_score: Minimum threat score to include
            
        Returns:
            List of ThreatScore objects sorted by score (highest first)
        """
        threats = list(self.threat_scores.values())
        
        # Filter
        if level:
            threats = [t for t in threats if t.level == level]
        threats = [t for t in threats if t.score >= min_score]
        
        # Sort by score (highest first)
        threats.sort(key=lambda t: t.score, reverse=True)
        
        return threats
    
    def get_following_threats(self) -> List[ThreatScore]:
        """Get threats with following behavior detected."""
        return [t for t in self.threat_scores.values() if t.is_following]
    
    def get_statistics(self) -> Dict:
        """
        Get current session statistics.
        
        Returns:
            Dictionary with statistics
        """
        elapsed = datetime.now() - self.session_start
        elapsed_minutes = max(elapsed.total_seconds() / 60, 1)
        
        high_threats = len(self.get_threats('high'))
        medium_threats = len(self.get_threats('medium'))
        low_threats = len(self.get_threats('low'))
        following_threats = len(self.get_following_threats())
        
        return {
            'session_start': self.session_start.isoformat(),
            'elapsed_seconds': elapsed.total_seconds(),
            'device_count': len(self.devices),
            'location_count': len(self.locations),
            'detection_count': self.detection_count,
            'detections_per_minute': self.detection_count / elapsed_minutes,
            'threat_summary': {
                'high': high_threats,
                'medium': medium_threats,
                'low': low_threats,
                'following': following_threats,
            }
        }
    
    def clear_session(self):
        """Clear all session data."""
        self.devices.clear()
        self.locations.clear()
        self.threat_scores.clear()
        self.detection_count = 0
        self.session_start = datetime.now()
        self.logger.info("Session data cleared")