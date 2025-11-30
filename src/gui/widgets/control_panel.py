"""
Control panel widget with run/stop buttons and configuration options.
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QSpinBox,
    QCheckBox, QFormLayout
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from core.detector_engine import DetectorEngine


class ControlPanel(QWidget):
    """
    Control panel for starting/stopping analysis and configuring parameters.
    """
    
    # Signals
    run_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    
    def __init__(self, config, logger: logging.Logger):
        """
        Initialize control panel.
        
        Args:
            config: Application configuration
            logger: Logger instance
        """
        super().__init__()
        self.config = config
        self.logger = logger
        self.detector = None
        
        self._setup_ui()
        
        self.logger.debug("Control panel initialized")
    
    def _setup_ui(self):
        """Set up user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Surveillance Detection Analysis")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("▶ Run Analysis")
        self.run_button.setObjectName("runButton")
        self.run_button.setMinimumHeight(40)
        self.run_button.clicked.connect(self._on_run)
        button_layout.addWidget(self.run_button)
        
        self.stop_button = QPushButton("⏹ Stop Analysis")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._on_stop)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # Configuration group
        config_group = QGroupBox("Configuration")
        config_layout = QFormLayout()
        
        # Time window selection
        self.time_window_combo = QComboBox()
        self.time_window_combo.addItems([
            "5 minutes",
            "10 minutes",
            "15 minutes",
            "20 minutes"
        ])
        config_layout.addRow("Analysis Window:", self.time_window_combo)
        
        # Minimum detections
        self.min_detections_spin = QSpinBox()
        self.min_detections_spin.setMinimum(1)
        self.min_detections_spin.setMaximum(100)
        self.min_detections_spin.setValue(int(self.config.detection.min_detections))
        config_layout.addRow("Min Detections:", self.min_detections_spin)
        
        # Dwell time threshold
        self.dwell_time_spin = QSpinBox()
        self.dwell_time_spin.setMinimum(60)
        self.dwell_time_spin.setMaximum(3600)
        self.dwell_time_spin.setSingleStep(60)
        self.dwell_time_spin.setValue(int(self.config.detection.min_dwell_time))
        self.dwell_time_spin.setSuffix(" seconds")
        config_layout.addRow("Min Dwell Time:", self.dwell_time_spin)
        
        # RSSI threshold
        self.rssi_spin = QSpinBox()
        self.rssi_spin.setMinimum(-100)
        self.rssi_spin.setMaximum(-30)
        self.rssi_spin.setValue(int(self.config.detection.rssi_proximity_threshold))
        self.rssi_spin.setSuffix(" dBm")
        config_layout.addRow("RSSI Threshold:", self.rssi_spin)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Detection parameters group
        params_group = QGroupBox("Detection Parameters")
        params_layout = QFormLayout()
        
        # Clustering distance
        self.clustering_dist_spin = QSpinBox()
        self.clustering_dist_spin.setMinimum(10)
        self.clustering_dist_spin.setMaximum(1000)
        self.clustering_dist_spin.setValue(int(self.config.clustering.eps_meters))
        self.clustering_dist_spin.setSuffix(" meters")
        params_layout.addRow("Clustering Distance:", self.clustering_dist_spin)
        
        # Threat detection options
        self.detect_following_check = QCheckBox("Detect Following Behavior")
        self.detect_following_check.setChecked(True)
        params_layout.addRow(self.detect_following_check)
        
        self.show_all_devices_check = QCheckBox("Show All Devices")
        self.show_all_devices_check.setChecked(False)
        params_layout.addRow(self.show_all_devices_check)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Status info
        self.status_info = QLabel("Ready to start analysis")
        layout.addWidget(self.status_info)
        
        layout.addStretch()
    
    def _on_run(self):
        """Handle run button click."""
        # Create detector engine
        self.detector = DetectorEngine(self.config, self.logger)
        
        # Update configuration from UI
        self.detector.config.detection.min_detections = self.min_detections_spin.value()
        self.detector.config.detection.min_dwell_time = self.dwell_time_spin.value()
        self.detector.config.clustering.eps_meters = self.clustering_dist_spin.value()
        
        # Update UI state
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.time_window_combo.setEnabled(False)
        self.min_detections_spin.setEnabled(False)
        self.dwell_time_spin.setEnabled(False)
        
        self.status_info.setText("Analysis running...")
        
        # Emit signal
        self.run_clicked.emit()
    
    def _on_stop(self):
        """Handle stop button click."""
        # Update UI state
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.time_window_combo.setEnabled(True)
        self.min_detections_spin.setEnabled(True)
        self.dwell_time_spin.setEnabled(True)
        
        self.status_info.setText("Analysis stopped")
        
        # Emit signal
        self.stop_clicked.emit()
    
    def get_detector_engine(self) -> DetectorEngine:
        """
        Get the detector engine instance.
        
        Returns:
            DetectorEngine object
        """
        return self.detector
    
    def get_selected_time_window(self) -> int:
        """
        Get selected time window in minutes.
        
        Returns:
            Time window in minutes
        """
        text = self.time_window_combo.currentText()
        return int(text.split()[0])
    
    def get_config_settings(self) -> dict:
        """
        Get current configuration settings from UI.
        
        Returns:
            Dictionary of settings
        """
        return {
            'time_window': self.get_selected_time_window(),
            'min_detections': self.min_detections_spin.value(),
            'dwell_time': self.dwell_time_spin.value(),
            'rssi_threshold': self.rssi_spin.value(),
            'clustering_distance': self.clustering_dist_spin.value(),
            'detect_following': self.detect_following_check.isChecked(),
            'show_all_devices': self.show_all_devices_check.isChecked(),
        }