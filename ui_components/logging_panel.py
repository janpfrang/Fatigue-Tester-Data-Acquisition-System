"""
Logging Panel UI Component
Handles data logging controls
"""

from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QLabel, QPushButton, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal


class LoggingPanel(QGroupBox):
    """
    Data logging controls panel
    
    Signals:
        save_clicked: User clicked Save Log As button
        new_log_clicked: User clicked Start New Log button
    """
    
    save_clicked = pyqtSignal()
    new_log_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Data Logging", parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout()
        
        # Current log file display
        self.current_log_label = QLabel("No active log file")
        self.current_log_label.setWordWrap(True)
        layout.addWidget(self.current_log_label)
        
        # Buttons
        save_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Log As...")
        self.save_btn.clicked.connect(self.save_clicked.emit)
        self.save_btn.setEnabled(False)
        save_layout.addWidget(self.save_btn)
        
        self.new_log_btn = QPushButton("Start New Log")
        self.new_log_btn.clicked.connect(self.new_log_clicked.emit)
        self.new_log_btn.setEnabled(False)
        save_layout.addWidget(self.new_log_btn)
        
        layout.addLayout(save_layout)
        
        self.setLayout(layout)
    
    def set_log_filename(self, filename: str):
        """Update the current log filename display"""
        if filename:
            self.current_log_label.setText(f"Logging to: {filename}")
        else:
            self.current_log_label.setText("No active log file")
    
    def set_buttons_enabled(self, enabled: bool):
        """Enable or disable the logging buttons"""
        self.save_btn.setEnabled(enabled)
        self.new_log_btn.setEnabled(enabled)
