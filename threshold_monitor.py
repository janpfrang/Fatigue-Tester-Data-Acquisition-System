"""
Threshold Monitor Module
Handles threshold configuration and violation detection for fatigue test data

Part of Phase 2 refactoring - Business Logic Extraction
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ThresholdConfiguration:
    """Configuration for threshold monitoring"""
    # Upper Force thresholds
    upper_force_enabled: bool = False
    upper_force_upper_limit: float = 250.0
    upper_force_lower_limit: float = -1.0
    
    # Loss of Stiffness thresholds
    stiffness_enabled: bool = False
    stiffness_upper_limit: float = 50.0
    stiffness_lower_limit: float = 0.0


class ThresholdMonitor:
    """
    Monitor data for threshold violations
    Tracks violations and provides statistics
    """
    
    def __init__(self, config: Optional[ThresholdConfiguration] = None):
        """
        Initialize threshold monitor
        
        Args:
            config: Threshold configuration (uses defaults if None)
        """
        self.config = config or ThresholdConfiguration()
        
        # Violation counters
        self.force_violations = 0
        self.stiffness_violations = 0
        
        # Violation history (for detailed analysis)
        self.force_violation_cycles = []
        self.stiffness_violation_cycles = []
    
    def update_configuration(self, config: ThresholdConfiguration):
        """
        Update threshold configuration
        
        Args:
            config: New threshold configuration
        """
        self.config = config
    
    def check_upper_force(self, value: float, cycle: int) -> bool:
        """
        Check if upper force value violates thresholds
        
        Args:
            value: Upper force value [N]
            cycle: Current cycle number
            
        Returns:
            True if violation detected, False otherwise
        """
        if not self.config.upper_force_enabled:
            return False
        
        # Check if value is outside the range [lower_limit, upper_limit]
        if value > self.config.upper_force_upper_limit or value < self.config.upper_force_lower_limit:
            self.force_violations += 1
            self.force_violation_cycles.append(cycle)
            return True
        
        return False
    
    def check_stiffness(self, value: float, cycle: int) -> bool:
        """
        Check if loss of stiffness value violates thresholds
        
        Args:
            value: Loss of stiffness value [%]
            cycle: Current cycle number
            
        Returns:
            True if violation detected, False otherwise
        """
        if not self.config.stiffness_enabled:
            return False
        
        # Check if value is outside the range [lower_limit, upper_limit]
        if value > self.config.stiffness_upper_limit or value < self.config.stiffness_lower_limit:
            self.stiffness_violations += 1
            self.stiffness_violation_cycles.append(cycle)
            return True
        
        return False
    
    def check_data(self, data) -> tuple:
        """
        Check a data point for all threshold violations
        
        Args:
            data: FatigueTestData object
            
        Returns:
            Tuple of (force_violation: bool, stiffness_violation: bool)
        """
        force_violation = self.check_upper_force(data.force_upper_n, data.cycles)
        stiffness_violation = self.check_stiffness(
            data.calculate_loss_of_stiffness(), 
            data.cycles
        )
        
        return (force_violation, stiffness_violation)
    
    def get_violation_counts(self) -> tuple:
        """
        Get current violation counts
        
        Returns:
            Tuple of (force_violations: int, stiffness_violations: int)
        """
        return (self.force_violations, self.stiffness_violations)
    
    def get_violation_percentage(self, total_points: int) -> tuple:
        """
        Get violation percentages
        
        Args:
            total_points: Total number of data points
            
        Returns:
            Tuple of (force_percentage: float, stiffness_percentage: float)
        """
        if total_points == 0:
            return (0.0, 0.0)
        
        force_pct = (self.force_violations / total_points) * 100
        stiffness_pct = (self.stiffness_violations / total_points) * 100
        
        return (force_pct, stiffness_pct)
    
    def get_violation_cycles(self) -> tuple:
        """
        Get lists of cycles where violations occurred
        
        Returns:
            Tuple of (force_cycles: list, stiffness_cycles: list)
        """
        return (self.force_violation_cycles.copy(), self.stiffness_violation_cycles.copy())
    
    def reset(self):
        """Reset all violation counters and history"""
        self.force_violations = 0
        self.stiffness_violations = 0
        self.force_violation_cycles.clear()
        self.stiffness_violation_cycles.clear()
    
    def get_statistics(self) -> dict:
        """
        Get comprehensive threshold statistics
        
        Returns:
            Dictionary with all threshold statistics
        """
        return {
            'force_enabled': self.config.upper_force_enabled,
            'force_upper_limit': self.config.upper_force_upper_limit,
            'force_lower_limit': self.config.upper_force_lower_limit,
            'force_violations': self.force_violations,
            'stiffness_enabled': self.config.stiffness_enabled,
            'stiffness_upper_limit': self.config.stiffness_upper_limit,
            'stiffness_lower_limit': self.config.stiffness_lower_limit,
            'stiffness_violations': self.stiffness_violations,
        }
    
    def calculate_advanced_force_analysis(self, force_data: list) -> dict:
        """
        Calculate advanced force analysis (for Advanced Options dialog)
        
        Args:
            force_data: List of upper force values
            
        Returns:
            Dictionary with analysis results
        """
        if not self.config.upper_force_enabled or not force_data:
            return {
                'threshold_103_percentage': 0.0,
                'exceeding_count': 0,
                'total_count': 0,
                'enabled': False
            }
        
        threshold_value = self.config.upper_force_upper_limit * 1.03
        exceeding_count = sum(1 for val in force_data if val > threshold_value)
        total_count = len(force_data)
        percentage = (exceeding_count / total_count * 100) if total_count > 0 else 0
        
        return {
            'threshold_103_percentage': percentage,
            'exceeding_count': exceeding_count,
            'total_count': total_count,
            'threshold_value': threshold_value,
            'enabled': True
        }
