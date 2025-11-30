"""
WiGLE API client for SSID geolocation and enrichment.

Provides SSID-to-location lookups and organization identification
using the WiGLE WiFi database API.
"""

import logging
import requests
import time
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class SSIDLocation:
    """SSID location information from WiGLE."""
    ssid: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    found_count: int = 0
    last_found: Optional[str] = None
    organization: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'ssid': self.ssid,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'found_count': self.found_count,
            'last_found': self.last_found,
            'organization': self.organization,
        }


class WiGLEClient:
    """
    Client for WiGLE WiFi geolocation API.
    
    Features:
    - SSID lookup in WiGLE database
    - Approximate geolocation
    - Organization identification
    - Caching to reduce API calls
    - Rate limiting support
    """
    
    def __init__(self, api_key: str, logger: logging.Logger = None,
                 rate_limit: int = 10):
        """
        Initialize WiGLE client.
        
        Args:
            api_key: WiGLE API key
            logger: Logger instance
            rate_limit: Max requests per minute
        """
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)
        self.rate_limit = rate_limit
        
        self.api_url = "https://api.wigle.net/api/v2"
        self.cache: Dict[str, SSIDLocation] = {}
        self.cache_time: Dict[str, datetime] = {}
        self.cache_duration = 3600  # 1 hour
        self.last_request_time = 0
        self.request_count = 0
        
        self.is_enabled = bool(api_key and api_key != "YOUR_WIGLE_API_KEY_HERE")
        
        if not self.is_enabled:
            self.logger.warning("WiGLE API not configured (disabled)")
        else:
            self.logger.info("WiGLE client initialized")
    
    def lookup_ssid(self, ssid: str) -> Optional[SSIDLocation]:
        """
        Look up SSID location in WiGLE database.
        
        Args:
            ssid: WiFi network SSID
            
        Returns:
            SSIDLocation object or None
        """
        if not self.is_enabled:
            return None
        
        if not ssid:
            return None
        
        # Check cache first
        if ssid in self.cache:
            if self._is_cache_valid(ssid):
                self.logger.debug(f"SSID cache hit: {ssid}")
                return self.cache[ssid]
            else:
                del self.cache[ssid]
        
        # Make API request
        return self._query_wigle(ssid)
    
    def _is_cache_valid(self, ssid: str) -> bool:
        """Check if cache entry is still valid."""
        if ssid not in self.cache_time:
            return False
        
        age = datetime.now() - self.cache_time[ssid]
        return age.total_seconds() < self.cache_duration
    
    def _query_wigle(self, ssid: str) -> Optional[SSIDLocation]:
        """
        Query WiGLE API for SSID information.
        
        Args:
            ssid: SSID to search
            
        Returns:
            SSIDLocation or None
        """
        try:
            # Rate limiting
            self._apply_rate_limit()
            
            # Prepare request
            headers = {
                'User-Agent': 'SurveillanceDetector/1.0'
            }
            
            # Use HTTP Basic Auth with API key as username
            auth = (self.api_key, self.api_key)
            
            # Query endpoint
            url = f"{self.api_url}/network/search"
            params = {
                'ssid': ssid,
                'limit': 1
            }
            
            self.logger.debug(f"Querying WiGLE for SSID: {ssid}")
            response = requests.get(
                url,
                params=params,
                headers=headers,
                auth=auth,
                timeout=10
            )
            
            if response.status_code == 200:
                result = self._parse_response(response.json(), ssid)
                
                # Cache result
                if result:
                    self.cache[ssid] = result
                    self.cache_time[ssid] = datetime.now()
                
                return result
            elif response.status_code == 401:
                self.logger.error("WiGLE API authentication failed (invalid API key)")
                self.is_enabled = False
                return None
            elif response.status_code == 403:
                self.logger.error("WiGLE API rate limited")
                return None
            else:
                self.logger.warning(f"WiGLE API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.warning(f"WiGLE API timeout for SSID: {ssid}")
            return None
        except Exception as e:
            self.logger.error(f"Error querying WiGLE: {e}")
            return None
    
    def _parse_response(self, response_data: Dict, ssid: str) -> Optional[SSIDLocation]:
        """
        Parse WiGLE API response.
        
        Args:
            response_data: API response JSON
            ssid: Original SSID searched
            
        Returns:
            SSIDLocation or None
        """
        try:
            # Check if results exist
            if not response_data.get('results'):
                return None
            
            results = response_data['results']
            if not results or len(results) == 0:
                return None
            
            # Get first result
            result = results[0]
            
            # Extract location
            lat = result.get('trilat')
            lon = result.get('trilong')
            
            # Extract other info
            accuracy = result.get('accuracy')
            found_count = result.get('found')
            last_found = result.get('lastupdt')
            
            # Try to identify organization
            org = self._identify_organization(ssid)
            
            return SSIDLocation(
                ssid=ssid,
                latitude=lat,
                longitude=lon,
                accuracy=accuracy,
                found_count=found_count or 0,
                last_found=last_found,
                organization=org
            )
            
        except Exception as e:
            self.logger.debug(f"Error parsing WiGLE response: {e}")
            return None
    
    def _identify_organization(self, ssid: str) -> Optional[str]:
        """
        Try to identify organization from SSID.
        
        Args:
            ssid: SSID string
            
        Returns:
            Organization name or None
        """
        if not ssid:
            return None
        
        ssid_lower = ssid.lower()
        
        # Check for known patterns
        patterns = {
            'starbucks': 'Starbucks',
            'mcdonalds': "McDonald's",
            'airports': 'Airport',
            'hotel': 'Hotel',
            'library': 'Library',
            'airline': 'Airline',
            'hospital': 'Hospital',
            'university': 'University',
            'corporate': 'Corporate',
        }
        
        for pattern, org in patterns.items():
            if pattern in ssid_lower:
                return org
        
        return None
    
    def _apply_rate_limit(self):
        """Apply rate limiting to API requests."""
        # Check if we need to wait
        min_interval = 60.0 / self.rate_limit  # seconds between requests
        elapsed = time.time() - self.last_request_time
        
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            self.logger.debug(f"Rate limiting: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def batch_lookup(self, ssids: List[str]) -> Dict[str, Optional[SSIDLocation]]:
        """
        Look up multiple SSIDs.
        
        Args:
            ssids: List of SSIDs
            
        Returns:
            Dictionary of SSID -> SSIDLocation
        """
        results = {}
        
        for ssid in ssids:
            results[ssid] = self.lookup_ssid(ssid)
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'cached_ssids': len(self.cache),
            'cache_size_kb': sum(
                len(str(v).encode('utf-8')) for v in self.cache.values()
            ) / 1024,
            'enabled': self.is_enabled,
        }
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache.clear()
        self.cache_time.clear()
        self.logger.info("WiGLE cache cleared")
    
    def __repr__(self) -> str:
        """String representation."""
        status = "enabled" if self.is_enabled else "disabled"
        return f"WiGLEClient({status}, cached: {len(self.cache)})"