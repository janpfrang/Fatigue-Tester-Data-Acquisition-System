# tests/test_error_handling.py
"""
Unit tests for error handling and edge cases
"""

import unittest
from data_parser import DataParser, FatigueTestData
from config import ERROR_CODES


class TestParserErrorHandling(unittest.TestCase):
    """Test error handling in data parser"""
    
    def setUp(self):
        self.parser = DataParser()
    
    def test_missing_fields(self):
        """Test handling of missing fields"""
        raw = "DTA;100;200;!"
        result = self.parser.parse(raw)
        self.assertIsNone(result)
    
    def test_extra_fields(self):
        """Test handling of extra fields"""
        raw = "DTA;100;200;300;0;400;500;0;600;0;10;EXTRA;!"
        result = self.parser.parse(raw)
        self.assertIsNone(result)
    
    def test_non_numeric_fields(self):
        """Test handling of non-numeric data"""
        raw = "DTA;ABC;200;300;0;400;500;0;600;0;!"
        result = self.parser.parse(raw)
        self.assertIsNone(result)
    
    def test_empty_string(self):
        """Test handling of empty input"""
        result = self.parser.parse("")
        self.assertIsNone(result)
    
    def test_whitespace_handling(self):
        """Test that parser handles whitespace"""
        raw = "  DTA;31422;182;263;0;793;2238;0;611;0;!  "
        result = self.parser.parse(raw)
        self.assertIsNotNone(result)
    
    def test_missing_end_marker_with_trailing_semicolon(self):
        """Test handling of missing end marker (but with trailing semicolon)"""
        # Note: The format requires a trailing ; to have 11 fields when split
        raw = "DTA;31422;182;263;0;793;2238;0;611;0;"
        result = self.parser.parse(raw)
        # Parser should still work
        self.assertIsNotNone(result)
    
    def test_completely_malformed_data(self):
        """Test handling of completely malformed data"""
        raw = "DTA;31422;182;263;0;793;2238;0;611;0"  # No ! and no trailing ;
        result = self.parser.parse(raw)
        # This should fail - wrong format (only 10 fields)
        self.assertIsNone(result)
    
    def test_invalid_status(self):
        """Test handling of invalid status"""
        raw = "INVALID;100;182;263;0;793;2238;0;611;0;!"
        result = self.parser.parse(raw)
        self.assertIsNotNone(result)  # Parsed, but...
        
        # Validation should catch it
        is_valid, msg = self.parser.validate_data(result)
        self.assertFalse(is_valid)
    
    def test_negative_cycles_rejected(self):
        """Test that negative cycles are rejected"""
        raw = "DTA;-100;182;263;0;793;2238;0;611;0;!"
        result = self.parser.parse(raw)
        self.assertIsNotNone(result)  # Parsed
        
        is_valid, msg = self.parser.validate_data(result)
        self.assertFalse(is_valid)
    
    def test_parse_error_counter(self):
        """Test that parse errors are counted"""
        initial_errors = self.parser.parse_errors
        
        # Send invalid data
        self.parser.parse("INVALID;DATA;!")
        
        # Error counter should increment
        self.assertGreater(self.parser.parse_errors, initial_errors)


class TestDataValidation(unittest.TestCase):
    """Test data validation logic"""
    
    def setUp(self):
        self.parser = DataParser()
    
    def test_valid_data_passes(self):
        """Test that valid data passes validation"""
        raw = "DTA;100;182;263;0;793;2238;0;611;0;!"
        result = self.parser.parse(raw)
        is_valid, msg = self.parser.validate_data(result)
        self.assertTrue(is_valid)
    
    def test_end_status_valid(self):
        """Test that END status is valid"""
        raw = "END;100;182;263;0;793;2238;0;611;0;!"
        result = self.parser.parse(raw)
        is_valid, msg = self.parser.validate_data(result)
        self.assertTrue(is_valid)
    
    def test_zero_cycles_valid(self):
        """Test that zero cycles is valid"""
        raw = "DTA;0;182;263;0;793;2238;0;611;0;!"
        result = self.parser.parse(raw)
        is_valid, msg = self.parser.validate_data(result)
        self.assertTrue(is_valid)


class TestErrorCodeMapping(unittest.TestCase):
    """Test error code to description mapping"""
    
    def test_error_code_0_description(self):
        """Test error code 0 description"""
        desc = ERROR_CODES.get(0)
        self.assertEqual(desc, "No Error: Everything is OK")
    
    def test_error_code_11_description(self):
        """Test error code 11 description"""
        desc = ERROR_CODES.get(11)
        self.assertIsNotNone(desc)
        self.assertIn("Additional Path 1", desc)
    
    def test_all_error_codes_have_descriptions(self):
        """Test that all defined error codes have descriptions"""
        for code in ERROR_CODES.keys():
            desc = ERROR_CODES[code]
            self.assertGreater(len(desc), 0)
    
    def test_unknown_error_code_handling(self):
        """Test handling of unknown error codes"""
        unknown_code = 999
        desc = ERROR_CODES.get(unknown_code, f"Unknown Error Code: {unknown_code}")
        self.assertIsNotNone(desc)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        self.parser = DataParser()
    
    def test_very_large_cycle_number(self):
        """Test handling of very large cycle numbers"""
        raw = "DTA;999999;182;263;0;793;2238;0;611;0;!"
        result = self.parser.parse(raw)
        self.assertIsNotNone(result)
        self.assertEqual(result.cycles, 999999)
    
    def test_zero_force(self):
        """Test handling of zero force"""
        raw = "DTA;100;182;0;0;793;0;0;611;0;!"
        result = self.parser.parse(raw)
        self.assertIsNotNone(result)
        self.assertEqual(result.force_lower_n, 0.0)
    
    def test_maximum_negative_value(self):
        """Test handling of large negative values"""
        raw = "DTA;100;-9999;-9999;-9999;9999;9999;9999;9999;0;!"
        result = self.parser.parse(raw)
        self.assertIsNotNone(result)
        self.assertLess(result.position_1_mm, 0)


if __name__ == '__main__':
    unittest.main()
