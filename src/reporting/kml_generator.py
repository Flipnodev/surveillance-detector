"""
KML map generator for Google Earth visualization.

Creates professional KML files with threat-colored markers,
device paths, and location clustering for geographic analysis.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import simplekml
from data.location import Location, GPSCoordinate
from core.detector_engine import ThreatScore


class KMLGenerator:
    """
    Generate KML files for Google Earth visualization.
    
    Features:
    - Threat-level color coding
    - Device location markers
    - Centroid markers with clustering
    - Device paths showing movement
    - Metadata popups with threat information
    - Professional styling
    """
    
    # Color mapping for threat levels (KML uses AABBGGRR format)
    COLORS = {
        'none': 'ff00aa00',      # Green (0, 170, 0)
        'low': 'ff00aaff',       # Orange (255, 170, 0)
        'medium': 'ff0055ff',    # Dark orange (255, 85, 0)
        'high': 'ff0000ff',      # Red (255, 0, 0)
        'following': 'ffff00ff', # Magenta (255, 0, 255)
    }
    
    # Icon URLs (Google Maps icons)
    ICONS = {
        'threat_high': 'http://maps.google.com/mapfiles/kml/paddle/red-stars.png',
        'threat_medium': 'http://maps.google.com/mapfiles/kml/paddle/orange-stars.png',
        'threat_low': 'http://maps.google.com/mapfiles/kml/paddle/yellow-stars.png',
        'threat_none': 'http://maps.google.com/mapfiles/kml/paddle/grn-circle.png',
        'following': 'http://maps.google.com/mapfiles/kml/paddle/purple-stars.png',
        'centroid': 'http://maps.google.com/mapfiles/kml/pushpin/blu-pushpin.png',
        'device': 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png',
    }
    
    def __init__(self, logger: logging.Logger = None):
        """
        Initialize KML generator.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.kml = None
    
    def create_map(self, locations: List[Location], 
                   threat_scores: Dict[str, ThreatScore],
                   title: str = "Surveillance Detection Map") -> simplekml.Kml:
        """
        Create KML map with locations and threat data.
        
        Args:
            locations: List of Location objects
            threat_scores: Dict of MAC -> ThreatScore
            title: Map title
            
        Returns:
            simplekml.Kml object
        """
        self.kml = simplekml.Kml()
        self.kml.name = title
        
        # Create folders for organization
        threat_folder = self.kml.newfolder(name="Threats")
        location_folder = self.kml.newfolder(name="Locations")
        path_folder = self.kml.newfolder(name="Device Paths")
        
        self.logger.info(f"Creating KML map with {len(locations)} locations")
        
        # Add threat markers
        for mac, threat_score in threat_scores.items():
            if threat_score.location_count > 0:
                self._add_threat_marker(threat_folder, mac, threat_score)
        
        # Add location centroids
        for location in locations:
            self._add_location_marker(location_folder, location)
            
            # Add device paths
            if len(location.coordinates) > 1:
                self._add_path(path_folder, location)
        
        self.logger.info("KML map created successfully")
        return self.kml
    
    def _add_threat_marker(self, folder, mac: str, threat: ThreatScore):
        """Add threat marker to map."""
        try:
            # Get threat location (use first location visited)
            if not threat.device_mac or threat.location_count == 0:
                return
            
            # Create marker with threat info
            pnt = folder.newpoint(
                name=f"Threat: {mac}",
                description=self._create_threat_description(threat)
            )
            
            # Get icon and color based on threat level
            icon_url = self.ICONS.get(f'threat_{threat.level}', self.ICONS['device'])
            color = self.COLORS.get(threat.level, self.COLORS['threat_none'])
            
            pnt.style.iconstyle.icon.href = icon_url
            pnt.style.iconstyle.color = color
            pnt.style.iconstyle.scale = 1.5
            
            # Add label style
            pnt.style.labelstyle.color = color
            pnt.style.labelstyle.scale = 1.0
            
            self.logger.debug(f"Added threat marker: {mac}")
            
        except Exception as e:
            self.logger.error(f"Error adding threat marker: {e}")
    
    def _add_location_marker(self, folder, location: Location):
        """Add location centroid marker."""
        try:
            # Create folder for this location
            loc_folder = folder.newfolder(name=f"Location: {location.name}")
            
            # Add centroid marker
            pnt = loc_folder.newpoint(
                name=location.name,
                description=self._create_location_description(location),
                coords=[(location.centroid.longitude, location.centroid.latitude)]
            )
            
            pnt.style.iconstyle.icon.href = self.ICONS['centroid']
            pnt.style.iconstyle.color = self.COLORS['none']
            pnt.style.iconstyle.scale = 1.2
            
            # Add device location points
            for i, coord in enumerate(location.coordinates):
                device_pnt = loc_folder.newpoint(
                    name=f"Detection {i+1}",
                    coords=[(coord.longitude, coord.latitude)]
                )
                device_pnt.style.iconstyle.icon.href = self.ICONS['device']
                device_pnt.style.iconstyle.color = 'ff00ccff'
                device_pnt.style.iconstyle.scale = 0.8
            
            self.logger.debug(f"Added location marker: {location.name}")
            
        except Exception as e:
            self.logger.error(f"Error adding location marker: {e}")
    
    def _add_path(self, folder, location: Location):
        """Add device path (line connecting detections)."""
        try:
            if len(location.coordinates) < 2:
                return
            
            # Create coordinate list
            coords = [
                (c.longitude, c.latitude) for c in location.coordinates
            ]
            
            # Create line string
            line = folder.newlinestring(
                name=f"Path: {location.name}",
                description=f"Movement path at {location.name}",
                coords=coords
            )
            
            line.style.linestyle.color = 'ff0000ff'  # Red
            line.style.linestyle.width = 2
            
            self.logger.debug(f"Added path for location: {location.name}")
            
        except Exception as e:
            self.logger.error(f"Error adding path: {e}")
    
    def _create_threat_description(self, threat: ThreatScore) -> str:
        """Create HTML description for threat marker."""
        html = f"""
        <html>
            <head><title>Threat Details</title></head>
            <body style="font-family: Arial; font-size: 12px;">
                <h3>Device Threat Analysis</h3>
                <table border="1" cellpadding="5">
                    <tr><td><b>MAC Address</b></td><td>{threat.device_mac}</td></tr>
                    <tr><td><b>Threat Level</b></td><td>{threat.level.upper()}</td></tr>
                    <tr><td><b>Threat Score</b></td><td>{threat.score:.1f}/100</td></tr>
                    <tr><td><b>Detections</b></td><td>{threat.detection_count}</td></tr>
                    <tr><td><b>Dwell Time</b></td><td>{int(threat.dwell_time)} seconds</td></tr>
                    <tr><td><b>Locations Visited</b></td><td>{threat.location_count}</td></tr>
                    <tr><td><b>RSSI Trend</b></td><td>{threat.rssi_trend}</td></tr>
                    <tr><td><b>Following</b></td><td>{'YES' if threat.is_following else 'NO'}</td></tr>
                    <tr><td><b>Confidence</b></td><td>{threat.confidence*100:.0f}%</td></tr>
                </table>
            </body>
        </html>
        """
        return html
    
    def _create_location_description(self, location: Location) -> str:
        """Create HTML description for location marker."""
        html = f"""
        <html>
            <head><title>Location Details</title></head>
            <body style="font-family: Arial; font-size: 12px;">
                <h3>Location Analysis</h3>
                <table border="1" cellpadding="5">
                    <tr><td><b>Location Name</b></td><td>{location.name}</td></tr>
                    <tr><td><b>Latitude</b></td><td>{location.centroid.latitude:.6f}</td></tr>
                    <tr><td><b>Longitude</b></td><td>{location.centroid.longitude:.6f}</td></tr>
                    <tr><td><b>Duration</b></td><td>{int(location.duration)} seconds</td></tr>
                    <tr><td><b>Unique Devices</b></td><td>{location.device_count}</td></tr>
                    <tr><td><b>Detections</b></td><td>{len(location.coordinates)}</td></tr>
                </table>
                <br/>
                <b>Devices at this location:</b><br/>
        """
        
        for mac in location.device_macs:
            html += f"{mac}<br/>"
        
        html += """
            </body>
        </html>
        """
        return html
    
    def save(self, filepath: str) -> bool:
        """
        Save KML to file.
        
        Args:
            filepath: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.kml is None:
                self.logger.error("No KML map created yet")
                return False
            
            self.kml.save(filepath)
            self.logger.info(f"KML saved to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving KML: {e}")
            return False
    
    def get_kml_string(self) -> str:
        """
        Get KML as string.
        
        Returns:
            KML string
        """
        try:
            if self.kml is None:
                return ""
            return self.kml.kml()
        except Exception as e:
            self.logger.error(f"Error getting KML string: {e}")
            return ""