"""
Statistics Panel UI Component
Displays real-time statistics
"""

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont


class StatisticsPanel(QGroupBox):
    """
    Statistics display panel
    """
    
    def __init__(self, parent=None):
        super().__init__("Statistics", parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(100)
        font = QFont("Courier New", 9)
        self.stats_text.setFont(font)
        layout.addWidget(self.stats_text)
        
        self.setLayout(layout)
    
    def update_statistics(self, stats_text: str):
        """Update the statistics display"""
        self.stats_text.setPlainText(stats_text)
