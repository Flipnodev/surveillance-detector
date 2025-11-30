from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QGroupBox, QProgressBar
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class StatusWidget(QWidget):
    """Display session statistics and status."""
    
    def __init__(self):
        """Initialize status widget."""
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up user interface."""
        layout = QVBoxLayout(self)
        
        # Session info group
        session_group = QGroupBox("Session Information")
        session_layout = QGridLayout()
        
        self.elapsed_label = QLabel("Elapsed Time: 00:00:00")
        self.device_count_label = QLabel("Tracked Devices: 0")
        self.detection_count_label = QLabel("Total Detections: 0")
        self.dpm_label = QLabel("Detections/Min: 0.0")
        
        session_layout.addWidget(self.elapsed_label, 0, 0)
        session_layout.addWidget(self.device_count_label, 0, 1)
        session_layout.addWidget(self.detection_count_label, 1, 0)
        session_layout.addWidget(self.dpm_label, 1, 1)
        
        session_group.setLayout(session_layout)
        layout.addWidget(session_group)
        
        # Threats group
        threats_group = QGroupBox("Threat Summary")
        threats_layout = QGridLayout()
        
        self.high_label = QLabel("High Threats: 0")
        self.high_label.setStyleSheet("color: #ff0000; font-weight: bold;")
        self.medium_label = QLabel("Medium Threats: 0")
        self.medium_label.setStyleSheet("color: #ff5500; font-weight: bold;")
        self.low_label = QLabel("Low Threats: 0")
        self.low_label.setStyleSheet("color: #ffaa00;")
        self.following_label = QLabel("Following Behavior: 0")
        self.following_label.setStyleSheet("color: #ff00ff; font-weight: bold;")
        
        threats_layout.addWidget(self.high_label, 0, 0)
        threats_layout.addWidget(self.medium_label, 0, 1)
        threats_layout.addWidget(self.low_label, 1, 0)
        threats_layout.addWidget(self.following_label, 1, 1)
        
        threats_group.setLayout(threats_layout)
        layout.addWidget(threats_group)
        
        layout.addStretch()
    
    def update_stats(self, stats: dict):
        """Update displayed statistics."""
        elapsed = int(stats['elapsed_seconds'])
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        
        self.elapsed_label.setText(f"Elapsed Time: {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.device_count_label.setText(f"Tracked Devices: {stats['device_count']}")
        self.detection_count_label.setText(f"Total Detections: {stats['detection_count']}")
        self.dpm_label.setText(f"Detections/Min: {stats['detections_per_minute']:.1f}")
        
        threats = stats['threat_summary']
        self.high_label.setText(f"High Threats: {threats['high']}")
        self.medium_label.setText(f"Medium Threats: {threats['medium']}")
        self.low_label.setText(f"Low Threats: {threats['low']}")
        self.following_label.setText(f"Following Behavior: {threats['following']}")