"""
Status Log Panel UI Component
Displays status messages and logs
"""

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit, QPushButton


class StatusLogPanel(QGroupBox):
    """
    Status log display panel
    """
    
    def __init__(self, parent=None):
        super().__init__("Status Log", parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout()
        
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setMaximumHeight(120)
        layout.addWidget(self.status_log)
        
        # Clear log button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(lambda: self.status_log.clear())
        layout.addWidget(clear_btn)
        
        self.setLayout(layout)
    
    def append_message(self, message: str):
        """Append a message to the log"""
        self.status_log.append(message)
    
    def clear(self):
        """Clear the log"""
        self.status_log.clear()
