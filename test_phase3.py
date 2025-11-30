#!/usr/bin/env python3
"""
Phase 3 Testing Script

Tests all Phase 3 components:
- Kismet client (REST API connection, device fetching)
- KML generation (map creation, threat visualization)
- WiGLE client (SSID lookup, caching, rate limiting)
- Integration with Phase 1 & 2 components

Run this to verify Phase 3 functionality before deployment.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import time

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


def test_kismet_client_imports():
    """Test KismetClient imports."""
    print_test("KismetClient Imports")
    
    try:
        from clients.kismet_client import KismetClient, KismetDevice
        print_success("KismetClient imported successfully")
        print_success("KismetDevice imported successfully")
        
        return True
        
    except Exception as e:
        print_error(f"KismetClient import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kismet_client_initialization():
    """Test KismetClient initialization."""
    print_test("KismetClient Initialization")
    
    try:
        from clients.kismet_client import KismetClient
        from utils.logger import get_logger
        
        logger = get_logger()
        
        # Initialize client
        kismet = KismetClient(
            host='localhost',
            port=2501,
            username='kismet',
            password='kismet',
            logger=logger
        )
        
        print_success("KismetClient initialized")
        print_info(f"Server URL: {kismet.base_url}")
        print_info(f"Connected: {kismet.is_connected}")
        
        # Test string representation
        repr_str = repr(kismet)
        print_success(f"String representation: {repr_str}")
        
        return True
        
    except Exception as e:
        print_error(f"KismetClient initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kismet_device_model():
    """Test KismetDevice data model."""
    print_test("KismetDevice Model")
    
    try:
        from clients.kismet_client import KismetDevice
        from datetime import datetime
        
        # Create test device
        device = KismetDevice(
            mac='AA:BB:CC:DD:EE:FF',
            device_type='WiFi',
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            signal_dbm=-65,
            latitude=58.9700,
            longitude=5.7331,
            ssid='TestNetwork',
            manuf='Apple'
        )
        
        print_success(f"Created KismetDevice: {device.mac}")
        
        # Test conversion to dict
        device_dict = device.to_dict()
        print_success("Device to_dict() working")
        
        # Verify dict contains all fields
        expected_keys = ['mac', 'device_type', 'first_seen', 'last_seen', 
                        'signal_dbm', 'latitude', 'longitude', 'ssid', 'manuf']
        
        for key in expected_keys:
            if key not in device_dict:
                print_error(f"Missing key in dict: {key}")
                return False
        
        print_success(f"All device fields present in dict")
        
        return True
        
    except Exception as e:
        print_error(f"KismetDevice model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kml_generator_imports():
    """Test KMLGenerator imports."""
    print_test("KMLGenerator Imports")
    
    try:
        from reporting.kml_generator import KMLGenerator
        print_success("KMLGenerator imported successfully")
        
        return True
        
    except Exception as e:
        print_error(f"KMLGenerator import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kml_generator_initialization():
    """Test KMLGenerator initialization."""
    print_test("KMLGenerator Initialization")
    
    try:
        from reporting.kml_generator import KMLGenerator
        from utils.logger import get_logger
        
        logger = get_logger()
        
        # Initialize generator
        kml_gen = KMLGenerator(logger=logger)
        print_success("KMLGenerator initialized")
        
        # Check color mapping
        colors = kml_gen.COLORS
        print_info(f"Color mappings defined: {len(colors)}")
        
        if 'high' not in colors or 'following' not in colors:
            print_error("Missing color definitions")
            return False
        
        print_success("All threat level colors defined")
        
        # Check icons
        icons = kml_gen.ICONS
        print_info(f"Icon URLs defined: {len(icons)}")
        print_success("KML styling configured")
        
        return True
        
    except Exception as e:
        print_error(f"KMLGenerator initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_kml_map_creation():
    """Test KML map creation with mock data."""
    print_test("KML Map Creation")
    
    try:
        from reporting.kml_generator import KMLGenerator
        from core.detector_engine import DetectorEngine, ThreatScore
        from data.location import Location, GPSCoordinate
        from config import load_config
        from utils.logger import get_logger
        
        logger = get_logger()
        config = load_config('config.yaml')
        
        # Create test locations
        locations = []
        for i in range(3):
            coord = GPSCoordinate(
                58.97 + (i * 0.001),
                5.73 + (i * 0.001),
                timestamp=datetime.now()
            )
            location = Location(
                id=f"loc_{i}",
                centroid=coord,
                name=f"Test Location {i}"
            )
            locations.append(location)
        
        print_success(f"Created {len(locations)} test locations")
        
        # Create test threat scores
        threat_scores = {}
        for i, loc in enumerate(locations):
            threat = ThreatScore(
                device_mac=f"AA:BB:CC:DD:EE:{i:02X}",
                score=20 + (i * 20),
                level=['low', 'medium', 'high'][i],
                detection_count=5 + i,
                dwell_time=300 + (i * 100),
                rssi_trend='stable',
                location_count=1,
                is_following=i == 2,
                confidence=0.8
            )
            threat_scores[f"AA:BB:CC:DD:EE:{i:02X}"] = threat
        
        print_success(f"Created {len(threat_scores)} threat scores")
        
        # Generate KML map
        kml_gen = KMLGenerator(logger=logger)
        kml = kml_gen.create_map(
            locations=locations,
            threat_scores=threat_scores,
            title="Test Surveillance Map"
        )
        
        if kml is None:
            print_error("KML generation failed")
            return False
        
        print_success("KML map created successfully")
        
        # Get KML string
        kml_string = kml_gen.get_kml_string()
        if not kml_string or len(kml_string) == 0:
            print_error("KML string is empty")
            return False
        
        print_success(f"KML string generated ({len(kml_string)} bytes)")
        
        # Test saving to file
        test_file = Path('outputs/kml/test_map.kml')
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        if kml_gen.save(str(test_file)):
            if test_file.exists():
                file_size = test_file.stat().st_size
                print_success(f"KML saved to file ({file_size} bytes)")
            else:
                print_error("KML file not created")
                return False
        else:
            print_error("Failed to save KML")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"KML map creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wigle_client_imports():
    """Test WiGLEClient imports."""
    print_test("WiGLEClient Imports")
    
    try:
        from clients.wigle_client import WiGLEClient, SSIDLocation
        print_success("WiGLEClient imported successfully")
        print_success("SSIDLocation imported successfully")
        
        return True
        
    except Exception as e:
        print_error(f"WiGLEClient import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wigle_client_initialization():
    """Test WiGLEClient initialization."""
    print_test("WiGLEClient Initialization")
    
    try:
        from clients.wigle_client import WiGLEClient
        from utils.logger import get_logger
        
        logger = get_logger()
        
        # Test with dummy API key
        wigle = WiGLEClient(
            api_key='test_api_key',
            logger=logger,
            rate_limit=10
        )
        
        print_success("WiGLEClient initialized")
        print_info(f"Enabled: {wigle.is_enabled}")
        print_info(f"Rate limit: {wigle.rate_limit} req/min")
        
        # Test with disabled API key
        wigle_disabled = WiGLEClient(
            api_key='YOUR_WIGLE_API_KEY_HERE',
            logger=logger
        )
        
        if not wigle_disabled.is_enabled:
            print_success("WiGLEClient correctly disabled without API key")
        else:
            print_error("WiGLEClient should be disabled with placeholder key")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"WiGLEClient initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ssid_location_model():
    """Test SSIDLocation data model."""
    print_test("SSIDLocation Model")
    
    try:
        from clients.wigle_client import SSIDLocation
        
        # Create test location
        location = SSIDLocation(
            ssid='StarbucksWiFi',
            latitude=58.9700,
            longitude=5.7331,
            accuracy=100,
            found_count=5,
            organization='Starbucks'
        )
        
        print_success(f"Created SSIDLocation: {location.ssid}")
        
        # Test conversion to dict
        loc_dict = location.to_dict()
        print_success("SSIDLocation to_dict() working")
        
        # Verify all fields
        if 'ssid' not in loc_dict or 'latitude' not in loc_dict:
            print_error("Missing fields in SSIDLocation dict")
            return False
        
        print_success("All fields present in dict")
        
        return True
        
    except Exception as e:
        print_error(f"SSIDLocation model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wigle_caching():
    """Test WiGLE client caching."""
    print_test("WiGLE Caching System")
    
    try:
        from clients.wigle_client import WiGLEClient, SSIDLocation
        from utils.logger import get_logger
        
        logger = get_logger()
        wigle = WiGLEClient(api_key='test_key', logger=logger)
        
        # Create test location
        location = SSIDLocation(
            ssid='TestSSID',
            latitude=58.97,
            longitude=5.73,
            found_count=10
        )
        
        # Manually add to cache
        wigle.cache['TestSSID'] = location
        from datetime import datetime
        wigle.cache_time['TestSSID'] = datetime.now()
        
        print_success("Cache populated with test data")
        
        # Check cache validity
        if wigle._is_cache_valid('TestSSID'):
            print_success("Cache validity check working")
        else:
            print_error("Cache validity check failed")
            return False
        
        # Test cache stats
        stats = wigle.get_cache_stats()
        print_info(f"Cache stats: {stats}")
        
        if stats['cached_ssids'] != 1:
            print_error("Cache size incorrect")
            return False
        
        print_success("Cache system working correctly")
        
        # Test cache clearing
        wigle.clear_cache()
        if len(wigle.cache) == 0:
            print_success("Cache cleared successfully")
        else:
            print_error("Cache clearing failed")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"WiGLE caching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_phase3_integration():
    """Test Phase 3 integration with Phase 1/2."""
    print_test("Phase 1/2/3 Integration")
    
    try:
        from clients.kismet_client import KismetClient
        from reporting.kml_generator import KMLGenerator
        from clients.wigle_client import WiGLEClient
        from core.detector_engine import DetectorEngine
        from config import load_config
        from utils.logger import get_logger
        
        logger = get_logger()
        config = load_config('config.yaml')
        
        # Initialize Phase 3 components
        kismet = KismetClient(logger=logger)
        print_success("KismetClient created")
        
        kml_gen = KMLGenerator(logger=logger)
        print_success("KMLGenerator created")
        
        wigle = WiGLEClient(api_key='test_key', logger=logger)
        print_success("WiGLEClient created")
        
        # Initialize Phase 2 component
        detector = DetectorEngine(config, logger)
        print_success("DetectorEngine created")
        
        # Simulate data flow
        detector.start()
        print_success("Detector engine started")
        
        # Process mock detection
        from datetime import datetime
        detector.process_detection(
            mac="AA:BB:CC:DD:EE:FF",
            ssid="TestSSID",
            rssi=-65,
            latitude=58.97,
            longitude=5.73,
            timestamp=datetime.now()
        )
        
        # Calculate threats
        detector.calculate_threat_scores()
        print_success("Threat scores calculated")
        
        # Generate KML
        if len(detector.locations) > 0:
            kml = kml_gen.create_map(
                locations=detector.locations.values(),
                threat_scores=detector.threat_scores
            )
            print_success("KML map generated from detector data")
        
        detector.stop()
        print_success("Phase 3 integration working correctly")
        
        return True
        
    except Exception as e:
        print_error(f"Phase 3 integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}SURVEILLANCE DETECTION SYSTEM - PHASE 3 TESTING{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results = {}
    
    # Run all tests
    results['KismetClient Imports'] = test_kismet_client_imports()
    results['KismetClient Initialization'] = test_kismet_client_initialization()
    results['KismetDevice Model'] = test_kismet_device_model()
    results['KMLGenerator Imports'] = test_kml_generator_imports()
    results['KMLGenerator Initialization'] = test_kml_generator_initialization()
    results['KML Map Creation'] = test_kml_map_creation()
    results['WiGLEClient Imports'] = test_wigle_client_imports()
    results['WiGLEClient Initialization'] = test_wigle_client_initialization()
    results['SSIDLocation Model'] = test_ssid_location_model()
    results['WiGLE Caching'] = test_wigle_caching()
    results['Phase 1/2/3 Integration'] = test_phase3_integration()
    
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
        print(f"{GREEN}Phase 3 foundation is ready for deployment!{RESET}")
        return 0
    else:
        print(f"{RED}✗ SOME TESTS FAILED ({passed}/{total} passed){RESET}")
        print(f"{YELLOW}Please fix the issues before proceeding.{RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(main())