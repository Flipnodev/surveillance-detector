#!/usr/bin/env python3
"""
Surveillance Detection System - Main Entry Point

Initializes the application, sets up all components, and launches the GUI.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.logger import setup_logging, get_logger
from utils.file_manager import FileManager
from config import load_config, get_config
from gui.main_window import MainWindow

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("ERROR: PyQt6 not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


def initialize_application():
    """
    Initialize all application components.
    
    Returns:
        Tuple of (logger, config, file_manager)
    """
    # Load configuration
    try:
        config = load_config('config.yaml')
    except FileNotFoundError:
        print("ERROR: config.yaml not found in project root")
        sys.exit(1)
    
    # Initialize logging
    log_level = getattr(__import__('logging'), config.logging.console_level)
    logger = setup_logging(
        log_dir=config.directories.logs,
        console_level=log_level,
        file_level=__import__('logging').DEBUG
    )
    
    # Initialize file manager
    fm = FileManager()
    fm.initialize_directories({
        'kml': config.directories.kml,
        'reports': config.directories.reports,
        'logs': config.directories.logs,
        'data': config.directories.data,
    })
    
    logger.info("=" * 70)
    logger.info(f"{config.app.name} v{config.app.version}")
    logger.info("=" * 70)
    logger.info("Application components initialized successfully")
    
    return logger, config, fm


def main():
    """Main application entry point."""
    try:
        # Initialize components
        logger, config, fm = initialize_application()
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName(config.app.name)
        app.setApplicationVersion(config.app.version)
        
        logger.info("Launching GUI...")
        
        # Create and show main window
        window = MainWindow(config, logger, fm)
        window.show()
        
        logger.info("GUI window displayed")
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()