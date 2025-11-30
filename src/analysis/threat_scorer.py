from typing import List
from data.device import Device


class ThreatScorer:
    """Advanced threat scoring and analysis."""
    
    @staticmethod
    def calculate_proximity_score(rssi_values: List[int]) -> float:
        """
        Calculate proximity score from RSSI values.
        
        Args:
            rssi_values: List of RSSI measurements in dBm
            
        Returns:
            Proximity score (0-100)
        """
        if not rssi_values:
            return 0
        
        avg_rssi = sum(rssi_values) / len(rssi_values)
        
        # Convert RSSI to approximate distance and score
        # RSSI range typically -30 (very close) to -100 (far)
        # Normalize to 0-100 where higher score = closer
        score = max(0, min(100, (avg_rssi + 100) * 1.5))
        
        return score
    
    @staticmethod
    def calculate_persistence_score(detection_count: int,
                                   min_threshold: int = 3) -> float:
        """
        Calculate persistence score based on detection count.
        
        Args:
            detection_count: Number of detections
            min_threshold: Minimum detections to register
            
        Returns:
            Persistence score (0-100)
        """
        if detection_count < min_threshold:
            return 0
        
        # Exponential scoring for higher detections
        score = min(100, 50 + (detection_count - min_threshold) * 5)
        
        return score
    
    @staticmethod
    def calculate_stability_score(location_count: int) -> float:
        """
        Calculate stability score based on location diversity.
        
        Args:
            location_count: Number of different locations
            
        Returns:
            Stability score (0-100)
        """
        if location_count == 0:
            return 100  # Single location = stable
        elif location_count == 1:
            return 80
        elif location_count == 2:
            return 50
        else:
            return 20  # Multiple locations = unstable/following