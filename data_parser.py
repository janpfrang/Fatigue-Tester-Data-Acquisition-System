"""
Data Parser module for Fatigue Tester
Handles parsing and validation of serial data
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import config


@dataclass
class FatigueTestData:
    """Structured data from fatigue test"""
    timestamp: datetime
    status: str
    cycles: int
    position_1_mm: float
    force_lower_n: float
    travel_1_mm: float
    position_2_mm: float
    force_upper_n: float
    travel_2_mm: float
    travel_at_upper_mm: float
    error_code: int
    raw_data: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for CSV export"""
        return {
            'Timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'Status': self.status,
            'Cycles': self.cycles,
            'Position_1_mm': self.position_1_mm,
            'Force_Lower_N': self.force_lower_n,
            'Travel_1_mm': self.travel_1_mm,
            'Position_2_mm': self.position_2_mm,
            'Force_Upper_N': self.force_upper_n,
            'Travel_2_mm': self.travel_2_mm,
            'Travel_at_Upper_mm': self.travel_at_upper_mm,
            'Loss_of_Stiffness_Percent': self.calculate_loss_of_stiffness(),
            'Error_Code': self.error_code,
            'Error_Description': config.ERROR_CODES.get(self.error_code, "Unknown Error"),
            'Raw_Data': self.raw_data
        }
    
    def calculate_loss_of_stiffness(self) -> float:
        """Calculate loss of stiffness percentage"""
        if self.travel_at_upper_mm == 0:
            return 0.0
        return (self.travel_2_mm / self.travel_at_upper_mm) * 100.0
    
    def is_test_end(self) -> bool:
        """Check if test has ended"""
        return self.status == "END"
    
    def has_error(self) -> bool:
        """Check if there's an error"""
        return self.error_code != 0


class DataParser:
    """Parser for fatigue test serial data"""
    
    def __init__(self):
        self.parse_errors = 0
        
    def parse(self, raw_data: str) -> Optional[FatigueTestData]:
        """
        Parse raw serial data string
        
        Expected format: DTA;31422;182;263;0;793;2238;0;611;0;!
        
        Args:
            raw_data: Raw string from serial port
            
        Returns:
            FatigueTestData object or None if parsing fails
        """
        try:
            # Remove trailing exclamation mark and whitespace
            raw_data = raw_data.strip()
            if raw_data.endswith('!'):
                raw_data = raw_data[:-1]
            
            # Split by semicolon
            parts = raw_data.split(';')
            
            if len(parts) != 11:
                raise ValueError(f"Expected 11 fields, got {len(parts)}")
            
            # Parse each field with proper decimal conversion
            status = parts[0].strip()
            cycles = int(parts[1])
            position_1_mm = int(parts[2]) / 100.0  # Last 2 digits are decimals
            force_lower_n = int(parts[3]) / 10.0    # Last digit is decimal
            travel_1_mm = int(parts[4]) / 100.0 # Last 2 digits are decimals
            position_2_mm = int(parts[5]) / 100.0  # Last 2 digits are decimals
            force_upper_n = int(parts[6]) / 10.0    # Last digit is decimal
            travel_2_mm = int(parts[7]) / 100.0 # Last 2 digits are decimals
            travel_at_upper_mm = int(parts[8]) / 100.0  # Last 2 digits are decimals
            error_code = int(parts[9])
            
            # Create structured data object
            return FatigueTestData(
                timestamp=datetime.now(),
                status=status,
                cycles=cycles,
                position_1_mm=position_1_mm,
                force_lower_n=force_lower_n,
                travel_1_mm=travel_1_mm,
                position_2_mm=position_2_mm,
                force_upper_n=force_upper_n,
                travel_2_mm=travel_2_mm,
                travel_at_upper_mm=travel_at_upper_mm,
                error_code=error_code,
                raw_data=raw_data + '!'
            )
            
        except (ValueError, IndexError) as e:
            self.parse_errors += 1
            print(f"Parse error #{self.parse_errors}: {e} - Data: {raw_data}")
            return None
    
    def validate_data(self, data: FatigueTestData) -> Tuple[bool, str]:
        """
        Validate parsed data for reasonableness
        
        Returns:
            (is_valid, error_message)
        """
        # Basic range checks
        if data.cycles < 0:
            return False, "Invalid cycle count (negative)"
        
        if data.status not in ["DTA", "END"]:
            return False, f"Invalid status: {data.status}"
        
        # Note: Negative values for force and position are allowed per V2 requirements
        # Upper force should typically be greater than lower force (but not enforced strictly)
        
        return True, "OK"
    
    def get_error_description(self, error_code: int) -> str:
        """Get human-readable error description"""
        return config.ERROR_CODES.get(error_code, f"Unknown Error Code: {error_code}")
