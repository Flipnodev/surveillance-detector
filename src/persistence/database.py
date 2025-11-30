"""
SQLite database backend for session persistence.

Stores device tracking, location history, and threat analysis
for historical data access and trend analysis.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from data.device import Device, DeviceType
from data.location import Location, GPSCoordinate


class DatabaseManager:
    """
    SQLite database manager for session persistence.
    
    Features:
    - Fast device lookups with indexed queries
    - Location and GPS history tracking
    - Threat score persistence
    - Automatic old data cleanup
    - Transaction support
    """
    
    def __init__(self, db_path: str = 'outputs/data/surveillance.db',
                 logger: logging.Logger = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
            logger: Logger instance
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        
        self.connection = None
        self._initialize_database()
        self.logger.info(f"Database initialized: {self.db_path}")
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            cursor = self.connection.cursor()
            
            # Devices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY,
                    mac TEXT UNIQUE NOT NULL,
                    device_type TEXT,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    ssid TEXT,
                    manufacturer TEXT,
                    avg_rssi REAL,
                    detection_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Locations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY,
                    location_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    latitude REAL,
                    longitude REAL,
                    duration_seconds REAL DEFAULT 0,
                    device_count INTEGER DEFAULT 0,
                    first_detection TIMESTAMP,
                    last_detection TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # GPS history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gps_history (
                    id INTEGER PRIMARY KEY,
                    device_mac TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    altitude REAL,
                    accuracy REAL,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (device_mac) REFERENCES devices(mac)
                )
            ''')
            
            # Threat scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_scores (
                    id INTEGER PRIMARY KEY,
                    device_mac TEXT NOT NULL,
                    threat_level TEXT,
                    score REAL,
                    is_following INTEGER DEFAULT 0,
                    confidence REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (device_mac) REFERENCES devices(mac)
                )
            ''')
            
            # RSSI history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rssi_history (
                    id INTEGER PRIMARY KEY,
                    device_mac TEXT NOT NULL,
                    rssi_dbm INTEGER,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (device_mac) REFERENCES devices(mac)
                )
            ''')
            
            # Create indexes for fast queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_devices_mac ON devices(mac)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_gps_device ON gps_history(device_mac)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat_device ON threat_scores(device_mac)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_rssi_device ON rssi_history(device_mac)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat_timestamp ON threat_scores(timestamp)')
            
            self.connection.commit()
            self.logger.debug("Database tables created/verified")
            
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def save_device(self, device: Device) -> bool:
        """
        Save or update device record.
        
        Args:
            device: Device object
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO devices 
                (mac, device_type, first_seen, last_seen, ssid, manufacturer, 
                 avg_rssi, detection_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device.mac,
                device.device_type.value,
                device.first_seen,
                device.last_seen,
                device.ssid,
                device.manufacturer,
                device.average_rssi or 0,
                device.detection_count
            ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error saving device: {e}")
            return False
    
    def get_device(self, mac: str) -> Optional[Dict]:
        """
        Get device record by MAC address.
        
        Args:
            mac: Device MAC address
            
        Returns:
            Device dict or None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM devices WHERE mac = ?', (mac,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        except sqlite3.Error as e:
            self.logger.error(f"Error getting device: {e}")
            return None
    
    def save_location(self, location: Location) -> bool:
        """
        Save or update location record.
        
        Args:
            location: Location object
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO locations 
                (location_id, name, latitude, longitude, duration_seconds, 
                 device_count, first_detection, last_detection)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location.id,
                location.name,
                location.centroid.latitude,
                location.centroid.longitude,
                location.duration,
                location.device_count,
                location.start_time,
                location.end_time
            ))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error saving location: {e}")
            return False
    
    def save_gps_point(self, device_mac: str, latitude: float, 
                       longitude: float, timestamp: datetime,
                       altitude: Optional[float] = None,
                       accuracy: Optional[float] = None) -> bool:
        """
        Save GPS coordinate history.
        
        Args:
            device_mac: Device MAC address
            latitude: Latitude
            longitude: Longitude
            timestamp: GPS timestamp
            altitude: Optional altitude
            accuracy: Optional accuracy
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO gps_history 
                (device_mac, latitude, longitude, altitude, accuracy, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (device_mac, latitude, longitude, altitude, accuracy, timestamp))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error saving GPS point: {e}")
            return False
    
    def save_threat_score(self, device_mac: str, threat_level: str,
                         score: float, is_following: bool = False,
                         confidence: float = 1.0) -> bool:
        """
        Save threat score record.
        
        Args:
            device_mac: Device MAC address
            threat_level: Threat level (low, medium, high, none)
            score: Threat score (0-100)
            is_following: Whether device is following
            confidence: Confidence score (0-1)
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO threat_scores 
                (device_mac, threat_level, score, is_following, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (device_mac, threat_level, score, int(is_following), confidence))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error saving threat score: {e}")
            return False
    
    def save_rssi_value(self, device_mac: str, rssi_dbm: int,
                       timestamp: datetime) -> bool:
        """
        Save RSSI history point.
        
        Args:
            device_mac: Device MAC address
            rssi_dbm: RSSI value in dBm
            timestamp: Measurement timestamp
            
        Returns:
            True if successful
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO rssi_history (device_mac, rssi_dbm, timestamp)
                VALUES (?, ?, ?)
            ''', (device_mac, rssi_dbm, timestamp))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error saving RSSI: {e}")
            return False
    
    def get_device_history(self, device_mac: str, 
                          hours: int = 24) -> Dict:
        """
        Get device history for specified time period.
        
        Args:
            device_mac: Device MAC address
            hours: Hours of history to retrieve
            
        Returns:
            Dictionary with device history
        """
        try:
            cursor = self.connection.cursor()
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Get device info
            cursor.execute('SELECT * FROM devices WHERE mac = ?', (device_mac,))
            device_row = cursor.fetchone()
            
            # Get threat scores
            cursor.execute('''
                SELECT * FROM threat_scores 
                WHERE device_mac = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (device_mac, cutoff_time))
            threats = cursor.fetchall()
            
            # Get GPS history
            cursor.execute('''
                SELECT * FROM gps_history 
                WHERE device_mac = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (device_mac, cutoff_time))
            gps_points = cursor.fetchall()
            
            # Get RSSI history
            cursor.execute('''
                SELECT * FROM rssi_history 
                WHERE device_mac = ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (device_mac, cutoff_time))
            rssi_points = cursor.fetchall()
            
            return {
                'device': device_row,
                'threats': threats,
                'gps_points': gps_points,
                'rssi_points': rssi_points,
                'time_period_hours': hours
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error getting device history: {e}")
            return {}
    
    def cleanup_old_data(self, retention_hours: int = 24) -> int:
        """
        Delete records older than retention period.
        
        Args:
            retention_hours: Hours to keep
            
        Returns:
            Number of records deleted
        """
        try:
            cursor = self.connection.cursor()
            cutoff_time = datetime.now() - timedelta(hours=retention_hours)
            
            # Delete old threat scores
            cursor.execute('DELETE FROM threat_scores WHERE timestamp < ?', 
                          (cutoff_time,))
            deleted = cursor.rowcount
            
            # Delete old GPS history
            cursor.execute('DELETE FROM gps_history WHERE timestamp < ?',
                          (cutoff_time,))
            deleted += cursor.rowcount
            
            # Delete old RSSI history
            cursor.execute('DELETE FROM rssi_history WHERE timestamp < ?',
                          (cutoff_time,))
            deleted += cursor.rowcount
            
            self.connection.commit()
            
            if deleted > 0:
                self.logger.info(f"Deleted {deleted} old records")
            
            return deleted
            
        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning up data: {e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with counts and stats
        """
        try:
            cursor = self.connection.cursor()
            
            # Count records
            cursor.execute('SELECT COUNT(*) FROM devices')
            device_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM locations')
            location_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM threat_scores')
            threat_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM gps_history')
            gps_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM rssi_history')
            rssi_count = cursor.fetchone()[0]
            
            return {
                'devices': device_count,
                'locations': location_count,
                'threats': threat_count,
                'gps_points': gps_count,
                'rssi_points': rssi_count,
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"DatabaseManager({self.db_path})"