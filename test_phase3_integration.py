#!/usr/bin/env python3
"""
Phase 3 Integration Testing Script

Tests all Phase 3 components working together:
- Kismet integration
- KML map generation
- WiGLE API integration
- Database persistence
- Caching system
- HTML report generation
- Data export (JSON/CSV)
- Full end-to-end workflows

Run this after Phase 1 & 2 tests pass to verify Phase 3 functionality.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import os

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(name: str):
    """Print test name."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Testing: {name}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")


def print_success(message: str):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message: str):
    """Print info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


def test_kismet_integration():
    """Test Kismet client integration."""
    print_test("Kismet Integration")
    
    try:
        from clients.kismet_client import KismetClient, KismetDevice
        from utils.logger import get_logger
        
        logger = get_logger()
        kismet = KismetClient(host='localhost', port=2501, logger=logger)
        
        print_success("KismetClient instantiated")
        
        # Test initialization
        assert kismet.host == 'localhost'
        assert kismet.port == 2501
        assert kismet.base_url == 'http://localhost:2501'
        print_success("Configuration parameters correct")
        
        # Test device caching
        assert len(kismet.device_cache) == 0
        print_success("Device cache initialized")
        
        # Test that we can call methods (won't connect without real server)
        status = kismet.get_status()
        print_info(f"Kismet status check: {status.get('connected', False)}")
        print_success("Kismet client methods working")
        
        # Test KismetDevice model
        device = KismetDevice(
            mac='AA:BB:CC:DD:EE:FF',
            device_type='WiFi',
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            signal_dbm=-65,
            ssid='TestNetwork'
        )
        
        device_dict = device.to_dict()
        assert device_dict['mac'] == 'AA:BB:CC:DD:EE:FF'
        assert device_dict['device_type'] == 'WiFi'
        assert device_dict['signal_dbm'] == -65
        print_success("KismetDevice model working")
        
        return True
        
    except Exception as e:
        print_error(f"Kismet integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_persistence():
    """Test database persistence functionality."""
    print_test("Database Persistence")
    
    try:
        from persistence.database import DatabaseManager
        from data.device import Device, DeviceType
        from utils.logger import get_logger
        
        logger = get_logger()
        
        # Use test database
        test_db = 'outputs/data/test_surveillance.db'
        db = DatabaseManager(db_path=test_db, logger=logger)
        
        print_success("Database initialized")
        
        # Create test device
        now = datetime.now()
        device = Device(
            mac='AA:BB:CC:DD:EE:01',
            device_type=DeviceType.WIFI_CLIENT,
            first_seen=now,
            last_seen=now + timedelta(minutes=5),
            ssid='TestNetwork',
            manufacturer='Apple'
        )
        
        # Save device
        result = db.save_device(device)
        assert result == True
        print_success("Device saved to database")
        
        # Retrieve device
        retrieved = db.get_device('AA:BB:CC:DD:EE:01')
        assert retrieved is not None
        assert retrieved['mac'] == 'AA:BB:CC:DD:EE:01'
        print_success("Device retrieved from database")
        
        # Save GPS point
        result = db.save_gps_point(
            device_mac='AA:BB:CC:DD:EE:01',
            latitude=58.97,
            longitude=5.73,
            timestamp=now
        )
        assert result == True
        print_success("GPS point saved")
        
        # Save threat score
        result = db.save_threat_score(
            device_mac='AA:BB:CC:DD:EE:01',
            threat_level='high',
            score=85.5,
            is_following=True,
            confidence=0.95
        )
        assert result == True
        print_success("Threat score saved")
        
        # Save RSSI
        result = db.save_rssi_value(
            device_mac='AA:BB:CC:DD:EE:01',
            rssi_dbm=-65,
            timestamp=now
        )
        assert result == True
        print_success("RSSI value saved")
        
        # Get statistics
        stats = db.get_statistics()
        assert stats['devices'] >= 1
        assert stats['threats'] >= 1
        assert stats['gps_points'] >= 1
        print_info(f"Database stats: {stats}")
        print_success("Database statistics working")
        
        db.close()
        return True
        
    except Exception as e:
        print_error(f"Database persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_caching_system():
    """Test caching and cache manager."""
    print_test("Caching System")
    
    try:
        from analysis.cache import LRUCache, CacheManager
        from utils.logger import get_logger
        
        logger = get_logger()
        
        # Test LRUCache
        cache = LRUCache(max_size=100, default_ttl=3600, logger=logger)
        
        # Store values
        cache.put('device_001', {'mac': 'AA:BB:CC:DD:EE:01', 'threat': 85})
        cache.put('device_002', {'mac': 'AA:BB:CC:DD:EE:02', 'threat': 45})
        
        print_success("Values stored in cache")
        
        # Retrieve values
        value1 = cache.get('device_001')
        assert value1 is not None
        assert value1['threat'] == 85
        print_success("Cache retrieval working")
        
        # Check hit rate
        stats = cache.get_statistics()
        assert stats['hits'] > 0
        print_info(f"Cache stats: {stats}")
        print_success("Cache statistics working")
        
        # Test CacheManager
        cache_mgr = CacheManager(logger=logger)
        
        # Store in different caches
        cache_mgr.device_cache.put('test_device', {'type': 'WiFi'})
        cache_mgr.ssid_cache.put('test_ssid', {'location': (58.97, 5.73)})
        cache_mgr.threat_cache.put('test_threat', {'level': 'high'})
        cache_mgr.gps_cache.put('test_gps', {'lat': 58.97, 'lon': 5.73})
        
        print_success("Cache manager populated")
        
        # Get summary
        summary = cache_mgr.get_summary()
        print_info(f"Cache manager summary:\n{summary}")
        print_success("Cache manager working")
        
        return True
        
    except Exception as e:
        print_error(f"Caching system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_html_reporting():
    """Test HTML report generation."""
    print_test("HTML Report Generation")
    
    try:
        from reporting.html_report import HTMLReporter
        from core.detector_engine import ThreatScore
        from data.location import Location, GPSCoordinate
        from utils.logger import get_logger
        
        logger = get_logger()
        reporter = HTMLReporter(logger=logger)
        
        print_success("HTMLReporter initialized")
        
        # Create test data
        threats = {
            'AA:BB:CC:DD:EE:01': ThreatScore(
                device_mac='AA:BB:CC:DD:EE:01',
                level='high',
                score=85.5,
                detection_count=10,
                dwell_time=300.0,
                location_count=2,
                is_following=True,
                confidence=0.95,
                rssi_trend='increasing'
            ),
            'AA:BB:CC:DD:EE:02': ThreatScore(
                device_mac='AA:BB:CC:DD:EE:02',
                level='low',
                score=25.0,
                detection_count=3,
                dwell_time=60.0,
                location_count=1,
                is_following=False,
                confidence=0.80,
                rssi_trend='stable'
            )
        }
        
        locations = [
            Location(
                id='loc_001',
                centroid=GPSCoordinate(58.97, 5.73),
                name='Location 1'
            ),
            Location(
                id='loc_002',
                centroid=GPSCoordinate(58.98, 5.74),
                name='Location 2'
            )
        ]
        
        # Generate report
        html = reporter.create_report(
            threats=threats,
            locations=locations,
            title="Phase 3 Integration Test Report"
        )
        
        assert html is not None
        assert len(html) > 1000
        assert 'html' in html.lower()
        assert 'Surveillance Detection Report' in html
        print_success("HTML report generated successfully")
        
        # Check content
        assert '85.5' in html  # Threat score
        assert 'high' in html.lower()  # Threat level
        assert '2' in html  # Number of locations
        print_success("Report contains expected content")
        
        # Save report
        report_file = 'outputs/reports/test_report.html'
        result = reporter.save(html, report_file)
        assert result == True
        assert os.path.exists(report_file)
        print_success(f"Report saved to {report_file}")
        
        return True
        
    except Exception as e:
        print_error(f"HTML reporting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_export():
    """Test JSON and CSV export functionality."""
    print_test("Data Export (JSON & CSV)")
    
    try:
        from reporting.json_exporter import DataExporter
        from core.detector_engine import ThreatScore
        from data.location import Location, GPSCoordinate
        from utils.logger import get_logger
        
        logger = get_logger()
        exporter = DataExporter(logger=logger)
        
        print_success("DataExporter initialized")
        
        # Create test data
        threats = {
            'AA:BB:CC:DD:EE:01': ThreatScore(
                device_mac='AA:BB:CC:DD:EE:01',
                level='high',
                score=85.5,
                detection_count=10,
                dwell_time=300.0,
                location_count=2,
                is_following=True,
                confidence=0.95,
                rssi_trend='increasing'
            )
        }
        
        locations = [
            Location(
                id='loc_001',
                centroid=GPSCoordinate(58.97, 5.73),
                name='Test Location'
            )
        ]
        
        # Test JSON export
        json_str = exporter.export_to_json(threats, locations)
        assert json_str is not None
        assert len(json_str) > 100
        
        # Parse to verify it's valid JSON
        json_data = json.loads(json_str)
        assert 'metadata' in json_data
        assert 'summary' in json_data
        assert 'threats' in json_data
        assert 'locations' in json_data
        print_success("JSON export working")
        
        # Save JSON
        json_file = 'outputs/reports/test_export.json'
        result = exporter.save_json(json_str, json_file)
        assert result == True
        assert os.path.exists(json_file)
        print_success(f"JSON saved to {json_file}")
        
        # Test CSV exports
        threats_csv = exporter.export_threats_to_csv(threats)
        assert threats_csv is not None
        assert 'Device MAC' in threats_csv
        assert 'AA:BB:CC:DD:EE:01' in threats_csv
        print_success("Threats CSV export working")
        
        locations_csv = exporter.export_locations_to_csv(locations)
        assert locations_csv is not None
        assert 'Location ID' in locations_csv
        assert 'loc_001' in locations_csv
        print_success("Locations CSV export working")
        
        # Save CSV files
        csv_threats_file = 'outputs/reports/test_threats.csv'
        csv_locations_file = 'outputs/reports/test_locations.csv'
        
        exporter.save_csv(threats_csv, csv_threats_file)
        exporter.save_csv(locations_csv, csv_locations_file)
        
        assert os.path.exists(csv_threats_file)
        assert os.path.exists(csv_locations_file)
        print_success("CSV files saved")
        
        return True
        
    except Exception as e:
        print_error(f"Data export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kml_generation():
    """Test KML map generation."""
    print_test("KML Map Generation")
    
    try:
        from reporting.kml_generator import KMLGenerator
        from core.detector_engine import ThreatScore
        from data.location import Location, GPSCoordinate
        from utils.logger import get_logger
        
        logger = get_logger()
        kml_gen = KMLGenerator(logger=logger)
        
        print_success("KMLGenerator initialized")
        
        # Create test data
        threats = {
            'AA:BB:CC:DD:EE:01': ThreatScore(
                device_mac='AA:BB:CC:DD:EE:01',
                level='high',
                score=85.5,
                detection_count=10,
                dwell_time=300.0,
                location_count=2,
                is_following=True,
                confidence=0.95,
                rssi_trend='increasing'
            )
        }
        
        locations = [
            Location(
                id='loc_001',
                centroid=GPSCoordinate(58.97, 5.73),
                name='Test Location'
            ),
            Location(
                id='loc_002',
                centroid=GPSCoordinate(58.98, 5.74),
                name='Test Location 2'
            )
        ]
        
        # Add coordinates to locations
        locations[0].add_coordinate(GPSCoordinate(58.97, 5.73, timestamp=datetime.now()))
        locations[0].add_coordinate(GPSCoordinate(58.9705, 5.7305, timestamp=datetime.now()))
        
        # Create KML
        kml = kml_gen.create_map(locations, threats)
        assert kml is not None
        print_success("KML map created")
        
        # Save KML
        kml_file = 'outputs/kml/test_map.kml'
        result = kml_gen.save(kml_file)
        assert result == True
        assert os.path.exists(kml_file)
        
        # Verify file has content
        with open(kml_file, 'r') as f:
            content = f.read()
            assert len(content) > 100
            assert 'kml' in content.lower()
        
        print_success(f"KML map saved to {kml_file}")
        
        return True
        
    except Exception as e:
        print_error(f"KML generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wigle_integration():
    """Test WiGLE client integration."""
    print_test("WiGLE Integration")
    
    try:
        from clients.wigle_client import WiGLEClient, SSIDLocation
        from utils.logger import get_logger
        
        logger = get_logger()
        
        # Test with placeholder API key (should be disabled)
        wigle = WiGLEClient(api_key="YOUR_WIGLE_API_KEY_HERE", logger=logger)
        assert wigle.is_enabled == False
        print_success("WiGLE correctly disabled with placeholder key")
        
        # Test with fake API key (would be enabled, but won't actually call API)
        wigle = WiGLEClient(api_key="test_api_key_12345", logger=logger)
        assert wigle.is_enabled == True
        print_success("WiGLE enabled with API key")
        
        # Test SSIDLocation model
        location = SSIDLocation(
            ssid='StarbucksWiFi',
            latitude=58.97,
            longitude=5.73,
            found_count=150,
            organization='Starbucks'
        )
        
        location_dict = location.to_dict()
        assert location_dict['ssid'] == 'StarbucksWiFi'
        assert location_dict['organization'] == 'Starbucks'
        print_success("SSIDLocation model working")
        
        # Test cache functionality
        cache_stats = wigle.get_cache_stats()
        assert 'cached_ssids' in cache_stats
        assert cache_stats['enabled'] == True
        print_info(f"WiGLE cache stats: {cache_stats}")
        print_success("WiGLE caching working")
        
        return True
        
    except Exception as e:
        print_error(f"WiGLE integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow():
    """Test complete workflow: detector -> reports -> exports."""
    print_test("Full Workflow Integration")
    
    try:
        from core.detector_engine import DetectorEngine
        from clients.mock_client import MockClient
        from reporting.html_report import HTMLReporter
        from reporting.json_exporter import DataExporter
        from reporting.kml_generator import KMLGenerator
        from config import load_config
        from utils.logger import get_logger
        
        logger = get_logger()
        config = load_config('config.yaml')
        
        # Initialize detector
        detector = DetectorEngine(config, logger)
        detector.start()
        print_success("DetectorEngine started")
        
        # Generate mock detections
        mock_client = MockClient(logger=logger)
        detections = mock_client.generate_scenario('normal')
        print_info(f"Generated {len(detections)} mock detections")
        
        # Process detections
        for detection in detections[:10]:  # Process first 10
            detector.process_detection(
                mac=detection.mac,
                ssid=detection.ssid,
                rssi=detection.rssi,
                latitude=detection.latitude,
                longitude=detection.longitude,
                timestamp=detection.timestamp
            )
        
        print_success("Detections processed")
        
        # Calculate threats
        detector.calculate_threat_scores()
        print_info(f"Calculated threats for {len(detector.threat_scores)} devices")
        print_success("Threat scoring completed")
        
        # Generate HTML report
        html_reporter = HTMLReporter(logger=logger)
        html = html_reporter.create_report(
            threats=detector.threat_scores,
            locations=list(detector.locations.values()),
            session_info=detector.get_statistics()
        )
        html_reporter.save(html, 'outputs/reports/workflow_test.html')
        print_success("HTML report generated")
        
        # Export data
        exporter = DataExporter(logger=logger)
        results = exporter.export_all_formats(
            threats=detector.threat_scores,
            locations=list(detector.locations.values()),
            devices=detector.devices
        )
        
        if all(results.values()):
            print_success("All data exports successful")
        
        # Generate KML
        kml_gen = KMLGenerator(logger=logger)
        kml = kml_gen.create_map(
            locations=list(detector.locations.values()),
            threat_scores=detector.threat_scores
        )
        kml_gen.save('outputs/kml/workflow_test.kml')
        print_success("KML map generated")
        
        detector.stop()
        print_success("Full workflow completed successfully")
        
        return True
        
    except Exception as e:
        print_error(f"Full workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}SURVEILLANCE DETECTION SYSTEM - PHASE 3 INTEGRATION TESTS{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results = {}
    
    # Run all tests
    results['Kismet Integration'] = test_kismet_integration()
    results['Database Persistence'] = test_database_persistence()
    results['Caching System'] = test_caching_system()
    results['HTML Reporting'] = test_html_reporting()
    results['Data Export'] = test_data_export()
    results['KML Generation'] = test_kml_generation()
    results['WiGLE Integration'] = test_wigle_integration()
    results['Full Workflow'] = test_full_workflow()
    
    # Print summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    if passed == total:
        print(f"{GREEN}✓ ALL TESTS PASSED ({passed}/{total}){RESET}")
        print(f"{GREEN}Phase 3 foundation is production-ready!{RESET}")
        print(f"{GREEN}Ready for v3.0.0 release and deployment!{RESET}")
        return 0
    else:
        print(f"{RED}✗ SOME TESTS FAILED ({passed}/{total} passed){RESET}")
        print(f"{YELLOW}Please fix the issues before release.{RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(main())