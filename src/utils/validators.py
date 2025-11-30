"""
Input validation utilities.

Provides validation functions for MAC addresses, GPS coordinates,
file paths, and other input data.
"""

import re
from typing import Optional, Tuple
from pathlib import Path


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class Validators:
    """Collection of validation methods for input data."""
    
    # MAC address patterns
    MAC_PATTERNS = [
        re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'),  # XX:XX:XX:XX:XX:XX
        re.compile(r'^([0-9A-Fa-f]{2}\.){5}([0-9A-Fa-f]{2})$'),    # XX.XX.XX.XX.XX.XX
        re.compile(r'^[0-9A-Fa-f]{12}$'),                          # XXXXXXXXXXXX
    ]
    
    @staticmethod
    def validate_mac_address(mac: str) -> bool:
        """
        Validate MAC address format.
        
        Args:
            mac: MAC address string
            
        Returns:
            True if valid, False otherwise
        """
        if not mac:
            return False
        
        return any(pattern.match(mac) for pattern in Validators.MAC_PATTERNS)
    
    @staticmethod
    def normalize_mac_address(mac: str) -> str:
        """
        Normalize MAC address to standard format (XX:XX:XX:XX:XX:XX).
        
        Args:
            mac: MAC address in any supported format
            
        Returns:
            Normalized MAC address
            
        Raises:
            ValidationError: If MAC address is invalid
        """
        if not Validators.validate_mac_address(mac):
            raise ValidationError(f"Invalid MAC address: {mac}")
        
        # Remove all separators and convert to uppercase
        clean_mac = mac.replace(':', '').replace('-', '').replace('.', '').upper()
        
        # Insert colons
        normalized = ':'.join(clean_mac[i:i+2] for i in range(0, 12, 2))
        
        return normalized
    
    @staticmethod
    def validate_gps_coordinate(latitude: float, longitude: float) -> bool:
        """
        Validate GPS coordinates.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return False
        
        return -90 <= latitude <= 90 and -180 <= longitude <= 180
    
    @staticmethod
    def validate_rssi(rssi: int) -> bool:
        """
        Validate RSSI signal strength value.
        
        Args:
            rssi: RSSI value in dBm
            
        Returns:
            True if valid (typically between -100 and 0), False otherwise
        """
        if not isinstance(rssi, int):
            return False
        
        # Typical WiFi RSSI range
        return -100 <= rssi <= 0
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = False) -> bool:
        """
        Validate file path.
        
        Args:
            path: File path string
            must_exist: If True, path must exist on filesystem
            
        Returns:
            True if valid, False otherwise
        """
        if not path:
            return False
        
        try:
            path_obj = Path(path)
            
            if must_exist:
                return path_obj.exists()
            
            # Check if path is valid (parent directory must be valid)
            return True
        except (ValueError, OSError):
            return False
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """
        Validate IPv4 address.
        
        Args:
            ip: IP address string
            
        Returns:
            True if valid, False otherwise
        """
        pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        
        if not pattern.match(ip):
            return False
        
        # Check each octet is 0-255
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
    
    @staticmethod
    def validate_port(port: int) -> bool:
        """
        Validate network port number.
        
        Args:
            port: Port number
            
        Returns:
            True if valid (1-65535), False otherwise
        """
        return isinstance(port, int) and 1 <= port <= 65535
    
    @staticmethod
    def validate_time_window(minutes: int) -> bool:
        """
        Validate time window value.
        
        Args:
            minutes: Time window in minutes
            
        Returns:
            True if valid (positive and reasonable), False otherwise
        """
        # Time windows should be between 1 minute and 24 hours
        return isinstance(minutes, int) and 1 <= minutes <= 1440
    
    @staticmethod
    def validate_threat_score(score: float) -> bool:
        """
        Validate threat score value.
        
        Args:
            score: Threat score (0-100)
            
        Returns:
            True if valid, False otherwise
        """
        return isinstance(score, (int, float)) and 0 <= score <= 100
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename safe for all filesystems
        """
        # Remove invalid characters
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(invalid_chars, '_', filename)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')
        
        # Ensure not empty
        if not sanitized:
            sanitized = 'unnamed'
        
        return sanitized
    
    @staticmethod
    def validate_ssid(ssid: str) -> bool:
        """
        Validate WiFi SSID.
        
        Args:
            ssid: SSID string
            
        Returns:
            True if valid (0-32 bytes), False otherwise
        """
        if not ssid:
            return False
        
        # SSID must be 0-32 bytes (UTF-8 encoded)
        return 0 < len(ssid.encode('utf-8')) <= 32
    
    @staticmethod
    def parse_mac_address(mac: str) -> Optional[str]:
        """
        Parse and normalize MAC address, returning None if invalid.
        
        Args:
            mac: MAC address string
            
        Returns:
            Normalized MAC address or None if invalid
        """
        try:
            return Validators.normalize_mac_address(mac)
        except ValidationError:
            return None
    
    @staticmethod
    def parse_gps_coordinate(lat: str, lon: str) -> Optional[Tuple[float, float]]:
        """
        Parse GPS coordinates from strings.
        
        Args:
            lat: Latitude string
            lon: Longitude string
            
        Returns:
            Tuple of (latitude, longitude) or None if invalid
        """
        try:
            latitude = float(lat)
            longitude = float(lon)
            
            if Validators.validate_gps_coordinate(latitude, longitude):
                return (latitude, longitude)
        except (ValueError, TypeError):
            pass
        
        return None