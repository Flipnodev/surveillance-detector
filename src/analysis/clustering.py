import logging
from typing import List, Dict, Tuple
import numpy as np
from sklearn.cluster import DBSCAN

from data.location import Location, GPSCoordinate


class ClusterAnalyzer:
    """DBSCAN clustering for location-based device tracking."""
    
    def __init__(self, eps_meters: float = 100, min_samples: int = 2,
                 logger: logging.Logger = None):
        """
        Initialize clustering analyzer.
        
        Args:
            eps_meters: Maximum distance between points in meters
            min_samples: Minimum points to form cluster
            logger: Logger instance
        """
        self.eps_meters = eps_meters
        self.min_samples = min_samples
        self.logger = logger or logging.getLogger(__name__)
    
    def cluster_locations(self, locations: List[Location]) -> Dict[int, List[Location]]:
        """
        Cluster locations using DBSCAN.
        
        Args:
            locations: List of Location objects
            
        Returns:
            Dictionary of cluster_id -> list of locations
        """
        if not locations:
            return {}
        
        # Extract coordinates
        coords = np.array([
            (loc.centroid.latitude, loc.centroid.longitude)
            for loc in locations
        ])
        
        # Convert eps from meters to approximate degrees
        # 1 degree latitude ≈ 111 km
        eps_degrees = self.eps_meters / 111000
        
        # Perform DBSCAN clustering
        dbscan = DBSCAN(eps=eps_degrees, min_samples=self.min_samples)
        labels = dbscan.fit_predict(coords)
        
        # Group locations by cluster
        clusters = {}
        for location, label in zip(locations, labels):
            if label == -1:  # Skip noise points
                continue
            
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(location)
        
        self.logger.debug(f"Clustered {len(locations)} locations into {len(clusters)} clusters")
        
        return clusters