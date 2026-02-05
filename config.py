"""
Configuration module for Fatigue Tester Data Acquisition System
Contains all configuration parameters and error codes
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class SerialConfig:
    """Serial communication configuration"""
    port: str = "COM3"
    baudrate: int = 115200
    timeout: float = 1.0
    bytesize: int = 8
    parity: str = 'N'  # None
    stopbits: int = 1


@dataclass
class PlotConfig:
    """Plot configuration"""
    update_interval_ms: int = 1000  # Update plot every 1 second
    max_points_display: int = 0  # 0 = unlimited points (plot all data)
    auto_range: bool = True
    

@dataclass
class LogConfig:
    """Logging configuration"""
    base_filename: str = "fatigue_test"
    file_extension: str = ".csv"
    timestamp_format: str = "%Y%m%d_%H%M%S"
    

@dataclass
class WatchdogConfig:
    """Watchdog configuration"""
    timeout_seconds: float = 5.0  # Alert if no data for 5 seconds
    

# Error code definitions
ERROR_CODES: Dict[int, str] = {
    0: "No Error: Everything is OK",
    10: "Test failed: The test was completed with an error",
    11: "Additional Path 1 Violation: Additional path 1 has exceeded the permissible tolerance",
    12: "Additional Path 2 Violation: Additional path 2 has exceeded the permissible tolerance",
    13: "Force Limit 2 Violation: Force 2 fell below the permissible limit",
    14: "Force Limit 2 Violation: Force 2 exceeded the permissible limit",
    101: "Motor Error: The Voice Coil drive could not be initialized",
    102: "Motor Error: Communication error with the Voice Coil drive",
    103: "Reference Position: No reference position was set using the Zero Point button",
    104: "Motor Error: The Voice Coil drive is not ready",
    106: "Motor Error: The Voice Coil drive was not initialized correctly",
    107: "Motor Error: The Voice Coil drive is blocked",
    201: "Travel Determination: The determined resulting actuation travel is too small",
    202: "Force Search: At the starting point of force search run 1, the specified target force 1 had already been reached",
    203: "Force Search: At the starting point of force search run 2, the specified target force 2 had already been reached",
    204: "Force Search: Target force 1 could not be built up during the force search",
    205: "Force Search: Target force 2 could not be built up during the force search",
}


# Data format specification
DATA_FIELDS = [
    "Status",           # DTA or END
    "Cycles",           # Number of cycles
    "Position_1_mm",    # position 1 in mm (last 2 digits = decimals)
    "Force_Lower_N",    # Lower Force in N (last digit = decimal)
    "Travel_1_mm",      # additional travel 1 to reach Lower Force (last 2 digits = decimals)
    "Position_2_mm",    # position 2 in mm (last 2 digits = decimals)
    "Force_Upper_N",    # Upper Force in N (last digit = decimal)
    "Travel_2_mm",      # additional travel 2 to reach Upper Force (last 2 digits = decimals)
    "Travel_at_Upper_mm", # Travel at Upper Force (last 2 digits = decimals)
    "Error_Code"        # Error code
]
