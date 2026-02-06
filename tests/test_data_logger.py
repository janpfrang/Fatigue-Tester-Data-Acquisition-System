# tests/test_data_logger.py
"""
Unit tests for data_logger module
Tests CSV file creation and data logging
"""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime

from data_logger import DataLogger
from data_parser import FatigueTestData
from config import LogConfig


class TestDataLogger(unittest.TestCase):
    """Test cases for DataLogger class"""
    
    def setUp(self):
        """Create temp directory and logger for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = LogConfig()
        self.logger = DataLogger(self.config, output_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up temp directory after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_file_creation(self):
        """Test that log files are created with correct naming"""
        log_path = self.logger.start_new_log()
        
        # File should exist
        self.assertTrue(os.path.exists(log_path))
        
        # File should have correct pattern
        filename = os.path.basename(log_path)
        self.assertIn("fatigue_test_", filename)
        self.assertTrue(filename.endswith(".csv"))
    
    def test_no_overwrite(self):
        """Test that existing files are never overwritten"""
        # Create first log
        path1 = self.logger.start_new_log()
        self.logger.close_log()
        
        # Create second log (should not overwrite)
        path2 = self.logger.start_new_log()
        
        # Paths should be different
        self.assertNotEqual(path1, path2)
        
        # Both files should exist
        self.assertTrue(os.path.exists(path1))
        self.assertTrue(os.path.exists(path2))
    
    def test_csv_header(self):
        """Test that CSV has correct header"""
        self.logger.start_new_log()
        
        with open(self.logger.current_file, 'r') as f:
            header = f.readline().strip()
        
        # Verify required columns exist
        required_fields = [
            'Timestamp', 'Status', 'Cycles', 'Position_1_mm',
            'Force_Lower_N', 'Travel_1_mm', 'Loss_of_Stiffness_Percent',
            'Error_Code'
        ]
        
        for field in required_fields:
            self.assertIn(field, header)
    
    def test_log_data_point(self):
        """Test logging a single data point"""
        self.logger.start_new_log()
        
        # Create test data
        data = FatigueTestData(
            timestamp=datetime.now(),
            status="DTA",
            cycles=100,
            position_1_mm=1.5,
            force_lower_n=25.0,
            travel_1_mm=0.1,
            position_2_mm=7.5,
            force_upper_n=200.0,
            travel_2_mm=0.05,
            travel_at_upper_mm=6.0,
            error_code=0,
            raw_data="DTA;100;150;250;10;750;2000;5;600;0;!"
        )
        
        # Log it
        self.logger.log_data(data)
        
        # Verify counter
        self.assertEqual(self.logger.total_points_logged, 1)
    
    def test_statistics(self):
        """Test statistics reporting"""
        stats = self.logger.get_statistics()
        
        self.assertIn('total_points_logged', stats)
        self.assertIn('output_directory', stats)
        self.assertEqual(stats['total_points_logged'], 0)


if __name__ == '__main__':
    unittest.main()
