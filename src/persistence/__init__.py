
"""
Data persistence layer for session storage and history.

Includes:
- DatabaseManager: SQLite backend for device/location/threat history
- SessionManager: Session state management (coming soon)
"""

from .database import DatabaseManager

__all__ = [
    'DatabaseManager',
]