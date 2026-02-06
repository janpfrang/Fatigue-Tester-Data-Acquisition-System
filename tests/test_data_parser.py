# tests/test_data_parser.py
"""
Unit tests for data_parser module
Tests the core data parsing functionality
"""

import unittest
from data_parser import DataParser, FatigueTestData


class TestDataParser(unittest.TestCase):
    """Test cases for DataParser class"""
    
    def setUp(self):
        """Create a fresh parser for each test"""
        self.parser = DataParser()
    
    def test_parse_valid_data(self):
        """Test parsing valid serial data"""
        raw = "DTA;31422;182;263;0;793;2238;0;611;0;!"
        result = self.parser.parse(raw)
        
        # Verify parsing succeeded
        self.assertIsNotNone(result)
        
        # Verify field values
        self.assertEqual(result.status, "DTA")
        self.assertEqual(result.cycles, 31422)
        self.assertAlmostEqual(result.position_1_mm, 1.82)
        self.assertAlmostEqual(result.force_lower_n, 26.3)
    
    def test_decimal_conversion(self):
        """Test proper decimal place conversion"""
        raw = "DTA;100;100;100;100;100;100;100;100;0;!"
        result = self.parser.parse(raw)
        
        # 100 ÷ 100 = 1.0 mm
        self.assertAlmostEqual(result.position_1_mm, 1.0)
        
        # 100 ÷ 10 = 10.0 N
        self.assertAlmostEqual(result.force_lower_n, 10.0)
    
    def test_invalid_field_count(self):
        """Test rejection of malformed data"""
        raw = "DTA;100;200;!"  # Too few fields
        result = self.parser.parse(raw)
        
        # Should return None for invalid data
        self.assertIsNone(result)
    
    def test_negative_values_allowed(self):
        """Test that negative values are accepted (V2 requirement)"""
        raw = "DTA;100;-50;-100;-25;200;300;50;600;0;!"
        result = self.parser.parse(raw)
        
        # Should parse successfully
        self.assertIsNotNone(result)
        
        # Verify negative value
        self.assertAlmostEqual(result.position_1_mm, -0.50)
    
    def test_loss_of_stiffness_calculation(self):
        """Test Loss of Stiffness formula: (Travel_2 / Travel_at_Upper) × 100"""
        raw = "DTA;100;100;100;100;100;100;50;200;0;!"
        result = self.parser.parse(raw)
        
        # Calculate: (50 ÷ 100) / (200 ÷ 100) × 100 = 0.5 / 2.0 × 100 = 25%
        loss = result.calculate_loss_of_stiffness()
        self.assertAlmostEqual(loss, 25.0)
    
    def test_loss_of_stiffness_zero_division(self):
        """Test handling of zero travel at upper (avoid division by zero)"""
        raw = "DTA;100;100;100;100;100;100;50;0;0;!"
        result = self.parser.parse(raw)
        
        # Should return 0.0 instead of crashing
        loss = result.calculate_loss_of_stiffness()
        self.assertEqual(loss, 0.0)
    
    def test_is_test_end(self):
        """Test detection of test end status"""
        raw_end = "END;1000;182;263;0;793;2238;0;611;0;!"
        result = self.parser.parse(raw_end)
        
        self.assertTrue(result.is_test_end())
    
    def test_has_error(self):
        """Test detection of error codes"""
        raw_error = "DTA;100;182;263;0;793;2238;0;611;11;!"
        result = self.parser.parse(raw_error)
        
        self.assertTrue(result.has_error())
        self.assertEqual(result.error_code, 11)


if __name__ == '__main__':
    unittest.main()
