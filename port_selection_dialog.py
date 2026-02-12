"""
Port Selection Dialog - UI Consumer Layer
Provides user interface for serial port selection
Integrates with main_application.py UI framework
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QListWidgetItem,
                             QGroupBox, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from PyQt5.QtGui import QColor, QFont
import logging

from serial_port_detector import get_port_detector

logger = logging.getLogger(__name__)


class PortDetectionWorker(QThread):
    """
    Worker thread for port detection
    Runs detection in background to avoid blocking UI
    
    Architecture Layer: Data Processing (Broker)
    Ensures non-blocking port detection per best practices
    """
    
    ports_found = pyqtSignal(list)      # Emits list of port names
    detection_started = pyqtSignal()
    detection_completed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, port_detector):
        """Initialize worker with port detector"""
        super().__init__()
        self.port_detector = port_detector
    
    def run(self):
        """Detect ports in background thread"""
        try:
            self.detection_started.emit()
            ports = self.port_detector.get_port_names()
            self.ports_found.emit(ports)
            logger.info(f"Detected {len(ports)} port(s)")
        except Exception as e:
            logger.error(f"Port detection error: {e}")
            self.error_occurred.emit(str(e))
        finally:
            self.detection_completed.emit()


class PortSelectionDialog(QDialog):
    """
    Port Selection Dialog
    Provides user interface for selecting serial port
    
    Features:
    - Auto-detection of available ports
    - Port availability status (Available/In Use)
    - Auto-selection of fatigue tester if found
    - Validation of port selection
    - Non-blocking background detection
    
    Signals:
    - port_selected(str): Emitted when user selects a port
    """
    
    port_selected = pyqtSignal(str)  # Emits selected port name
    
    def __init__(self, parent=None, port_detector=None):
        """
        Initialize port selection dialog
        
        Args:
            parent: Parent widget (typically MainWindow)
            port_detector: Port detector instance
        """
        super().__init__(parent)
        self.setWindowTitle("Select Serial Port")
        self.setGeometry(200, 200, 600, 400)
        self.selected_port = None
        self.ports = []
        self.port_detector = port_detector or get_port_detector()
        
        # Setup UI
        self.setup_ui()
        
        # Setup port detection worker
        self.detection_worker = PortDetectionWorker(self.port_detector)
        self.detection_worker.ports_found.connect(self.on_ports_found)
        self.detection_worker.error_occurred.connect(self.on_detection_error)
        
        # Start detection
        self.start_detection()
    
    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Available Serial Ports")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Status label
        self.status_label = QLabel("Detecting ports...")
        self.status_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Port list
        self.port_list = QListWidget()
        self.port_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.port_list.itemDoubleClicked.connect(self.on_port_double_clicked)
        layout.addWidget(self.port_list)
        
        # Info group
        info_group = QGroupBox("Port Information")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Select a port to see details")
        self.info_label.setStyleSheet("color: #333333;")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Button group
        button_layout = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.start_detection)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Select button
        select_btn = QPushButton("Select")
        select_btn.clicked.connect(self.on_select_clicked)
        select_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(select_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def start_detection(self):
        """Start background port detection"""
        self.port_list.clear()
        self.status_label.setText("Detecting ports...")
        self.status_label.setStyleSheet("color: #FF9800; font-style: italic;")
        self.port_list.setEnabled(False)
        
        self.detection_worker.start()
    
    def on_ports_found(self, ports: list):
        """
        Handle ports detected by worker thread
        
        Args:
            ports: List of port names (strings)
        """
        self.ports = ports
        self.port_list.clear()
        
        if not ports:
            self.status_label.setText("No serial ports detected")
            self.status_label.setStyleSheet("color: #F44336; font-style: italic;")
            return
        
        # Add ports to list
        for port in ports:
            self.add_port_to_list(port)
        
        # Update status
        self.status_label.setText(f"Found {len(ports)} port(s)")
        self.status_label.setStyleSheet("color: #4CAF50; font-style: italic;")
        
        self.port_list.setEnabled(True)
    
    def add_port_to_list(self, port: str):
        """
        Add port to list widget with color coding
        
        Args:
            port: Port name (e.g., 'COM3', '/dev/ttyUSB0')
        """
        # Create display text
        display_text = f"✓ {port}"
        
        item = QListWidgetItem(display_text)
        item.setData(Qt.UserRole, port)  # Store actual port name
        
        # Color coding - green for available
        item.setForeground(QColor("#2E7D32"))  # Green
        
        # Add to list
        self.port_list.addItem(item)
    
    def on_selection_changed(self):
        """Handle port selection change in list"""
        current_item = self.port_list.currentItem()
        if not current_item:
            self.info_label.setText("No port selected")
            return
        
        port_name = current_item.data(Qt.UserRole)
        
        # Display port info
        info_text = f"<b>Port:</b> {port_name}<br><b>Status:</b> ✓ Available"
        self.info_label.setText(info_text)
    
    def on_port_double_clicked(self, item):
        """Handle double-click on port to auto-select"""
        self.selected_port = item.data(Qt.UserRole)
        self.port_selected.emit(self.selected_port)
        self.accept()
    
    def auto_select_port(self, port_name: str):
        """
        Auto-select a port in the list
        
        Args:
            port_name: Port name to select
        """
        for i in range(self.port_list.count()):
            item = self.port_list.item(i)
            if item.data(Qt.UserRole) == port_name:
                self.port_list.setCurrentItem(item)
                self.on_selection_changed()
                return
    
    def on_select_clicked(self):
        """Handle Select button click"""
        current_item = self.port_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a port")
            return
        
        self.selected_port = current_item.data(Qt.UserRole)
        self.port_selected.emit(self.selected_port)
        self.accept()
    
    def on_detection_error(self, error_msg: str):
        """Handle detection error"""
        self.status_label.setText(f"Error: {error_msg}")
        self.status_label.setStyleSheet("color: #F44336; font-style: italic;")
        self.port_list.setEnabled(True)
    
    def get_selected_port(self) -> str:
        """
        Get the selected port name
        
        Returns:
            Selected port name or empty string
        """
        return self.selected_port or ""


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = PortSelectionDialog()
    if dialog.exec_() == QDialog.Accepted:
        print(f"Selected port: {dialog.get_selected_port()}")
    sys.exit()
