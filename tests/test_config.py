# tests/test_config.py
"""
Unit tests for configuration module
Tests default values and configuration loading
"""

import unittest
from config import (
    SerialConfig, PlotConfig, LogConfig, 
    WatchdogConfig, ERROR_CODES, DATA_FIELDS
)


class TestSerialConfig(unittest.TestCase):
    """Test serial communication configuration"""
    
    def test_default_port(self):
        """Test default COM port"""
        config = SerialConfig()
        self.assertEqual(config.port, "COM3")
    
    def test_default_baudrate(self):
        """Test default baudrate"""
        config = SerialConfig()
        self.assertEqual(config.baudrate, 9600)
    
    def test_default_timeout(self):
        """Test default timeout"""
        config = SerialConfig()
        self.assertEqual(config.timeout, 1.0)
    
    def test_valid_parity(self):
        """Test parity setting"""
        config = SerialConfig()
        self.assertEqual(config.parity, 'N')  # None


class TestPlotConfig(unittest.TestCase):
    """Test plotting configuration"""
    
    def test_update_interval(self):
        """Test plot update interval"""
        config = PlotConfig()
        self.assertEqual(config.update_interval_ms, 1000)
    
    def test_unlimited_points(self):
        """Test that V2 allows unlimited points"""
        config = PlotConfig()
        # 0 means unlimited (V2 requirement)
        self.assertEqual(config.max_points_display, 0)
    
    def test_auto_range_enabled(self):
        """Test auto-ranging is enabled by default"""
        config = PlotConfig()
        self.assertTrue(config.auto_range)


class TestLogConfig(unittest.TestCase):
    """Test logging configuration"""
    
    def test_base_filename(self):
        """Test default log filename pattern"""
        config = LogConfig()
        self.assertEqual(config.base_filename, "fatigue_test")
    
    def test_file_extension(self):
        """Test log file extension"""
        config = LogConfig()
        self.assertEqual(config.file_extension, ".csv")
    
    def test_timestamp_format(self):
        """Test timestamp format"""
        config = LogConfig()
        # Should be YYYYMMDD_HHMMSS
        self.assertEqual(config.timestamp_format, "%Y%m%d_%H%M%S")


class TestWatchdogConfig(unittest.TestCase):
    """Test watchdog configuration"""
    
    def test_timeout_seconds(self):
        """Test watchdog timeout is 5 seconds"""
        config = WatchdogConfig()
        self.assertEqual(config.timeout_seconds, 5.0)


class TestErrorCodes(unittest.TestCase):
    """Test error code definitions"""
    
    def test_error_code_0_exists(self):
        """Test that error code 0 (no error) is defined"""
        self.assertIn(0, ERROR_CODES)
        self.assertEqual(ERROR_CODES[0], "No Error: Everything is OK")
    
    def test_error_code_11_exists(self):
        """Test that error code 11 is defined"""
        self.assertIn(11, ERROR_CODES)
        self.assertIn("Additional Path 1", ERROR_CODES[11])
    
    def test_motor_error_codes(self):
        """Test motor error codes range"""
        motor_errors = [101, 102, 103, 104, 106, 107]
        for code in motor_errors:
            self.assertIn(code, ERROR_CODES)
            self.assertIn("Motor", ERROR_CODES[code])
    
    def test_all_codes_have_descriptions(self):
        """Test that all error codes have descriptions"""
        for code, description in ERROR_CODES.items():
            self.assertIsNotNone(description)
            self.assertGreater(len(description), 5)


class TestDataFields(unittest.TestCase):
    """Test data field definitions (V2 naming)"""
    
    def test_data_fields_count(self):
        """Test that we have all expected fields"""
        self.assertEqual(len(DATA_FIELDS), 10)
    
    def test_v2_field_names(self):
        """Test that V2 field names are used"""
        self.assertIn("Position_1_mm", DATA_FIELDS)
        self.assertIn("Position_2_mm", DATA_FIELDS)
        self.assertIn("Travel_1_mm", DATA_FIELDS)
        self.assertIn("Travel_2_mm", DATA_FIELDS)
    
    def test_no_v1_field_names(self):
        """Test that old V1 names are not present"""
        self.assertNotIn("Position_0_mm", DATA_FIELDS)
        self.assertNotIn("Position_Upper_mm", DATA_FIELDS)
        self.assertNotIn("Travel_Lower_mm", DATA_FIELDS)
        self.assertNotIn("Travel_Upper_mm", DATA_FIELDS)


if __name__ == '__main__':
    unittest.main()
