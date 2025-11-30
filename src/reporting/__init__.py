"""
Report generation modules.

Includes:
- KMLGenerator: Google Earth map visualization
- HTMLReporter: Professional HTML reports (coming soon)
- JSONExporter: JSON data export
"""

from .kml_generator import KMLGenerator

__all__ = [
    'KMLGenerator',
]