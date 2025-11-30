"""
JSON and CSV export functionality for surveillance data.

Provides structured data export for integration with other tools
and systems for further analysis.
"""

import json
import csv
import logging
from typing import List, Dict, Optional
from datetime import datetime
from core.detector_engine import ThreatScore
from data.location import Location
from data.device import Device


class DataExporter:
    """
    Export surveillance data in multiple formats.
    
    Supported formats:
    - JSON (complete data structure)
    - CSV (tabular format)
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        Initialize data exporter.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    # ==================== JSON Export ====================
    
    def export_to_json(self, threats: Dict[str, ThreatScore],
                      locations: List[Location],
                      devices: Optional[Dict[str, Device]] = None,
                      metadata: Optional[Dict] = None) -> str:
        """
        Export all data to JSON format.
        
        Args:
            threats: Threat scores dictionary
            locations: List of locations
            devices: Optional devices dictionary
            metadata: Optional metadata (session info, etc.)
            
        Returns:
            JSON string
        """
        export_data = {
            'metadata': metadata or {
                'timestamp': datetime.now().isoformat(),
                'version': '3.0.0',
                'system': 'Surveillance Detection System'
            },
            'summary': self._create_summary(threats, locations),
            'threats': self._serialize_threats(threats),
            'locations': self._serialize_locations(locations),
            'devices': self._serialize_devices(devices) if devices else None,
        }
        
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        self.logger.info("Data exported to JSON format")
        return json_str
    
    def _create_summary(self, threats: Dict[str, ThreatScore],
                       locations: List[Location]) -> Dict:
        """Create summary statistics."""
        threat_counts = {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
        following_count = 0
        total_score = 0
        
        for threat in threats.values():
            threat_counts[threat.level] += 1
            if threat.is_following:
                following_count += 1
            total_score += threat.score
        
        return {
            'export_time': datetime.now().isoformat(),
            'total_devices': len(threats),
            'total_locations': len(locations),
            'threat_distribution': threat_counts,
            'following_threats': following_count,
            'average_threat_score': total_score / len(threats) if threats else 0,
        }
    
    def _serialize_threats(self, threats: Dict[str, ThreatScore]) -> List[Dict]:
        """Serialize threat data."""
        return [
            {
                'device_mac': threat.device_mac,
                'threat_level': threat.level,
                'score': threat.score,
                'confidence': threat.confidence,
                'is_following': threat.is_following,
                'detection_count': threat.detection_count,
                'dwell_time_seconds': threat.dwell_time,
                'location_count': threat.location_count,
                'average_rssi': threat.average_rssi if hasattr(threat, 'average_rssi') else None,
                'rssi_trend': threat.rssi_trend,
            }
            for threat in threats.values()
        ]
    
    def _serialize_locations(self, locations: List[Location]) -> List[Dict]:
        """Serialize location data."""
        return [location.to_dict() for location in locations]
    
    def _serialize_devices(self, devices: Dict[str, Device]) -> List[Dict]:
        """Serialize device data."""
        return [device.to_dict() for device in devices.values()] if devices else []
    
    def save_json(self, json_str: str, filepath: str) -> bool:
        """
        Save JSON to file.
        
        Args:
            json_str: JSON string
            filepath: Destination file path
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
            self.logger.info(f"JSON exported to: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving JSON: {e}")
            return False
    
    # ==================== CSV Export ====================
    
    def export_threats_to_csv(self, threats: Dict[str, ThreatScore]) -> str:
        """
        Export threats to CSV format.
        
        Args:
            threats: Threat scores dictionary
            
        Returns:
            CSV string
        """
        if not threats:
            return ""
        
        # Create in-memory CSV
        lines = []
        
        # Headers
        headers = [
            'Device MAC',
            'Threat Level',
            'Threat Score',
            'Confidence',
            'Detections',
            'Dwell Time (s)',
            'Locations',
            'Avg RSSI',
            'RSSI Trend',
            'Following'
        ]
        lines.append(','.join(headers))
        
        # Data rows
        for threat in sorted(threats.values(), key=lambda x: x.score, reverse=True):
            avg_rssi = threat.average_rssi if hasattr(threat, 'average_rssi') and threat.average_rssi else "N/A"
            row = [
                threat.device_mac,
                threat.level,
                f"{threat.score:.2f}",
                f"{threat.confidence:.2f}",
                str(threat.detection_count),
                f"{threat.dwell_time:.1f}",
                str(threat.location_count),
                str(avg_rssi),
                threat.rssi_trend or "N/A",
                "YES" if threat.is_following else "NO"
            ]
            lines.append(','.join('"' + str(cell) + '"' if ',' in str(cell) else str(cell) 
                                for cell in row))
        
        csv_str = '\n'.join(lines)
        self.logger.info("Threats exported to CSV format")
        return csv_str
    
    def export_locations_to_csv(self, locations: List[Location]) -> str:
        """
        Export locations to CSV format.
        
        Args:
            locations: List of locations
            
        Returns:
            CSV string
        """
        if not locations:
            return ""
        
        lines = []
        
        # Headers
        headers = [
            'Location ID',
            'Location Name',
            'Latitude',
            'Longitude',
            'Duration (s)',
            'Device Count',
            'Detection Count'
        ]
        lines.append(','.join(headers))
        
        # Data rows
        for loc in locations:
            row = [
                loc.id,
                loc.name or "Unknown",
                f"{loc.centroid.latitude:.6f}",
                f"{loc.centroid.longitude:.6f}",
                f"{loc.duration:.1f}",
                str(loc.device_count),
                str(len(loc.coordinates))
            ]
            lines.append(','.join('"' + str(cell) + '"' for cell in row))
        
        csv_str = '\n'.join(lines)
        self.logger.info("Locations exported to CSV format")
        return csv_str
    
    def export_devices_to_csv(self, devices: Dict[str, Device]) -> str:
        """
        Export devices to CSV format.
        
        Args:
            devices: Dictionary of devices
            
        Returns:
            CSV string
        """
        if not devices:
            return ""
        
        lines = []
        
        # Headers
        headers = [
            'MAC Address',
            'Device Type',
            'SSID',
            'Manufacturer',
            'First Seen',
            'Last Seen',
            'Detection Count',
            'Dwell Time (s)',
            'Avg RSSI',
            'Locations'
        ]
        lines.append(','.join(headers))
        
        # Data rows
        for device in devices.values():
            row = [
                device.mac,
                device.device_type.value,
                device.ssid or "N/A",
                device.manufacturer or "N/A",
                device.first_seen.isoformat(),
                device.last_seen.isoformat(),
                str(device.detection_count),
                f"{device.dwell_time:.1f}",
                f"{device.average_rssi:.1f}" if device.average_rssi else "N/A",
                str(len(device.location_ids))
            ]
            lines.append(','.join('"' + str(cell) + '"' for cell in row))
        
        csv_str = '\n'.join(lines)
        self.logger.info("Devices exported to CSV format")
        return csv_str
    
    def save_csv(self, csv_str: str, filepath: str) -> bool:
        """
        Save CSV to file.
        
        Args:
            csv_str: CSV string
            filepath: Destination file path
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                f.write(csv_str)
            self.logger.info(f"CSV exported to: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
            return False
    
    # ==================== Batch Export ====================
    
    def export_all_formats(self, threats: Dict[str, ThreatScore],
                          locations: List[Location],
                          devices: Optional[Dict[str, Device]] = None,
                          output_dir: str = "outputs/reports") -> Dict[str, bool]:
        """
        Export to all formats at once.
        
        Args:
            threats: Threat scores
            locations: Locations
            devices: Devices
            output_dir: Output directory
            
        Returns:
            Dictionary with success status for each format
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = {}
        
        # JSON export
        json_data = self.export_to_json(threats, locations, devices)
        json_file = f"{output_dir}/analysis_{timestamp}.json"
        results['json'] = self.save_json(json_data, json_file)
        
        # CSV exports
        threats_csv = self.export_threats_to_csv(threats)
        threats_file = f"{output_dir}/threats_{timestamp}.csv"
        results['threats_csv'] = self.save_csv(threats_csv, threats_file)
        
        locations_csv = self.export_locations_to_csv(locations)
        locations_file = f"{output_dir}/locations_{timestamp}.csv"
        results['locations_csv'] = self.save_csv(locations_csv, locations_file)
        
        if devices:
            devices_csv = self.export_devices_to_csv(devices)
            devices_file = f"{output_dir}/devices_{timestamp}.csv"
            results['devices_csv'] = self.save_csv(devices_csv, devices_file)
        
        self.logger.info(f"Exported all formats to {output_dir}")
        return results