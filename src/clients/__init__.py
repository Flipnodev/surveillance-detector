"""
External API client implementations.

Includes:
- MockClient: Synthetic device generation (Phase 2)
- KismetClient: Real wireless monitoring (Phase 3)
- WiGLEClient: SSID geolocation (Phase 3)
"""

from .mock_client import MockClient, MockDetection
from .kismet_client import KismetClient, KismetDevice
from .wigle_client import WiGLEClient, SSIDLocation

__all__ = [
    'MockClient',
    'MockDetection',
    'KismetClient',
    'KismetDevice',
    'WiGLEClient',
    'SSIDLocation',
]