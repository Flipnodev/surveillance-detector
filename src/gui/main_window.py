"""
Main application window with tabs for control, logs, and results.
"""

import logging
import threading
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QLabel
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon

from utils.file_manager import FileManager
from .styles import get_stylesheet
from .widgets.control_panel import ControlPanel
from .widgets.log_viewer import LogViewer
from .widgets.results_panel import ResultsPanel
from .widgets.status_widget import StatusWidget


class SignalEmitter(QObject):
    """Helper class to emit signals from threads."""
    detection_signal = pyqtSignal(dict)
    stats_signal = pyqtSignal(dict)
    threat_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Features:
    - Multi-tab interface (Control, Logs, Results, Statistics)
    - Real-time status updates
    - Log streaming
    - Threat visualization
    """
    
    def __init__(self, config, logger: logging.Logger, fm: FileManager):
        """
        Initialize main window.
        
        Args:
            config: Application configuration
            logger: Logger instance
            fm: FileManager instance
        """
        super().__init__()
        
        self.config = config
        self.logger = logger
        self.fm = fm
        
        # Get dark mode from config
        self.dark_mode = getattr(config.gui, 'theme', 'light') == 'dark'
        
        # Signal emitter for thread communication
        self.signals = SignalEmitter()
        self.signals.detection_signal.connect(self._on_detection)
        self.signals.stats_signal.connect(self._on_stats_update)
        self.signals.threat_signal.connect(self._on_threat_update)
        self.signals.error_signal.connect(self._on_error)
        
        # Detection engine (initialized in control panel)
        self.detector = None
        self.is_analyzing = False
        
        # Setup UI
        self._setup_ui()
        self._apply_styling()
        self._setup_timers()
        
        self.logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Set up user interface."""
        self.setWindowTitle(f"{self.config.app.name} v{self.config.app.version}")
        self.setGeometry(100, 100, 
                        self.config.gui.window.width,
                        self.config.gui.window.height)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.control_panel = ControlPanel(self.config, self.logger)
        self.log_viewer = LogViewer()
        self.results_panel = ResultsPanel(self.config)
        self.status_widget = StatusWidget()
        
        # Connect control panel signals
        self.control_panel.run_clicked.connect(self._on_run_clicked)
        self.control_panel.stop_clicked.connect(self._on_stop_clicked)
        
        # Add tabs
        self.tabs.addTab(self.control_panel, "Control")
        self.tabs.addTab(self.log_viewer, "Logs")
        self.tabs.addTab(self.results_panel, "Results")
        self.tabs.addTab(self.status_widget, "Statistics")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self._setup_status_bar()
    
    def _setup_status_bar(self):
        """Set up status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Status labels
        self.status_label = QLabel("Ready")
        self.device_label = QLabel("Devices: 0")
        self.detection_label = QLabel("Detections: 0")
        
        self.statusbar.addWidget(self.status_label, 1)
        self.statusbar.addWidget(self.device_label)
        self.statusbar.addWidget(self.detection_label)
    
    def _apply_styling(self):
        """Apply application stylesheet."""
        from .styles import get_stylesheet
        self.setStyleSheet(get_stylesheet(dark_mode=self.dark_mode))
    
    def _setup_timers(self):
        """Set up update timers."""
        # Log update timer
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self._update_logs)
        
        # Stats update timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_statistics)
    
    def _on_run_clicked(self):
        """Handle run button click."""
        self.detector = self.control_panel.get_detector_engine()
        
        if self.detector is None:
            self._on_error("Failed to initialize detector engine")
            return
        
        self.is_analyzing = True
        self.status_label.setText("Running analysis...")
        
        # Start timers
        log_interval = int(self.config.gui.log_update_interval)
        stats_interval = int(self.config.gui.status_update_interval)
        self.log_timer.start(log_interval)
        self.stats_timer.start(stats_interval)
        
        # Start analysis in background
        self.analysis_thread = threading.Thread(target=self._run_analysis)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
        self.logger.info("Analysis started")
    
    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.is_analyzing = False
        self.log_timer.stop()
        self.stats_timer.stop()
        
        if self.detector:
            self.detector.stop()
        
        self.status_label.setText("Stopped")
        self.logger.info("Analysis stopped")
    
    def _run_analysis(self):
        """Run detection analysis in background thread."""
        try:
            from clients.mock_client import MockClient
            from datetime import datetime, timedelta
            
            # Initialize mock client
            mock = MockClient(self.logger)
            
            self.detector.start()
            self.logger.info("Starting mock detection simulation...")
            
            # Simulate detections for 60 seconds or until stopped
            start_time = datetime.now()
            while self.is_analyzing and (datetime.now() - start_time).total_seconds() < 60:
                # Generate mock detections
                detections = mock.generate_detections(count=5)
                
                # Process each detection
                for detection in detections:
                    if not self.is_analyzing:
                        break
                    
                    self.detector.process_detection(
                        mac=detection.mac,
                        ssid=detection.ssid,
                        rssi=detection.rssi,
                        latitude=detection.latitude,
                        longitude=detection.longitude,
                        timestamp=detection.timestamp
                    )
                    
                    # Emit signal
                    self.signals.detection_signal.emit(detection.to_dict())
                
                # Calculate and emit threat scores
                threats = self.detector.calculate_threat_scores()
                threat_list = [t for t in threats.values()]
                self.signals.threat_signal.emit(threat_list)
                
                # Small delay to avoid overwhelming the UI
                threading.Event().wait(0.1)
            
            self.detector.stop()
            self.status_label.setText("Analysis complete")
            self.logger.info("Analysis simulation completed")
            
        except Exception as e:
            self.signals.error_signal.emit(f"Analysis error: {str(e)}")
            self.logger.error(f"Analysis error: {e}", exc_info=True)
    
    def _on_detection(self, detection_data: dict):
        """Handle new detection."""
        self.log_viewer.add_log(
            f"Detection: {detection_data['mac']} RSSI={detection_data['rssi']}dBm",
            'INFO'
        )
    
    def _update_logs(self):
        """Update log display with new messages."""
        # Logs are added directly by the logger
        pass
    
    def _update_statistics(self):
        """Update statistics display."""
        if self.detector and self.detector.is_running:
            stats = self.detector.get_statistics()
            self.signals.stats_signal.emit(stats)
    
    def _on_stats_update(self, stats: dict):
        """Handle statistics update."""
        self.device_label.setText(f"Devices: {stats['device_count']}")
        self.detection_label.setText(f"Detections: {stats['detection_count']}")
        self.status_widget.update_stats(stats)
        self.results_panel.update_from_detector(self.detector)
    
    def _on_threat_update(self, threats: list):
        """Handle threat update."""
        self.results_panel.update_threats(threats)
    
    def _on_error(self, error_msg: str):
        """Handle error signal."""
        self.logger.error(error_msg)
        self.status_label.setText(f"Error: {error_msg[:50]}")
        self.log_viewer.add_log(error_msg, 'ERROR')
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.detector and self.detector.is_running:
            self._on_stop_clicked()
        
        self.logger.info("Application closing")
        event.accept()