"""
PyQt6 styling and theme configuration.

Provides consistent styling for the GUI application with light and dark mode support.
"""


def get_stylesheet(dark_mode: bool = False) -> str:
    """
    Get the main application stylesheet.
    
    Args:
        dark_mode: Use dark mode if True, light mode if False
    
    Returns:
        CSS stylesheet string
    """
    if dark_mode:
        return get_dark_stylesheet()
    else:
        return get_light_stylesheet()


def get_light_stylesheet() -> str:
    """Get light mode stylesheet."""
    return """
    /* Main Application */
    QMainWindow {
        background-color: #f5f5f5;
    }
    
    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #ddd;
    }
    
    QTabBar::tab {
        background-color: #e0e0e0;
        color: #333;
        padding: 8px 20px;
        border: 1px solid #ccc;
        border-bottom: none;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #fff;
        color: #000;
        border: 1px solid #ccc;
        border-bottom: 1px solid #fff;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #f0f0f0;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 12px;
    }
    
    QPushButton:hover {
        background-color: #106ebe;
    }
    
    QPushButton:pressed {
        background-color: #005a9e;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    
    /* Run Button - Special */
    #runButton {
        background-color: #107c10;
        font-size: 13px;
        padding: 10px 20px;
    }
    
    #runButton:hover {
        background-color: #09662e;
    }
    
    #runButton:pressed {
        background-color: #064c1c;
    }
    
    /* Stop Button */
    #stopButton {
        background-color: #d83b01;
    }
    
    #stopButton:hover {
        background-color: #a82200;
    }
    
    /* Text Input */
    QLineEdit, QTextEdit, QPlainTextEdit {
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 6px;
        background-color: white;
        color: #333;
        selection-background-color: #0078d4;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #0078d4;
        padding: 5px;
    }
    
    /* Labels */
    QLabel {
        color: #333;
    }
    
    /* Combobox */
    QComboBox {
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 6px;
        background-color: white;
        color: #333;
    }
    
    QComboBox:focus {
        border: 2px solid #0078d4;
        padding: 5px;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    /* Spinbox */
    QSpinBox, QDoubleSpinBox {
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 6px;
        background-color: white;
        color: #333;
    }
    
    /* Log Viewer */
    #logViewer {
        font-family: 'Courier New', monospace;
        font-size: 10px;
        background-color: #1e1e1e;
        color: #d4d4d4;
        border: 1px solid #ccc;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #f0f0f0;
        color: #333;
        border-top: 1px solid #ccc;
    }
    
    QStatusBar::item {
        border: none;
    }
    
    /* Progress Bar */
    QProgressBar {
        border: 1px solid #ccc;
        border-radius: 4px;
        text-align: center;
        height: 20px;
    }
    
    QProgressBar::chunk {
        background-color: #0078d4;
    }
    
    /* Scrollbar */
    QScrollBar:vertical {
        border: none;
        background-color: #f5f5f5;
        width: 12px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #c0c0c0;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #a0a0a0;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    
    QScrollBar:horizontal {
        border: none;
        background-color: #f5f5f5;
        height: 12px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #c0c0c0;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #a0a0a0;
    }
    
    /* Group Box */
    QGroupBox {
        color: #333;
        border: 1px solid #ccc;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }
    
    /* Splitter Handle */
    QSplitter::handle {
        background-color: #ddd;
    }
    
    QSplitter::handle:hover {
        background-color: #ccc;
    }
    
    /* Table Widget */
    QTableWidget {
        background-color: white;
        color: #333;
        border: 1px solid #ddd;
    }
    
    QHeaderView::section {
        background-color: #f0f0f0;
        color: #333;
        padding: 5px;
        border: 1px solid #ddd;
    }
    
    QTableWidget::item {
        padding: 5px;
        border: 1px solid #eee;
    }
    
    QTableWidget::item:selected {
        background-color: #0078d4;
        color: white;
    }
    """


def get_dark_stylesheet() -> str:
    """Get dark mode stylesheet."""
    return """
    /* Main Application */
    QMainWindow {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    
    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #3e3e42;
    }
    
    QTabBar::tab {
        background-color: #2d2d30;
        color: #cccccc;
        padding: 8px 20px;
        border: 1px solid #3e3e42;
        border-bottom: none;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #3e3e42;
        border-bottom: 1px solid #1e1e1e;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #3e3e42;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 12px;
    }
    
    QPushButton:hover {
        background-color: #1084d7;
    }
    
    QPushButton:pressed {
        background-color: #005a9e;
    }
    
    QPushButton:disabled {
        background-color: #444444;
        color: #888888;
    }
    
    /* Run Button - Special */
    #runButton {
        background-color: #107c10;
        font-size: 13px;
        padding: 10px 20px;
    }
    
    #runButton:hover {
        background-color: #1b9e1b;
    }
    
    #runButton:pressed {
        background-color: #064c1c;
    }
    
    /* Stop Button */
    #stopButton {
        background-color: #d83b01;
    }
    
    #stopButton:hover {
        background-color: #f7630c;
    }
    
    /* Text Input */
    QLineEdit, QTextEdit, QPlainTextEdit {
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 6px;
        background-color: #3c3c3c;
        color: #cccccc;
        selection-background-color: #0078d4;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #0078d4;
        padding: 5px;
    }
    
    /* Labels */
    QLabel {
        color: #e0e0e0;
    }
    
    /* Combobox */
    QComboBox {
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 6px;
        background-color: #3c3c3c;
        color: #cccccc;
    }
    
    QComboBox:focus {
        border: 2px solid #0078d4;
        padding: 5px;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox::down-arrow {
        image: none;
    }
    
    /* Spinbox */
    QSpinBox, QDoubleSpinBox {
        border: 1px solid #3e3e42;
        border-radius: 4px;
        padding: 6px;
        background-color: #3c3c3c;
        color: #cccccc;
    }
    
    /* Log Viewer */
    #logViewer {
        font-family: 'Courier New', monospace;
        font-size: 10px;
        background-color: #1e1e1e;
        color: #d4d4d4;
        border: 1px solid #3e3e42;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #2d2d30;
        color: #cccccc;
        border-top: 1px solid #3e3e42;
    }
    
    QStatusBar::item {
        border: none;
    }
    
    /* Progress Bar */
    QProgressBar {
        border: 1px solid #3e3e42;
        border-radius: 4px;
        text-align: center;
        height: 20px;
        background-color: #3c3c3c;
    }
    
    QProgressBar::chunk {
        background-color: #0078d4;
    }
    
    /* Scrollbar */
    QScrollBar:vertical {
        border: none;
        background-color: #1e1e1e;
        width: 12px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #555555;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #707070;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    
    QScrollBar:horizontal {
        border: none;
        background-color: #1e1e1e;
        height: 12px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #555555;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #707070;
    }
    
    /* Group Box */
    QGroupBox {
        color: #e0e0e0;
        border: 1px solid #3e3e42;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }
    
    /* Splitter Handle */
    QSplitter::handle {
        background-color: #3e3e42;
    }
    
    QSplitter::handle:hover {
        background-color: #555555;
    }
    
    /* Table Widget */
    QTableWidget {
        background-color: #3c3c3c;
        color: #cccccc;
        border: 1px solid #3e3e42;
    }
    
    QHeaderView::section {
        background-color: #2d2d30;
        color: #cccccc;
        padding: 5px;
        border: 1px solid #3e3e42;
    }
    
    QTableWidget::item {
        padding: 5px;
        border: 1px solid #505050;
        background-color: #3c3c3c;
        color: #cccccc;
    }
    
    QTableWidget::item:selected {
        background-color: #0078d4;
        color: white;
    }
    """


def get_log_colors(dark_mode: bool = False) -> dict:
    """
    Get color codes for log levels.
    
    Args:
        dark_mode: Use dark mode colors if True
    
    Returns:
        Dictionary mapping log levels to HTML color codes
    """
    if dark_mode:
        return {
            'DEBUG': '#888888',    # Gray
            'INFO': '#4ec9b0',     # Teal (better on dark bg)
            'WARNING': '#ce9178',  # Orange/tan
            'ERROR': '#f48771',    # Light red
            'CRITICAL': '#c586c0', # Purple
        }
    else:
        return {
            'DEBUG': '#888888',    # Gray
            'INFO': '#00aa00',     # Green
            'WARNING': '#ffaa00',  # Orange
            'ERROR': '#ff0000',    # Red
            'CRITICAL': '#ff00ff', # Magenta
        }


def get_threat_colors(dark_mode: bool = False) -> dict:
    """
    Get color codes for threat levels.
    
    Args:
        dark_mode: Use dark mode colors if True
    
    Returns:
        Dictionary mapping threat levels to colors
    """
    if dark_mode:
        return {
            'none': '#4ec9b0',     # Teal (safe)
            'low': '#dcdcaa',      # Yellow
            'medium': '#ce9178',   # Orange
            'high': '#f48771',     # Light red
            'following': '#c586c0', # Purple
        }
    else:
        return {
            'none': '#00aa00',     # Green
            'low': '#ffaa00',      # Orange
            'medium': '#ff5500',   # Dark Orange
            'high': '#ff0000',     # Red
            'following': '#ff00ff', # Magenta
        }