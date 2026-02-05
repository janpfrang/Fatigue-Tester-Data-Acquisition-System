"""
Data Logger module - Consumer for CSV file operations
Handles logging of test data to CSV files
"""

import os
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import pandas as pd
from config import LogConfig
from data_parser import FatigueTestData


class DataLogger:
    """
    Consumer that logs data to CSV files
    Implements file management and CSV writing
    """
    
    def __init__(self, config: LogConfig, output_dir: str = "./logs"):
        """
        Initialize data logger
        
        Args:
            config: Logging configuration
            output_dir: Directory for log files
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.current_file: Optional[Path] = None
        self.current_filename: Optional[str] = None
        self.data_buffer: List[FatigueTestData] = []
        self.total_points_logged = 0
        
    def start_new_log(self) -> str:
        """
        Start a new log file with timestamp
        Ensures no overwriting of existing files
        
        Returns:
            Path to the new log file
        """
        timestamp = datetime.now().strftime(self.config.timestamp_format)
        base_name = f"{self.config.base_filename}_{timestamp}"
        filename = f"{base_name}{self.config.file_extension}"
        filepath = self.output_dir / filename
        
        # Ensure we don't overwrite existing files
        counter = 1
        while filepath.exists():
            filename = f"{base_name}_{counter:02d}{self.config.file_extension}"
            filepath = self.output_dir / filename
            counter += 1
        
        self.current_file = filepath
        self.current_filename = filename
        
        # Create file with header
        self._write_header()
        
        print(f"[DataLogger] Started new log file: {filename}")
        return str(filepath)
    
    def _write_header(self):
        """Write CSV header to current file"""
        if not self.current_file:
            return
        
        headers = [
            'Timestamp',
            'Status',
            'Cycles',
            'Position_1_mm',
            'Force_Lower_N',
            'Travel_1_mm',
            'Position_2_mm',
            'Force_Upper_N',
            'Travel_2_mm',
            'Travel_at_Upper_mm',
            'Loss_of_Stiffness_Percent',
            'Error_Code',
            'Error_Description',
            'Raw_Data'
        ]
        
        with open(self.current_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def log_data(self, data: FatigueTestData):
        """
        Log a single data point to current file
        
        Args:
            data: Parsed fatigue test data
        """
        if not self.current_file:
            self.start_new_log()
        
        # Add to buffer
        self.data_buffer.append(data)
        
        # Write to file
        self._write_to_file(data)
        
        self.total_points_logged += 1
    
    def _write_to_file(self, data: FatigueTestData):
        """Write single data point to CSV file"""
        if not self.current_file:
            return
        
        try:
            data_dict = data.to_dict()
            
            with open(self.current_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data_dict.keys())
                writer.writerow(data_dict)
                
        except Exception as e:
            print(f"[DataLogger] Error writing to file: {e}")
    
    def save_current_log(self, user_filename: Optional[str] = None) -> Optional[str]:
        """
        Save current log with optional custom filename
        
        Args:
            user_filename: Optional custom filename (without extension)
            
        Returns:
            Path to saved file or None if failed
        """
        if not self.current_file or not self.current_file.exists():
            print("[DataLogger] No active log file to save")
            return None
        
        if user_filename:
            # Create new filename
            new_path = self.output_dir / f"{user_filename}{self.config.file_extension}"
            
            # Ensure no overwriting
            counter = 1
            while new_path.exists():
                new_path = self.output_dir / f"{user_filename}_{counter:02d}{self.config.file_extension}"
                counter += 1
            
            # Copy current file to new location
            try:
                import shutil
                shutil.copy2(self.current_file, new_path)
                print(f"[DataLogger] Saved log as: {new_path.name}")
                return str(new_path)
            except Exception as e:
                print(f"[DataLogger] Error saving file: {e}")
                return None
        
        return str(self.current_file)
    
    def close_log(self):
        """Close current log file"""
        if self.current_file:
            print(f"[DataLogger] Closed log file: {self.current_filename}")
            self.current_file = None
            self.current_filename = None
    
    def get_statistics(self) -> dict:
        """Get logging statistics"""
        return {
            'current_file': self.current_filename,
            'total_points_logged': self.total_points_logged,
            'buffer_size': len(self.data_buffer),
            'output_directory': str(self.output_dir)
        }
    
    def export_to_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Export current buffer to pandas DataFrame
        
        Returns:
            DataFrame with logged data
        """
        if not self.data_buffer:
            return None
        
        data_dicts = [data.to_dict() for data in self.data_buffer]
        return pd.DataFrame(data_dicts)
    
    def get_log_files(self) -> List[str]:
        """Get list of all log files in output directory"""
        if not self.output_dir.exists():
            return []
        
        csv_files = list(self.output_dir.glob(f"*{self.config.file_extension}"))
        return [f.name for f in sorted(csv_files, reverse=True)]
