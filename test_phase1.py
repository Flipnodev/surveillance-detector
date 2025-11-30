#!/usr/bin/env python3
"""
Phase 1 Testing Script

Tests all foundation components:
- Logging system
- File manager
- Data models (Device, Location, GPSCoordinate)
- Configuration loader
- Validators

Run this before proceeding to Phase 2 to ensure everything works.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

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


def test_logging():
    """Test logging system."""
    print_test("Logging System")
    
    try:
        from utils.logger import setup_logging, get_logger
        
        # Setup logging
        logger = setup_logging(log_dir='outputs/logs')
        print_success("Logging initialized successfully")
        
        # Test different log levels
        logger.debug("Debug message test")
        logger.info("Info message test")
        logger.warning("Warning message test")
        logger.error("Error message test")
        
        print_success("All log levels working")
        
        # Check log file created
        log_dir = Path('outputs/logs')
        log_files = list(log_dir.glob('*.log'))
        if log_files:
            print_success(f"Log file created: {log_files[0].name}")
        else:
            print_error("No log file created")
        
        return True
        
    except Exception as e:
        print_error(f"Logging test failed: {e}")
        return False


def test_file_manager():
    """Test file manager."""
    print_test("File Manager")
    
    try:
        from utils.file_manager import FileManager
        
        # Initialize file manager
        fm = FileManager()
        fm.initialize_directories()
        print_success("File manager initialized")
        
        # Check directories created
        for dir_type in ['kml', 'reports', 'logs', 'data']:
            path = fm.get_path(dir_type)
            if path.exists():
                print_success(f"Directory exists: {path}")
            else:
                print_error(f"Directory not created: {path}")
        
        # Test filename generation
        filename = fm.generate_filename('test', 'txt', timestamp=True)
        print_success(f"Generated filename: {filename}")
        
        # Test saving text file
        test_content = "This is a test file"
        saved_path = fm.save_text(test_content, 'data', 'test.txt')
        print_success(f"Saved text file: {saved_path}")
        
        # Test saving JSON
        test_data = {'test': 'data', 'number': 42}
        json_path = fm.save_json(test_data, 'data', 'test.json')
        print_success(f"Saved JSON file: {json_path}")
        
        # Test loading JSON
        loaded_data = fm.load_json('data', 'test.json')
        if loaded_data == test_data:
            print_success("JSON load/save verified")
        else:
            print_error("JSON data mismatch")
        
        # Test disk usage
        usage = fm.get_disk_usage()
        print_info(f"Disk usage: {usage}")
        
        return True
        
    except Exception as e:
        print_error(f"File manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_device_model():
    """Test Device data model."""
    print_test("Device Data Model")
    
    try:
        from data.device import Device, DeviceType
        
        # Create a device
        now = datetime.now()
        device = Device(
            mac='AA:BB:CC:DD:EE:FF',
            device_type=DeviceType.WIFI_CLIENT,
            first_seen=now,
            last_seen=now + timedelta(minutes=10),
            ssid='TestNetwork',
            manufacturer='Apple'
        )
        print_success(f"Created device: {device.mac}")
        
        # Test MAC normalization
        test_macs = ['aa-bb-cc-dd-ee-ff', 'aa.bb.cc.dd.ee.ff', 'AABBCCDDEEFF']
        for mac in test_macs:
            d = Device(mac=mac, device_type=DeviceType.WIFI_CLIENT, 
                      first_seen=now, last_seen=now)
            if d.mac == 'AA:BB:CC:DD:EE:FF':
                print_success(f"MAC normalized: {mac} → {d.mac}")
            else:
                print_error(f"MAC normalization failed: {mac} → {d.mac}")
        
        # Test device updates
        device.update_detection(now + timedelta(minutes=5), rssi=-60, location_id='loc1')
        device.update_detection(now + timedelta(minutes=8), rssi=-55, location_id='loc2')
        print_success(f"Device updated: {device.detection_count} detections")
        
        # Test RSSI calculations
        device.rssi_values = [-70, -65, -60, -55, -50]
        print_info(f"Average RSSI: {device.average_rssi}")
        print_info(f"RSSI trend: {device.rssi_trend}")
        print_success("RSSI calculations working")
        
        # Test dwell time
        print_info(f"Dwell time: {device.dwell_time} seconds")
        print_success("Dwell time calculation working")
        
        # Test serialization
        device_dict = device.to_dict()
        print_success("Device to_dict() working")
        
        restored = Device.from_dict(device_dict)
        if restored.mac == device.mac:
            print_success("Device from_dict() working")
        else:
            print_error("Device serialization failed")
        
        return True
        
    except Exception as e:
        print_error(f"Device model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_location_model():
    """Test Location data model."""
    print_test("Location Data Model")
    
    try:
        from data.location import Location, GPSCoordinate
        
        # Create GPS coordinates
        coord1 = GPSCoordinate(58.9700, 5.7331, timestamp=datetime.now())  # Stavanger
        coord2 = GPSCoordinate(58.9710, 5.7340, timestamp=datetime.now())
        print_success(f"Created coordinates: {coord1.to_tuple()}")
        
        # Test distance calculation
        distance = coord1.distance_to(coord2)
        print_info(f"Distance between points: {distance:.2f} meters")
        print_success("Distance calculation working")
        
        # Test coordinate validation
        try:
            invalid = GPSCoordinate(200, 500)  # Invalid
            print_error("Coordinate validation failed - accepted invalid coords")
        except ValueError:
            print_success("Coordinate validation working")
        
        # Create location
        location = Location(
            id='loc_test_001',
            centroid=coord1,
            name='Test Location'
        )
        print_success(f"Created location: {location.name}")
        
        # Add coordinates and devices
        location.add_coordinate(coord1)
        location.add_coordinate(coord2)
        location.add_device('AA:BB:CC:DD:EE:FF')
        location.add_device('11:22:33:44:55:66')
        
        print_info(f"Location has {len(location.coordinates)} coordinates")
        print_info(f"Location has {location.device_count} devices")
        print_success("Location updates working")
        
        # Test serialization
        loc_dict = location.to_dict()
        print_success("Location to_dict() working")
        
        restored = Location.from_dict(loc_dict)
        if restored.id == location.id:
            print_success("Location from_dict() working")
        else:
            print_error("Location serialization failed")
        
        return True
        
    except Exception as e:
        print_error(f"Location model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration system."""
    print_test("Configuration System")
    
    try:
        from config import load_config, get_config
        
        # Check if config file exists
        config_path = Path('config.yaml')
        if not config_path.exists():
            print_error(f"Config file not found: {config_path}")
            print_info("Copy config.yaml from the artifacts to project root")
            return False
        
        # Load configuration
        config = load_config('config.yaml')
        print_success("Configuration loaded successfully")
        
        # Test accessing config values
        app_name = config.app.name
        print_info(f"App name: {app_name}")
        
        min_detections = config.detection.min_detections
        print_info(f"Min detections: {min_detections}")
        
        time_windows = config.detection.time_windows
        print_info(f"Time windows: {time_windows}")
        
        print_success("Configuration access working")
        
        # Test get method with default
        custom_value = config.get('nonexistent.key', 'default_value')
        if custom_value == 'default_value':
            print_success("Config default values working")
        
        # Test getting current config
        config2 = get_config()
        if config2.app.name == app_name:
            print_success("get_config() working")
        
        return True
        
    except Exception as e:
        print_error(f"Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validators():
    """Test validation utilities."""
    print_test("Validators")
    
    try:
        from utils.validators import Validators, ValidationError
        
        # Test MAC address validation
        valid_macs = [
            'AA:BB:CC:DD:EE:FF',
            'aa-bb-cc-dd-ee-ff',
            'aa.bb.cc.dd.ee.ff',
            'AABBCCDDEEFF'
        ]
        
        for mac in valid_macs:
            if Validators.validate_mac_address(mac):
                normalized = Validators.normalize_mac_address(mac)
                print_success(f"MAC valid: {mac} → {normalized}")
            else:
                print_error(f"MAC validation failed: {mac}")
        
        # Test invalid MAC
        invalid_macs = ['invalid', '00:00:00:00:00', 'ZZ:ZZ:ZZ:ZZ:ZZ:ZZ']
        for mac in invalid_macs:
            if not Validators.validate_mac_address(mac):
                print_success(f"Correctly rejected invalid MAC: {mac}")
            else:
                print_error(f"Accepted invalid MAC: {mac}")
        
        # Test GPS validation
        if Validators.validate_gps_coordinate(58.9700, 5.7331):
            print_success("GPS validation working (valid coords)")
        
        if not Validators.validate_gps_coordinate(200, 500):
            print_success("GPS validation working (rejected invalid)")
        
        # Test RSSI validation
        if Validators.validate_rssi(-60):
            print_success("RSSI validation working (valid)")
        
        if not Validators.validate_rssi(50):
            print_success("RSSI validation working (rejected invalid)")
        
        # Test filename sanitization
        unsafe = 'test<file>name?.txt'
        safe = Validators.sanitize_filename(unsafe)
        print_success(f"Filename sanitized: {unsafe} → {safe}")
        
        # Test SSID validation
        if Validators.validate_ssid('MyNetwork'):
            print_success("SSID validation working")
        
        return True
        
    except Exception as e:
        print_error(f"Validators test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test integration between components."""
    print_test("Integration Test")
    
    try:
        from utils.logger import get_logger
        from utils.file_manager import FileManager
        from data.device import Device, DeviceType
        from data.location import Location, GPSCoordinate
        from datetime import datetime
        
        logger = get_logger()
        fm = FileManager()
        fm.initialize_directories() 
        
        # Create a scenario: device detected at location
        logger.info("Creating integration test scenario...")
        
        now = datetime.now()
        location = Location(
            id='loc_001',
            centroid=GPSCoordinate(58.9700, 5.7331, timestamp=now),
            name='Test Location'
        )
        
        device = Device(
            mac='AA:BB:CC:DD:EE:FF',
            device_type=DeviceType.WIFI_CLIENT,
            first_seen=now,
            last_seen=now + timedelta(minutes=10),
            ssid='TestNetwork'
        )
        
        # Add device to location
        location.add_device(device.mac)
        
        # Save data
        scenario_data = {
            'location': location.to_dict(),
            'device': device.to_dict(),
            'timestamp': now.isoformat()
        }
        
        fm.save_json(scenario_data, 'data', 'integration_test.json')
        logger.info("Saved integration test data")
        
        # Load and verify
        loaded = fm.load_json('data', 'integration_test.json')
        if loaded['device']['mac'] == device.mac:
            print_success("Integration test passed - data saved and loaded correctly")
            logger.info("Integration test completed successfully")
            return True
        else:
            print_error("Integration test failed - data mismatch")
            return False
        
    except Exception as e:
        print_error(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}SURVEILLANCE DETECTION SYSTEM - PHASE 1 TESTING{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results = {}
    
    # Run all tests
    results['Logging'] = test_logging()
    results['File Manager'] = test_file_manager()
    results['Device Model'] = test_device_model()
    results['Location Model'] = test_location_model()
    results['Configuration'] = test_configuration()
    results['Validators'] = test_validators()
    results['Integration'] = test_integration()
    
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
        print(f"{GREEN}Phase 1 is ready! You can proceed to Phase 2.{RESET}")
        return 0
    else:
        print(f"{RED}✗ SOME TESTS FAILED ({passed}/{total} passed){RESET}")
        print(f"{YELLOW}Please fix the issues before proceeding to Phase 2.{RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(main())