"""
Connection Panel UI Component
Handles serial connection controls and port selection
"""

from PyQt5.QtWidgets import (QGroupBox, QGridLayout, QLabel, QComboBox, 
                             QPushButton, QCheckBox, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal


class ConnectionPanel(QGroupBox):
    """
    Serial connection settings panel
    
    Signals:
        connect_clicked: User clicked Connect/Disconnect button
        detect_ports_clicked: User clicked Detect Ports button
        port_selected: Port was selected from dialog (port_name: str)
    """
    
    connect_clicked = pyqtSignal()
    detect_ports_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Connection Settings", parent)
        self.is_connected = False
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI layout"""
        layout = QGridLayout()
        
        # Port selection
        layout.addWidget(QLabel("COM Port:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        layout.addWidget(self.port_combo, 0, 1)
        
        # Baudrate selection
        layout.addWidget(QLabel("Baudrate:"), 1, 0)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(['4800', '9600', '19200', '38400', '57600', '115200'])
        layout.addWidget(self.baudrate_combo, 1, 1)
        
        # Buttons (Connect and Detect Ports side by side)
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_clicked.emit)
        button_layout.addWidget(self.connect_btn)
        
        self.list_ports_btn = QPushButton("🔍 Detect Ports")
        self.list_ports_btn.setToolTip("Scan for available COM ports and select one")
        self.list_ports_btn.clicked.connect(self.detect_ports_clicked.emit)
        button_layout.addWidget(self.list_ports_btn)
        
        layout.addLayout(button_layout, 2, 0, 1, 2)
        
        # Mock mode checkbox
        self.mock_mode_check = QCheckBox("Use Mock Data (Testing)")
        layout.addWidget(self.mock_mode_check, 3, 0, 1, 2)
        
        self.setLayout(layout)
    
    def set_connected(self, connected: bool):
        """Update UI based on connection state"""
        self.is_connected = connected
        
        if connected:
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet("background-color: #ffcccc")
        else:
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet("")
        
        self.port_combo.setEnabled(not connected)
        self.baudrate_combo.setEnabled(not connected)
        self.mock_mode_check.setEnabled(not connected)
    
    def add_ports(self, port_names: list):
        """Add ports to dropdown"""
        self.port_combo.clear()
        self.port_combo.addItems(port_names)
    
    def get_port(self) -> str:
        """Get selected port"""
        return self.port_combo.currentText()
    
    def set_port(self, port: str):
        """Set selected port"""
        self.port_combo.setCurrentText(port)
    
    def get_baudrate(self) -> int:
        """Get selected baudrate"""
        return int(self.baudrate_combo.currentText())
    
    def set_baudrate(self, baudrate: int):
        """Set baudrate"""
        self.baudrate_combo.setCurrentText(str(baudrate))
    
    def is_mock_mode(self) -> bool:
        """Check if mock mode is enabled"""
        return self.mock_mode_check.isChecked()
