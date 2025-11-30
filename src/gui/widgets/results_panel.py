from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from .styles import get_threat_colors


class ResultsPanel(QWidget):
    """Display analysis results and threat list."""
    
    def __init__(self, config):
        """Initialize results panel."""
        super().__init__()
        self.config = config
        self.threat_colors = get_threat_colors()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up user interface."""
        layout = QVBoxLayout(self)
        
        # Threats table
        threats_group = QGroupBox("Detected Threats")
        threats_layout = QVBoxLayout()
        
        self.threats_table = QTableWidget()
        self.threats_table.setColumnCount(7)
        self.threats_table.setHorizontalHeaderLabels([
            'Device MAC', 'Threat Level', 'Score', 'Detections',
            'Dwell Time', 'Locations', 'Following'
        ])
        
        header = self.threats_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        threats_layout.addWidget(self.threats_table)
        threats_group.setLayout(threats_layout)
        layout.addWidget(threats_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        export_kml = QPushButton("Export KML")
        export_kml.clicked.connect(self._export_kml)
        button_layout.addWidget(export_kml)
        
        export_json = QPushButton("Export JSON")
        export_json.clicked.connect(self._export_json)
        button_layout.addWidget(export_json)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def update_threats(self, threats: list):
        """Update threats table."""
        self.threats_table.setRowCount(len(threats))
        
        for row, threat in enumerate(threats):
            # MAC
            mac_item = QTableWidgetItem(threat.device_mac)
            self.threats_table.setItem(row, 0, mac_item)
            
            # Level
            level_item = QTableWidgetItem(threat.level.upper())
            color = self.threat_colors.get(threat.level, '#d4d4d4')
            level_item.setForeground(QColor(color))
            self.threats_table.setItem(row, 1, level_item)
            
            # Score
            score_item = QTableWidgetItem(f"{threat.score:.1f}")
            self.threats_table.setItem(row, 2, score_item)
            
            # Detections
            det_item = QTableWidgetItem(str(threat.detection_count))
            self.threats_table.setItem(row, 3, det_item)
            
            # Dwell time
            dwell = int(threat.dwell_time)
            dwell_item = QTableWidgetItem(f"{dwell}s")
            self.threats_table.setItem(row, 4, dwell_item)
            
            # Locations
            loc_item = QTableWidgetItem(str(threat.location_count))
            self.threats_table.setItem(row, 5, loc_item)
            
            # Following
            follow_item = QTableWidgetItem("YES" if threat.is_following else "NO")
            if threat.is_following:
                follow_item.setForeground(QColor('#ff00ff'))
            self.threats_table.setItem(row, 6, follow_item)
    
    def update_from_detector(self, detector):
        """Update display from detector engine."""
        if detector:
            threats = list(detector.threat_scores.values())
            self.update_threats(threats)
    
    def _export_kml(self):
        """Export results as KML."""
        # Placeholder for KML export
        pass
    
    def _export_json(self):
        """Export results as JSON."""
        # Placeholder for JSON export
        pass