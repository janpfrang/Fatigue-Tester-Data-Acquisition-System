"""
Statistics Tracker Module
Handles application statistics tracking and reporting

Part of Phase 2 refactoring - Business Logic Extraction
"""

import time


class StatisticsTracker:
    """
    Track application statistics including connection time,
    data points, parsing statistics, and performance metrics
    """
    
    def __init__(self):
        """Initialize statistics tracker"""
        # Connection tracking
        self.connection_time = None
        self.is_connected = False
        
        # Data tracking
        self.data_points = 0
        
        # Parsing tracking
        self.lines_parsed = 0
        self.lines_skipped = 0
        self.parse_errors = 0
        
        # Performance tracking
        self.last_update_time = time.time()
        self.update_count = 0
    
    def start_connection(self):
        """Start tracking connection time"""
        self.connection_time = time.time()
        self.is_connected = True
    
    def stop_connection(self):
        """Stop connection tracking"""
        self.is_connected = False
    
    def get_connection_duration(self) -> float:
        """
        Get connection duration in seconds
        
        Returns:
            Duration in seconds, or 0 if not connected
        """
        if not self.is_connected or self.connection_time is None:
            return 0.0
        
        return time.time() - self.connection_time
    
    def increment_data_points(self, count: int = 1):
        """
        Increment data points counter
        
        Args:
            count: Number of points to add (default: 1)
        """
        self.data_points += count
        self.update_count += 1
    
    def update_parse_stats(self, parsed: int, skipped: int):
        """
        Update parsing statistics
        
        Args:
            parsed: Number of lines successfully parsed
            skipped: Number of lines skipped (headers, config)
        """
        self.lines_parsed = parsed
        self.lines_skipped = skipped
    
    def increment_parse_errors(self, count: int = 1):
        """
        Increment parse error counter
        
        Args:
            count: Number of errors to add (default: 1)
        """
        self.parse_errors += count
    
    def get_data_rate(self) -> float:
        """
        Calculate data reception rate (points per second)
        
        Returns:
            Data rate in points/second
        """
        duration = self.get_connection_duration()
        if duration <= 0:
            return 0.0
        
        return self.data_points / duration
    
    def reset_data_stats(self):
        """Reset data-related statistics (for plot clearing)"""
        self.data_points = 0
        self.update_count = 0
        self.last_update_time = time.time()
    
    def reset_all(self):
        """Reset all statistics"""
        self.connection_time = None
        self.is_connected = False
        self.data_points = 0
        self.lines_parsed = 0
        self.lines_skipped = 0
        self.parse_errors = 0
        self.update_count = 0
        self.last_update_time = time.time()
    
    def get_summary(self) -> dict:
        """
        Get all statistics as a dictionary
        
        Returns:
            Dictionary with all statistics
        """
        return {
            'is_connected': self.is_connected,
            'connection_duration': self.get_connection_duration(),
            'data_points': self.data_points,
            'lines_parsed': self.lines_parsed,
            'lines_skipped': self.lines_skipped,
            'parse_errors': self.parse_errors,
            'data_rate': self.get_data_rate(),
            'update_count': self.update_count,
        }
    
    def get_formatted_summary(self) -> str:
        """
        Get formatted statistics summary for display
        
        Returns:
            Formatted string with statistics
        """
        stats = self.get_summary()
        
        lines = []
        
        if stats['is_connected']:
            lines.append(f"Connection Time: {stats['connection_duration']:.1f}s")
        else:
            lines.append("Status: Disconnected")
        
        lines.append(f"Data Points: {stats['data_points']}")
        lines.append(f"Lines Parsed: {stats['lines_parsed']}")
        lines.append(f"Lines Skipped: {stats['lines_skipped']}")
        lines.append(f"Parse Errors: {stats['parse_errors']}")
        
        if stats['is_connected'] and stats['connection_duration'] > 0:
            lines.append(f"Data Rate: {stats['data_rate']:.2f} pts/s")
        
        return '\n'.join(lines)
