# Surveillance Detection System

A comprehensive Python-based system for detecting surveillance through wireless device monitoring, GPS tracking, behavioral analysis, and threat scoring.

**Version:** 1.0.0  
**Status:** Phase 2 Complete (GUI + Detection Engine)

---

## Features

### Core Detection
- **Real-time device tracking** - Monitor wireless devices via WiFi/Bluetooth
- **Location clustering** - DBSCAN-based geographic grouping
- **Threat scoring** - Multi-factor analysis (detections, dwell time, RSSI trend, location diversity)
- **Following behavior detection** - Identify potential surveillance patterns

### GUI Interface
- **Modern PyQt6 interface** - Tabbed design with real-time updates
- **Control panel** - Run/stop analysis with configurable parameters
- **Live log viewer** - Color-coded real-time logging
- **Results panel** - Threat table with export options
- **Statistics display** - Session metrics and threat summary

### Analysis Modules
- **Clustering** - DBSCAN location grouping with configurable radius
- **GPS utilities** - Coordinate calculations, bearing, proximity
- **Threat scoring** - Advanced multi-factor assessment
- **Mock data generator** - Realistic synthetic detections for testing

---

## System Requirements

### Hardware
- **Raspberry Pi 4** (recommended) or Linux desktop
- **2GB RAM minimum** (4GB+ recommended)
- **100MB free disk space**
- **WiFi adapter** (for live Kismet integration, optional)

### Software
- **Python 3.11+**
- **pip** package manager
- **git** (for version control)

### Optional
- **Kismet** - For real wireless monitoring (Phase 3)
- **WiGLE API** - For SSID geolocation (Phase 3)
- **Pandoc** - For HTML report generation

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/surveillance-detection.git
cd surveillance-detection
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Verify Configuration

```bash
# Ensure config.yaml exists in project root
ls -la config.yaml

# If not present, copy from config/config.yaml
cp config/config.yaml config.yaml
```

### 5. Run Phase 1 Tests (Optional but Recommended)

```bash
python3 test_phase1.py
```

Expected output: All tests PASSED ✓

---

## Quick Start

### Method 1: Using Launcher Script (Recommended)

```bash
chmod +x run.sh
./run.sh
```

The script will:
1. Check Python installation
2. Create/activate virtual environment
3. Install dependencies
4. Optionally run Phase 1 tests
5. Launch the GUI application

### Method 2: Manual Launch

```bash
source venv/bin/activate
python3 main.py
```

---

## Using the Application

### Main GUI Window

The application opens with a tabbed interface:

#### Control Tab
- **Run Analysis** button - Start surveillance detection
- **Stop Analysis** button - Stop current analysis
- **Configuration options:**
  - Analysis time window (5/10/15/20 minutes)
  - Minimum detections threshold
  - Minimum dwell time (seconds)
  - RSSI proximity threshold
  - Clustering distance (meters)
  - Detection options (following behavior, all devices)

#### Logs Tab
- Real-time colored log display
- Color codes:
  - **Green** - INFO messages
  - **Yellow** - WARNING messages
  - **Red** - ERROR messages
  - **Magenta** - CRITICAL messages
- Clear button to reset log view
- Logs automatically scroll to latest messages

#### Results Tab
- Threat summary table showing:
  - Device MAC address
  - Threat level (Low/Medium/High)
  - Threat score (0-100)
  - Detection count
  - Dwell time
  - Location count
  - Following behavior indicator
- Export buttons (KML, JSON) for further analysis

#### Statistics Tab
- Session information (elapsed time, device count)
- Detection statistics (total count, detections/minute)
- Threat summary (high/medium/low/following threats)

---

## Analysis Configuration

### Key Parameters

**config.yaml** contains all configurable parameters:

```yaml
detection:
  time_windows: [5, 10, 15, 20]        # Analysis windows (minutes)
  min_detections: 3                     # Minimum detections to track
  min_dwell_time: 300                   # Minimum seconds at location
  rssi_proximity_threshold: -70         # Signal strength threshold (dBm)
  
  scoring:
    detection_count_weight: 0.3         # 30% of threat score
    dwell_time_weight: 0.3              # 30% of threat score
    rssi_trend_weight: 0.2              # 20% of threat score
    location_count_weight: 0.2          # 20% of threat score
  
  threat_levels:
    low: 30                             # Score ≥ 30 = low threat
    medium: 60                          # Score ≥ 60 = medium threat
    high: 80                            # Score ≥ 80 = high threat

clustering:
  eps_meters: 100                       # Max distance for location cluster
  min_samples: 2                        # Min points to form cluster
```

### Threat Scoring

Threat score calculation:

1. **Detection Count Score** (0-30)
   - Devices detected multiple times score higher
   - Threshold: `min_detections`

2. **Dwell Time Score** (0-30)
   - Devices lingering at location score higher
   - Threshold: `min_dwell_time` (seconds)

3. **RSSI Trend Score** (0-20)
   - Increasing RSSI (getting closer) = 20 points
   - Stable = 10 points
   - Decreasing (moving away) = 5 points

4. **Location Count Score** (0-20)
   - Multiple location visits indicate suspicious behavior
   - More locations = higher score

5. **Following Behavior Boost** (×1.5)
   - Applied if 2+ following indicators detected:
     - Multiple location visits
     - Increasing RSSI trend
     - High detection count
     - Recent detections

---

## Mock Data for Testing

The application includes a mock data generator for testing without Kismet:

```python
from clients.mock_client import MockClient

mock = MockClient()

# Generate 10 random detections
detections = mock.generate_detections(count=10)

# Generate specific scenarios
detections = mock.generate_scenario('normal')      # Normal activity
detections = mock.generate_scenario('threat')      # High-threat device
detections = mock.generate_scenario('following')   # Following behavior
```

Mock devices include:
- iPhone, Android phones
- iPad, Laptops
- Devices with following behavior (MACs ending in :05, :06)

---

## Project Structure

```
surveillance-detection/
├── main.py                          # Application entry point
├── run.sh                           # Launcher script
├── config.yaml                      # Configuration (copy from config/)
├── requirements.txt                 # Python dependencies
├── test_phase1.py                   # Phase 1 unit tests
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── detector_engine.py       # Detection engine
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── clustering.py            # DBSCAN clustering
│   │   ├── gps_utils.py             # GPS utilities
│   │   └── threat_scorer.py         # Threat scoring
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── device.py                # Device data model
│   │   └── location.py              # Location data model
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py           # Main GUI window
│   │   ├── styles.py                # PyQt6 styling
│   │   ├── widgets/
│   │   │   ├── __init__.py
│   │   │   ├── control_panel.py     # Run/stop controls
│   │   │   ├── log_viewer.py        # Real-time logs
│   │   │   ├── status_widget.py     # Statistics display
│   │   │   ├── results_panel.py     # Threat results
│   │   │   └── styles.py            # Widget styles
│   │   └── dialogs/
│   │       └── __init__.py
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   └── mock_client.py           # Mock data generator
│   │
│   ├── reporting/
│   │   └── __init__.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                # Logging system
│       ├── file_manager.py          # File operations
│       └── validators.py            # Input validation
│
├── config/
│   ├── __init__.py                  # Config loader
│   └── config.yaml                  # Config template
│
├── outputs/
│   ├── kml/                         # KML export directory
│   ├── reports/                     # Report export directory
│   ├── logs/                        # Session logs
│   └── data/                        # Session data
│
└── tests/
    └── __init__.py
```

---

## Troubleshooting

### Issue: "config.yaml not found"
**Solution:** Copy `config/config.yaml` to project root:
```bash
cp config/config.yaml config.yaml
```

### Issue: PyQt6 import error
**Solution:** Reinstall PyQt6:
```bash
pip install --upgrade PyQt6
```

### Issue: "ModuleNotFoundError: No module named 'src'"
**Solution:** Ensure you're running from project root:
```bash
cd /path/to/surveillance-detection
python3 main.py
```

### Issue: GUI window doesn't display
**Solution:** Check for X11 forwarding on remote systems:
```bash
# On Raspberry Pi, enable X11 forwarding
sudo raspi-config  # Select Interfacing Options > SSH > Enable
```

### Issue: Mock data not generating
**Solution:** Check that `debug.use_mock_data` is true in config.yaml

---

## Phase Development Roadmap

### Phase 1: ✅ Complete
- Foundation components (logging, file manager, validators)
- Data models (Device, Location, GPSCoordinate)
- Configuration system
- Unit tests

### Phase 2: ✅ Complete
- **GUI (PyQt6)** - Multi-tab interface with real-time updates
- **Detection Engine** - Threat scoring and following behavior detection
- **Analysis Modules** - Clustering, GPS utilities, threat scoring
- **Mock Client** - Synthetic data generation for testing

### Phase 3: 🚀 Planned
- **Kismet Integration** - Live WiFi monitoring
  - REST API client
  - Event streaming
  - GPS data extraction
  - Bluetooth GPS sources

- **Advanced Reporting**
  - KML map generation
  - Markdown reports
  - HTML report generation
  - PDF export

- **WiGLE Integration**
  - SSID geolocation
  - Reverse WiFi lookup
  - SSID enrichment

- **Performance Optimization**
  - Multi-threaded analysis
  - Database backend (SQLite)
  - Caching system
  - Memory optimization

### Phase 4: 🔮 Future
- Web dashboard
- Mobile app integration
- Machine learning threat classification
- Distributed system support
- Real-time alerts

---

## Development & Contributing

### Running Tests

```bash
# Phase 1 unit tests
python3 test_phase1.py

# All tests should pass ✓
```

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions small and focused

### Logging

```python
from utils.logger import get_logger

logger = get_logger()
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## Performance Notes

- **Memory usage:** ~50-100MB for typical operation
- **CPU usage:** <5% on Raspberry Pi 4 (idle), 15-20% (analyzing)
- **Log rotation:** 10MB per file, keeps 5 backups
- **Max devices:** 1000 simultaneous (configurable)
- **Max log lines:** 1000 in GUI (configurable)

---

## Security Considerations

⚠️ **Important:** This is a security tool for legitimate surveillance detection. Use responsibly and legally.

- Run only on networks you own or have permission to monitor
- Respect privacy laws in your jurisdiction
- Do not intercept network traffic without authorization
- Keep API credentials (WiGLE) secure

---

## License

[Add your license here]

---

## Support & Documentation

- **GitHub Issues:** Report bugs and request features
- **Documentation:** See `/docs` directory
- **Examples:** See `/examples` directory

---

## Changelog

### v1.0.0 (Phase 2 Complete)
- ✅ Full GUI implementation
- ✅ Detection engine with threat scoring
- ✅ Mock data generator
- ✅ Real-time log viewer
- ✅ Statistics and results display

---

**Ready to monitor? Run `./run.sh` to get started!** 🚀