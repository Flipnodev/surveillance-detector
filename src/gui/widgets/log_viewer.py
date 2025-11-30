"""
Real-time log viewer widget with color-coded log levels.
"""

from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton
from PyQt6.QtGui import QTextCursor, QFont, QColor
from PyQt6.QtCore import Qt

from .styles import get_log_colors


class LogViewer(QWidget):
    """
    Real-time log display with color-coded messages.
    """
    
    def __init__(self, max_lines: int = 1000):
        """
        Initialize log viewer.
        
        Args:
            max_lines: Maximum lines to keep in display
        """
        super().__init__()
        self.max_lines = max_lines
        self.line_count = 0
        
        self._setup_ui()
        self.log_colors = get_log_colors()
    
    def _setup_ui(self):
        """Set up user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Log display
        self.log_text = QTextEdit()
        self.log_text.setObjectName("logViewer")
        self.log_text.setReadOnly(True)
        
        # Set monospace font
        font = QFont("Courier New", 9)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.log_text.setFont(font)
        
        layout.addWidget(self.log_text)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        clear_button = QPushButton("Clear")
        clear_button.setMaximumWidth(100)
        clear_button.clicked.connect(self.clear)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def add_log(self, message: str, level: str = 'INFO', 
               include_timestamp: bool = True):
        """
        Add a log message.
        
        Args:
            message: Log message text
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            include_timestamp: Include timestamp in message
        """
        # Format message
        if include_timestamp:
            timestamp = datetime.now().strftime('%H:%M:%S')
            formatted = f"[{timestamp}] [{level:8s}] {message}"
        else:
            formatted = f"[{level:8s}] {message}"
        
        # Get color for this level
        color = self.log_colors.get(level, '#d4d4d4')
        
        # Move cursor to end
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
        
        # Insert colored text
        self.log_text.setTextColor(QColor(color))
        self.log_text.insertPlainText(formatted + '\n')
        
        # Reset color
        self.log_text.setTextColor(QColor('#d4d4d4'))
        
        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
        # Trim old lines if necessary
        self.line_count += 1
        if self.line_count > self.max_lines:
            self._trim_oldest_lines()
    
    def _trim_oldest_lines(self):
        """Remove oldest lines when max_lines exceeded."""
        doc = self.log_text.document()
        block = doc.firstBlock()
        
        # Remove first 100 lines
        for _ in range(100):
            if block.isValid():
                cursor = self.log_text.textCursor()
                cursor.setPosition(block.position())
                cursor.select(cursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                block = block.next()
        
        self.line_count -= 100
    
    def clear(self):
        """Clear all log messages."""
        self.log_text.clear()
        self.line_count = 0
    
    def get_logs(self) -> str:
        """
        Get all log text.
        
        Returns:
            Complete log text
        """
        return self.log_text.toPlainText()
    
    def save_to_file(self, filepath: str):
        """
        Save logs to file.
        
        Args:
            filepath: Destination file path
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.get_logs())