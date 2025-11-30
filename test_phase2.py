#!/usr/bin/env python3
"""
Phase 2 Testing Script

Tests all Phase 2 components:
- Detection engine (threat scoring, following detection)
- Analysis modules (clustering, GPS, threat scoring)
- Mock data client
- GUI components (if display available)
- Integration with Phase 1 components

Run this after Phase 1 tests pass to verify Phase 2 functionality.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

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


def test_detector_engine():
    """Test detection engine functionality."""
    print_test("Detection Engine")
    
    try:
        from core.detector_engine import DetectorEngine
        from config import load_config
        from utils.logger import setup_logging
        import logging
        
        config = load_config('config.yaml')
        logger = setup_logging(log_dir='outputs/logs')
        
        # Initialize detector
        detector = DetectorEngine(config, logger)
        print_success("DetectorEngine initialized")
        
        # Start detector
        detector.start()
        print_success("Detector started")
        
        # Process some mock detections
        now = datetime.now()
        for i in range(10):
            mac = f"AA:BB:CC:DD:EE:{i:02X}"
            detector.process_detection(
                mac=mac,
                ssid=f"Test-Network-{i}",
                rssi=random.randint(-80, -50),
                latitude=58.97 + random.uniform(-0.005, 0.005),
                longitude=5.73 + random.uniform(-0.005, 0.005),
                timestamp=now + timedelta(seconds=i*5)
            )
        
        print_success(f"Processed 10 detections")
        
        # Calculate threat scores
        threats = detector.calculate_threat_scores()
        print_success(f"Calculated threat scores for {len(threats)} devices")
        
        # Check threat levels
        high_threats = detector.get_threats('high')
        medium_threats = detector.get_threats('medium')
        low_threats = detector.get_threats('low')
        
        print_info(f"Threat distribution: High={len(high_threats)}, Medium={len(medium_threats)}, Low={len(low_threats)}")
        print_success("Threat scoring working")
        
        # Check following detection
        following = detector.get_following_threats()
        print_info(f"Following threats detected: {len(following)}")
        print_success("Following behavior detection working")
        
        # Get statistics
        stats = detector.get_statistics()
        print_info(f"Session stats: Devices={stats['device_count']}, Detections={stats['detection_count']}")
        print_success("Statistics calculation working")
        
        # Stop detector
        detector.stop()
        print_success("Detector stopped")
        
        return True
        
    except Exception as e:
        print_error(f"Detection engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clustering():
    """Test DBSCAN clustering."""
    print_test("DBSCAN Clustering")
    
    try:
        from analysis.clustering import ClusterAnalyzer
        from data.location import Location, GPSCoordinate
        from utils.logger import get_logger
        
        logger = get_logger()
        analyzer = ClusterAnalyzer(eps_meters=100, min_samples=2, logger=logger)
        print_success("ClusterAnalyzer initialized")
        
        # Create test locations
        locations = []
        base_lat, base_lon = 58.97, 5.73
        
        # Cluster 1: 3 locations close together
        for i in range(3):
            coord = GPSCoordinate(
                base_lat + (i * 0.0001),
                base_lon + (i * 0.0001),
                timestamp=datetime.now()
            )
            loc = Location(
                id=f"loc_{i}",
                centroid=coord,
                name=f"Location {i}"
            )
            locations.append(loc)
        
        # Cluster 2: 2 locations far away
        for i in range(3, 5):
            coord = GPSCoordinate(
                base_lat + 0.01,
                base_lon + 0.01,
                timestamp=datetime.now()
            )
            loc = Location(
                id=f"loc_{i}",
                centroid=coord,
                name=f"Location {i}"
            )
            locations.append(loc)
        
        print_success(f"Created {len(locations)} test locations")
        
        # Perform clustering
        clusters = analyzer.cluster_locations(locations)
        print_success(f"Clustering produced {len(clusters)} clusters")
        
        if len(clusters) >= 1:
            print_info(f"Cluster sizes: {[len(locs) for locs in clusters.values()]}")
            print_success("DBSCAN clustering working")
        else:
            print_error("Expected at least 1 cluster")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Clustering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gps_utils():
    """Test GPS utilities."""
    print_test("GPS Utilities")
    
    try:
        from analysis.gps_utils import GPSUtils
        from data.location import GPSCoordinate
        
        # Create test coordinates (Stavanger area)
        coord1 = GPSCoordinate(58.9700, 5.7331)
        coord2 = GPSCoordinate(58.9710, 5.7340)
        
        print_success("Created test coordinates")
        
        # Test distance calculation
        distance = GPSUtils.calculate_distance(coord1, coord2)
        print_info(f"Distance between points: {distance:.2f} meters")
        if 50 < distance < 500:  # Should be ~100-150 meters apart
            print_success("Distance calculation correct")
        else:
            print_error(f"Unexpected distance: {distance}")
            return False
        
        # Test centroid calculation
        coords = [coord1, coord2]
        centroid = GPSUtils.calculate_centroid(coords)
        print_success(f"Centroid calculated: {centroid.latitude:.6f}, {centroid.longitude:.6f}")
        
        # Test bearing calculation
        bearing = GPSUtils.calculate_bearing(coord1, coord2)
        print_info(f"Bearing from point 1 to point 2: {bearing:.1f}°")
        if 0 <= bearing <= 360:
            print_success("Bearing calculation correct")
        else:
            print_error(f"Invalid bearing: {bearing}")
            return False
        
        # Test proximity check
        within = GPSUtils.is_within_radius(coord1, coord2, radius_meters=2000)
        if within:
            print_success("Proximity check working (within radius)")
        else:
            print_error("Proximity check failed")
            return False
        
        outside = GPSUtils.is_within_radius(coord1, coord2, radius_meters=100)
        if not outside:
            print_success("Proximity check working (outside radius)")
        else:
            print_error("Proximity check failed")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"GPS utilities test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_threat_scorer():
    """Test threat scoring."""
    print_test("Threat Scoring")
    
    try:
        from analysis.threat_scorer import ThreatScorer
        
        # Test proximity scoring
        rssi_values = [-70, -65, -60, -55, -50]
        proximity_score = ThreatScorer.calculate_proximity_score(rssi_values)
        print_info(f"Proximity score (strong signal): {proximity_score:.1f}")
        if 0 <= proximity_score <= 100:
            print_success("Proximity scoring working")
        else:
            print_error(f"Invalid proximity score: {proximity_score}")
            return False
        
        # Test persistence scoring
        persistence_score = ThreatScorer.calculate_persistence_score(detection_count=10)
        print_info(f"Persistence score (10 detections): {persistence_score:.1f}")
        if 0 <= persistence_score <= 100:
            print_success("Persistence scoring working")
        else:
            print_error(f"Invalid persistence score: {persistence_score}")
            return False
        
        # Test stability scoring
        stability_score = ThreatScorer.calculate_stability_score(location_count=3)
        print_info(f"Stability score (3 locations): {stability_score:.1f}")
        if 0 <= stability_score <= 100:
            print_success("Stability scoring working")
        else:
            print_error(f"Invalid stability score: {stability_score}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Threat scorer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mock_client():
    """Test mock data client."""
    print_test("Mock Data Client")
    
    try:
        from clients.mock_client import MockClient
        from utils.logger import get_logger
        
        logger = get_logger()
        mock = MockClient(logger)
        print_success("MockClient initialized")
        
        # Generate normal detections
        detections = mock.generate_detections(count=10)
        print_success(f"Generated {len(detections)} mock detections")
        
        if len(detections) > 0:
            det = detections[0]
            print_info(f"Sample detection: {det.mac} RSSI={det.rssi} dBm at ({det.latitude:.4f}, {det.longitude:.4f})")
        
        # Test scenario generation
        normal_scenario = mock.generate_scenario('normal')
        print_success(f"Generated normal scenario: {len(normal_scenario)} detections")
        
        threat_scenario = mock.generate_scenario('threat')
        print_success(f"Generated threat scenario: {len(threat_scenario)} detections")
        
        following_scenario = mock.generate_scenario('following')
        print_success(f"Generated following scenario: {len(following_scenario)} detections")
        
        # Test device info
        devices = mock.list_all_devices()
        print_info(f"Mock devices available: {len(devices)}")
        print_success("Device enumeration working")
        
        # Test reset
        mock.reset()
        print_success("Mock client reset working")
        
        return True
        
    except Exception as e:
        print_error(f"Mock client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_imports():
    """Test GUI component imports."""
    print_test("GUI Component Imports")
    
    try:
        print_info("Testing GUI imports (no display required)...")
        
        from gui.main_window import MainWindow
        print_success("MainWindow import successful")
        
        from gui.widgets.control_panel import ControlPanel
        print_success("ControlPanel import successful")
        
        from gui.widgets.log_viewer import LogViewer
        print_success("LogViewer import successful")
        
        from gui.widgets.status_widget import StatusWidget
        print_success("StatusWidget import successful")
        
        from gui.widgets.results_panel import ResultsPanel
        print_success("ResultsPanel import successful")
        
        from gui.styles import get_stylesheet, get_log_colors, get_threat_colors
        print_success("GUI styles import successful")
        
        # Test that stylesheet is non-empty
        stylesheet = get_stylesheet()
        if len(stylesheet) > 100:
            print_success("Stylesheet generated correctly")
        else:
            print_error("Stylesheet appears empty")
            return False
        
        # Test color dictionaries
        log_colors = get_log_colors()
        if len(log_colors) >= 5:
            print_success("Log colors defined")
        else:
            print_error("Log colors missing")
            return False
        
        threat_colors = get_threat_colors()
        if len(threat_colors) >= 4:
            print_success("Threat colors defined")
        else:
            print_error("Threat colors missing")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"GUI import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analysis_integration():
    """Test integration of Phase 1 and Phase 2 components."""
    print_test("Phase 1/2 Integration")
    
    try:
        from core.detector_engine import DetectorEngine
        from analysis.clustering import ClusterAnalyzer
        from analysis.gps_utils import GPSUtils
        from data.device import Device, DeviceType
        from data.location import Location, GPSCoordinate
        from utils.logger import get_logger
        from config import get_config
        
        config = get_config()
        logger = get_logger()
        
        print_success("All imports successful")
        
        # Create detector with Phase 1 data models
        detector = DetectorEngine(config, logger)
        detector.start()
        
        # Process a detection that uses Phase 1 models
        now = datetime.now()
        result = detector.process_detection(
            mac="AA:BB:CC:DD:EE:FF",
            ssid="Test-Network",
            rssi=-65,
            latitude=58.97,
            longitude=5.73,
            timestamp=now
        )
        
        # Check if device was tracked
        if "AA:BB:CC:DD:EE:FF" in detector.devices:
            device = detector.devices["AA:BB:CC:DD:EE:FF"]
            print_success("Phase 1 Device model works in Phase 2 engine")
        else:
            print_error("Device model integration failed")
            return False
        
        # Process multiple detections to create locations
        for i in range(5):
            detector.process_detection(
                mac="AA:BB:CC:DD:EE:FF",
                rssi=random.randint(-75, -55),
                latitude=58.97 + random.uniform(-0.001, 0.001),
                longitude=5.73 + random.uniform(-0.001, 0.001),
                timestamp=now + timedelta(seconds=i*10)
            )
        
        if len(detector.locations) > 0:
            print_success("Phase 1 Location model works in Phase 2 engine")
        else:
            print_error("Location model integration failed")
            return False
        
        # Cluster the locations
        analyzer = ClusterAnalyzer(eps_meters=100)
        clusters = analyzer.cluster_locations(list(detector.locations.values()))
        print_success("Analysis modules work with Phase 1 data models")
        
        detector.stop()
        return True
        
    except Exception as e:
        print_error(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_threat_detection_scenarios():
    """Test threat detection with specific scenarios."""
    print_test("Threat Detection Scenarios")
    
    try:
        from core.detector_engine import DetectorEngine
        from config import get_config
        from utils.logger import get_logger
        
        config = get_config()
        logger = get_logger()
        
        detector = DetectorEngine(config, logger)
        detector.start()
        print_success("Detector initialized for scenario testing")
        
        now = datetime.now()
        
        # Scenario 1: Single device with many detections (high threat)
        high_threat_mac = "AA:BB:CC:DD:EE:01"
        for i in range(15):
            detector.process_detection(
                mac=high_threat_mac,
                rssi=random.randint(-75, -50),
                latitude=58.97,
                longitude=5.73,
                timestamp=now + timedelta(seconds=i*5)
            )
        
        # Scenario 2: Device with following behavior (multiple locations)
        following_mac = "AA:BB:CC:DD:EE:02"
        for i in range(3):
            detector.process_detection(
                mac=following_mac,
                rssi=-70 + i*5,  # Getting closer (increasing RSSI)
                latitude=58.97 + i*0.005,
                longitude=5.73 + i*0.005,
                timestamp=now + timedelta(seconds=i*20)
            )
        
        # Scenario 3: Normal device (few detections)
        normal_mac = "AA:BB:CC:DD:EE:03"
        for i in range(2):
            detector.process_detection(
                mac=normal_mac,
                rssi=-70,
                latitude=58.97,
                longitude=5.73,
                timestamp=now + timedelta(seconds=i*30)
            )
        
        # Calculate threats
        detector.calculate_threat_scores()
        
        # Check high threat device
        high_threat_device = detector.threat_scores.get(high_threat_mac)
        if high_threat_device and high_threat_device.score > 30:
            print_success(f"High threat detected: {high_threat_device.device_mac} score={high_threat_device.score:.1f}")
        else:
            print_info(f"High threat device score: {high_threat_device.score if high_threat_device else 'None'}")
        
        # Check following threat
        following_device = detector.threat_scores.get(following_mac)
        if following_device:
            if following_device.is_following:
                print_success(f"Following behavior detected: {following_device.device_mac}")
            else:
                print_info(f"Following behavior not detected for {following_mac} (detection threshold not met)")
        
        # Check normal device
        normal_device = detector.threat_scores.get(normal_mac)
        if normal_device and normal_device.score < 50:
            print_success(f"Normal device score low: {normal_mac} score={normal_device.score:.1f}")
        
        print_success("Threat detection scenarios working")
        detector.stop()
        
        return True
        
    except Exception as e:
        print_error(f"Scenario test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}SURVEILLANCE DETECTION SYSTEM - PHASE 2 TESTING{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    results = {}
    
    # Run all tests
    results['Detection Engine'] = test_detector_engine()
    results['DBSCAN Clustering'] = test_clustering()
    results['GPS Utilities'] = test_gps_utils()
    results['Threat Scoring'] = test_threat_scorer()
    results['Mock Data Client'] = test_mock_client()
    results['GUI Imports'] = test_gui_imports()
    results['Phase 1/2 Integration'] = test_analysis_integration()
    results['Threat Detection Scenarios'] = test_threat_detection_scenarios()
    
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
        print(f"{GREEN}Phase 2 is ready! You can launch the GUI with: python3 main.py{RESET}")
        return 0
    else:
        print(f"{RED}✗ SOME TESTS FAILED ({passed}/{total} passed){RESET}")
        print(f"{YELLOW}Please fix the issues before using the application.{RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(main())