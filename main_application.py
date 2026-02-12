"""
Main Application - Fatigue Tester Data Acquisition System
Orchestrates all components with PyQt5 GUI

Version 2.2 - February 12, 2026
- Added COM port auto-detection with port selection dialog
- Added header/configuration logging to preserve test traceability
- Updated threshold feature implementation with violation detection
- Complete test metadata preservation in CSV files
"""

import sys
import queue
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QLineEdit, QGroupBox, QTextEdit, QStatusBar,
                             QFileDialog, QMessageBox, QSpinBox, QCheckBox,
                             QGridLayout, QTabWidget)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont
import pyqtgraph as pg

from config import SerialConfig, PlotConfig, LogConfig, WatchdogConfig
from data_parser import DataParser
from serial_reader import SerialReader, MockSerialReader
from data_logger import DataLogger
from live_plotter import LivePlotter
from serial_port_detector import get_port_detector
from port_selection_dialog import PortSelectionDialog


class DataProcessorWorker(QThread):
    """
    Worker thread for processing data from queue
    Implements the broker/processor layer
    """
    
    data_processed = pyqtSignal(object)  # Emits FatigueTestData
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data_queue: queue.Queue, parser: DataParser):
        super().__init__()
        self.data_queue = data_queue
        self.parser = parser
        self.running = False
        
        # Statistics for line filtering
        self.lines_skipped = 0
        self.lines_parsed = 0
    
    def should_parse_line(self, line: str) -> bool:
        """
        Determine if a line should be parsed
        Filters out header and configuration lines
        
        Args:
            line: Raw line from serial/file
            
        Returns:
            True if line should be parsed, False to skip
        """
        line = line.strip()
        
        # Skip empty lines
        if not line:
            return False
        
        # Skip header lines from fatigue tester
        if line.startswith('###'):
            return False
        if line.startswith('For display'):
            return False
        if line.startswith('Loading'):
            return False
        
        # Skip configuration line
        if line.startswith('CNF;'):
            return False
        
        # Parse data lines (DTA) and end markers (END)
        return line.startswith('DTA;') or line.startswith('END;')
        
    def run(self):
        """Process data from queue with intelligent line filtering"""
        self.running = True
        self.status_update.emit("Data processor started")
        
        while self.running:
            try:
                # Get data from queue with timeout
                raw_data = self.data_queue.get(timeout=0.1)
                
                # Filter out header and config lines
                if not self.should_parse_line(raw_data):
                    self.lines_skipped += 1
                    continue  # Skip this line
                
                # Parse data
                parsed_data = self.parser.parse(raw_data)
                
                if parsed_data:
                    # Validate data
                    is_valid, error_msg = self.parser.validate_data(parsed_data)
                    
                    if is_valid:
                        self.lines_parsed += 1
                        # Emit parsed data to consumers
                        self.data_processed.emit(parsed_data)
                    else:
                        self.error_occurred.emit(f"Validation error: {error_msg}")
                        
                    # Check for test end or errors
                    if parsed_data.is_test_end():
                        self.status_update.emit(
                            f"Test ended at cycle {parsed_data.cycles} "
                            f"(Parsed: {self.lines_parsed}, Skipped: {self.lines_skipped})"
                        )
                    
                    if parsed_data.has_error():
                        error_desc = self.parser.get_error_description(parsed_data.error_code)
                        self.error_occurred.emit(f"Test error: {error_desc}")
                
            except queue.Empty:
                continue
            except Exception as e:
                self.error_occurred.emit(f"Processing error: {e}")
    
    def stop(self):
        """Stop the processor and report statistics"""
        self.running = False
        if self.lines_parsed > 0 or self.lines_skipped > 0:
            self.status_update.emit(
                f"Processor stopped - Parsed: {self.lines_parsed}, "
                f"Skipped: {self.lines_skipped} header/config lines"
            )


class WatchdogTimer(QTimer):
    """
    Watchdog timer to detect data reception timeout
    """
    
    timeout_occurred = pyqtSignal(float)
    
    def __init__(self, timeout_seconds: float):
        super().__init__()
        self.timeout_seconds = timeout_seconds
        self.setSingleShot(False)
        self.setInterval(int(timeout_seconds * 1000))
        self.last_data_time = time.time()
        self.timeout.connect(self._check_timeout)
        
    def reset(self):
        """Reset watchdog (call when data is received)"""
        self.last_data_time = time.time()
        
    def _check_timeout(self):
        """Check if timeout has occurred"""
        elapsed = time.time() - self.last_data_time
        if elapsed >= self.timeout_seconds:
            self.timeout_occurred.emit(elapsed)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fatigue Tester Data Acquisition System v2.2")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize configurations
        self.serial_config = SerialConfig()
        self.plot_config = PlotConfig()
        self.log_config = LogConfig()
        self.watchdog_config = WatchdogConfig()
        
        # Initialize components
        self.data_queue = queue.Queue()
        self.parser = DataParser()
        self.logger = DataLogger(self.log_config)
        self.plotter = LivePlotter(self.plot_config)
        
        # Initialize port detector for COM port detection (v2.2)
        self.port_detector = get_port_detector()
        
        # Serial reader (will be created on connect)
        self.serial_reader = None
        self.processor_worker = None
        
        # Watchdog
        self.watchdog = WatchdogTimer(self.watchdog_config.timeout_seconds)
        self.watchdog.timeout_occurred.connect(self.on_watchdog_timeout)
        
        # Statistics
        self.connection_time = None
        self.is_connected = False
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup UI
        self.setup_ui()
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.update_status("Ready")
        
    def setup_menu_bar(self):
        """Setup menu bar with Help and Version menus"""
        menubar = self.menuBar()
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # User Manual action (NEW for v2.0)
        user_manual_action = help_menu.addAction('Serial Data Logger and Plotter - User Manual')
        user_manual_action.triggered.connect(self.show_user_manual)
        
        # Help action
        help_action = help_menu.addAction('Help Documentation')
        help_action.triggered.connect(self.show_help)
        
        # About action
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
        
        # Version menu
        version_menu = menubar.addMenu('Version')
        
        # Version info action
        version_action = version_menu.addAction('Version Information')
        version_action.triggered.connect(self.show_version)
        
        # Advanced Options menu (NEW)
        advanced_menu = menubar.addMenu('Advanced Options')
        
        # Advanced options action
        advanced_action = advanced_menu.addAction('Advanced Settings')
        advanced_action.triggered.connect(self.show_advanced_options)
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Connection settings
        conn_group = self.create_connection_group()
        left_panel.addWidget(conn_group)
        
        # Data logging controls
        log_group = self.create_logging_group()
        left_panel.addWidget(log_group)
        
        # Plot settings
        plot_group = self.create_plot_settings_group()
        left_panel.addWidget(plot_group)
        
        # Statistics display
        stats_group = self.create_statistics_group()
        left_panel.addWidget(stats_group)
        
        # Status log
        status_group = self.create_status_log_group()
        left_panel.addWidget(status_group)
        
        left_panel.addStretch()
        
        # Right panel - Plots
        right_panel = QVBoxLayout()
        
        # Create plot widget
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.setBackground('w')
        self.plotter.setup_plots(self.plot_widget)
        right_panel.addWidget(self.plot_widget)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 3)
        
        # Statistics update timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(1000)  # Update every second
    
    def create_connection_group(self) -> QGroupBox:
        """Create connection settings group with port detection (v2.2)"""
        group = QGroupBox("Connection Settings")
        layout = QGridLayout()
        
        # === PORT SELECTION (ENHANCED WITH AUTO-DETECTION) ===
        layout.addWidget(QLabel("COM Port:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        
        # Auto-detect ports on startup
        try:
            detected_ports = self.port_detector.get_port_names()
            if detected_ports:
                self.port_combo.addItems(detected_ports)
                self.log_status(f"Auto-detected ports: {', '.join(detected_ports)}")
            else:
                # Fallback to defaults if no ports detected
                self.port_combo.addItems(['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                                          'COM6', 'COM7', 'COM8', 'COM9', 'COM10'])
                self.log_status("No ports detected, using default list")
        except Exception as e:
            # Fallback if detection fails completely
            self.log_error(f"Port detection error: {e}")
            self.port_combo.addItems(['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                                      'COM6', 'COM7', 'COM8', 'COM9', 'COM10'])
        
        self.port_combo.setCurrentText(self.serial_config.port)
        layout.addWidget(self.port_combo, 0, 1)
        
        # === BAUDRATE ===
        layout.addWidget(QLabel("Baudrate:"), 1, 0)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(['4800', '9600', '19200', '38400', '57600', '115200'])
        self.baudrate_combo.setCurrentText(str(self.serial_config.baudrate))
        layout.addWidget(self.baudrate_combo, 1, 1)
        
        # === CONNECT AND DETECT PORTS BUTTONS (SIDE BY SIDE) ===
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_btn)
        
        self.list_ports_btn = QPushButton("🔍 Detect Ports")
        self.list_ports_btn.setToolTip("Scan for available COM ports and select one")
        self.list_ports_btn.clicked.connect(self.on_list_ports_clicked)
        button_layout.addWidget(self.list_ports_btn)
        
        layout.addLayout(button_layout, 2, 0, 1, 2)
        
        # === MOCK MODE ===
        self.mock_mode_check = QCheckBox("Use Mock Data (Testing)")
        layout.addWidget(self.mock_mode_check, 3, 0, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def create_logging_group(self) -> QGroupBox:
        """Create data logging group"""
        group = QGroupBox("Data Logging")
        layout = QVBoxLayout()
        
        # Current log file display
        self.current_log_label = QLabel("No active log file")
        self.current_log_label.setWordWrap(True)
        layout.addWidget(self.current_log_label)
        
        # Save button
        save_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Log As...")
        self.save_btn.clicked.connect(self.save_log_file)
        self.save_btn.setEnabled(False)
        save_layout.addWidget(self.save_btn)
        
        # New log button
        self.new_log_btn = QPushButton("Start New Log")
        self.new_log_btn.clicked.connect(self.start_new_log)
        self.new_log_btn.setEnabled(False)
        save_layout.addWidget(self.new_log_btn)
        
        layout.addLayout(save_layout)
        
        group.setLayout(layout)
        return group
    
    def create_plot_settings_group(self) -> QGroupBox:
        """Create plot settings group"""
        group = QGroupBox("Plot Settings")
        layout = QGridLayout()
        
        # Add spacing between rows to prevent overlap of taller widgets (32px)
        layout.setSpacing(8)  # Space between rows and columns
        layout.setRowMinimumHeight(0, 32)   # Ensure each row has minimum height
        
        # Update interval
        layout.addWidget(QLabel("Update Interval (ms):"), 0, 0)
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(100, 5000)
        self.update_interval_spin.setValue(self.plot_config.update_interval_ms)
        self.update_interval_spin.setSingleStep(100)
        self.update_interval_spin.valueChanged.connect(self.on_update_interval_changed)
        # Improve readability
        self.update_interval_spin.setMinimumHeight(28)
        font = self.update_interval_spin.font()
        font.setPointSize(8)
        self.update_interval_spin.setFont(font)
        # Add Qt stylesheet with margin/border spacing for visual separation
        self.update_interval_spin.setStyleSheet(
            "QSpinBox {"
            "  margin: 4px 2px 4px 2px;"
            "  padding: 3px;"
            "  border: 1px solid #cccccc;"
            "  border-radius: 2px;"
            "  background-color: #ffffff;"
            "}"
            "QSpinBox::up-button, QSpinBox::down-button {"
            "  width: 0px;"
            "}"
        )
        layout.addWidget(self.update_interval_spin, 0, 1)
        
        # Auto-range checkbox
        self.auto_range_check = QCheckBox("Auto Range")
        self.auto_range_check.setChecked(self.plot_config.auto_range)
        self.auto_range_check.stateChanged.connect(self.on_auto_range_changed)
        layout.addWidget(self.auto_range_check, 1, 0, 1, 2)
        
        # Clear plots button
        self.clear_plot_btn = QPushButton("Clear Plots")
        self.clear_plot_btn.clicked.connect(self.clear_plots)
        layout.addWidget(self.clear_plot_btn, 2, 0, 1, 2)
        
        # Separator line
        from PyQt5.QtWidgets import QFrame
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 3, 0, 1, 2)
        
        # --- Upper Force Thresholds ---
        layout.addWidget(QLabel("Upper Force Thresholds:"), 4, 0, 1, 2)
        
        # Enable Upper Force thresholds checkbox
        self.upper_force_threshold_check = QCheckBox("Enable Thresholds")
        self.upper_force_threshold_check.stateChanged.connect(self.on_upper_force_threshold_changed)
        layout.addWidget(self.upper_force_threshold_check, 5, 0, 1, 2)
        
        # Upper Force - Upper Limit
        layout.addWidget(QLabel("  Upper Limit [N]:"), 6, 0)
        from PyQt5.QtWidgets import QDoubleSpinBox
        self.upper_force_upper_limit_spin = QDoubleSpinBox()
        self.upper_force_upper_limit_spin.setRange(-99999.0, 99999.0)
        self.upper_force_upper_limit_spin.setValue(1000.0)
        self.upper_force_upper_limit_spin.setDecimals(2)
        self.upper_force_upper_limit_spin.setSingleStep(10.0)
        self.upper_force_upper_limit_spin.valueChanged.connect(self.on_upper_force_threshold_changed)
        self.upper_force_upper_limit_spin.setEnabled(False)
        # Improve readability
        self.upper_force_upper_limit_spin.setMinimumHeight(28)
        font = self.upper_force_upper_limit_spin.font()
        font.setPointSize(8)
        self.upper_force_upper_limit_spin.setFont(font)
        # Add Qt stylesheet with margin/border spacing for visual separation
        self.upper_force_upper_limit_spin.setStyleSheet(
            "QDoubleSpinBox {"
            "  margin: 4px 2px 4px 2px;"
            "  padding: 3px;"
            "  border: 1px solid #cccccc;"
            "  border-radius: 2px;"
            "  background-color: #ffffff;"
            "}"
            "QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {"
            "  width: 0px;"
            "}"
        )
        layout.addWidget(self.upper_force_upper_limit_spin, 6, 1)
        
        # Upper Force - Lower Limit
        layout.addWidget(QLabel("  Lower Limit [N]:"), 7, 0)
        self.upper_force_lower_limit_spin = QDoubleSpinBox()
        self.upper_force_lower_limit_spin.setRange(-99999.0, 99999.0)
        self.upper_force_lower_limit_spin.setValue(-1000.0)
        self.upper_force_lower_limit_spin.setDecimals(2)
        self.upper_force_lower_limit_spin.setSingleStep(10.0)
        self.upper_force_lower_limit_spin.valueChanged.connect(self.on_upper_force_threshold_changed)
        self.upper_force_lower_limit_spin.setEnabled(False)
        # Improve readability
        self.upper_force_lower_limit_spin.setMinimumHeight(28)
        font = self.upper_force_lower_limit_spin.font()
        font.setPointSize(8)
        self.upper_force_lower_limit_spin.setFont(font)
        # Add Qt stylesheet with margin/border spacing for visual separation
        self.upper_force_lower_limit_spin.setStyleSheet(
            "QDoubleSpinBox {"
            "  margin: 4px 2px 4px 2px;"
            "  padding: 3px;"
            "  border: 1px solid #cccccc;"
            "  border-radius: 2px;"
            "  background-color: #ffffff;"
            "}"
            "QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {"
            "  width: 0px;"
            "}"
        )
        layout.addWidget(self.upper_force_lower_limit_spin, 7, 1)
        
        # Separator line
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2, 8, 0, 1, 2)
        
        # --- Loss of Stiffness Thresholds ---
        layout.addWidget(QLabel("Loss of Stiffness Thresholds:"), 9, 0, 1, 2)
        
        # Enable Loss of Stiffness thresholds checkbox
        self.stiffness_threshold_check = QCheckBox("Enable Thresholds")
        self.stiffness_threshold_check.stateChanged.connect(self.on_stiffness_threshold_changed)
        layout.addWidget(self.stiffness_threshold_check, 10, 0, 1, 2)
        
        # Loss of Stiffness - Upper Limit
        layout.addWidget(QLabel("  Upper Limit [%]:"), 11, 0)
        self.stiffness_upper_limit_spin = QDoubleSpinBox()
        self.stiffness_upper_limit_spin.setRange(-99999.0, 99999.0)
        self.stiffness_upper_limit_spin.setValue(100.0)
        self.stiffness_upper_limit_spin.setDecimals(2)
        self.stiffness_upper_limit_spin.setSingleStep(1.0)
        self.stiffness_upper_limit_spin.valueChanged.connect(self.on_stiffness_threshold_changed)
        self.stiffness_upper_limit_spin.setEnabled(False)
        # Improve readability
        self.stiffness_upper_limit_spin.setMinimumHeight(28)
        font = self.stiffness_upper_limit_spin.font()
        font.setPointSize(8)
        self.stiffness_upper_limit_spin.setFont(font)
        # Add Qt stylesheet with margin/border spacing for visual separation
        self.stiffness_upper_limit_spin.setStyleSheet(
            "QDoubleSpinBox {"
            "  margin: 4px 2px 4px 2px;"
            "  padding: 3px;"
            "  border: 1px solid #cccccc;"
            "  border-radius: 2px;"
            "  background-color: #ffffff;"
            "}"
            "QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {"
            "  width: 0px;"
            "}"
        )
        layout.addWidget(self.stiffness_upper_limit_spin, 11, 1)
        
        # Loss of Stiffness - Lower Limit
        layout.addWidget(QLabel("  Lower Limit [%]:"), 12, 0)
        self.stiffness_lower_limit_spin = QDoubleSpinBox()
        self.stiffness_lower_limit_spin.setRange(-99999.0, 99999.0)
        self.stiffness_lower_limit_spin.setValue(0.0)
        self.stiffness_lower_limit_spin.setDecimals(2)
        self.stiffness_lower_limit_spin.setSingleStep(1.0)
        self.stiffness_lower_limit_spin.valueChanged.connect(self.on_stiffness_threshold_changed)
        self.stiffness_lower_limit_spin.setEnabled(False)
        # Improve readability
        self.stiffness_lower_limit_spin.setMinimumHeight(28)
        font = self.stiffness_lower_limit_spin.font()
        font.setPointSize(8)
        self.stiffness_lower_limit_spin.setFont(font)
        # Add Qt stylesheet with margin/border spacing for visual separation
        self.stiffness_lower_limit_spin.setStyleSheet(
            "QDoubleSpinBox {"
            "  margin: 4px 2px 4px 2px;"
            "  padding: 3px;"
            "  border: 1px solid #cccccc;"
            "  border-radius: 2px;"
            "  background-color: #ffffff;"
            "}"
            "QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {"
            "  width: 0px;"
            "}"
        )
        layout.addWidget(self.stiffness_lower_limit_spin, 12, 1)
        
        # Set column stretch factors for proper layout at all window sizes
        # Column 0 (labels): Fixed width - don't expand with window
        layout.setColumnStretch(0, 0)
        layout.setColumnMinimumWidth(0, 140)  # Minimum width for label text
        
        # Column 1 (input fields): Flexible - expand to fill available space
        layout.setColumnStretch(1, 1)
        
        group.setLayout(layout)
        return group
    
    def create_statistics_group(self) -> QGroupBox:
        """Create statistics display group"""
        group = QGroupBox("Statistics")
        layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(100)
        font = QFont("Courier New", 9)
        self.stats_text.setFont(font)
        layout.addWidget(self.stats_text)
        
        group.setLayout(layout)
        return group
    
    def create_status_log_group(self) -> QGroupBox:
        """Create status log group"""
        group = QGroupBox("Status Log")
        layout = QVBoxLayout()
        
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setMaximumHeight(120)
        layout.addWidget(self.status_log)
        
        # Clear log button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(lambda: self.status_log.clear())
        layout.addWidget(clear_btn)
        
        group.setLayout(layout)
        return group
    
    def toggle_connection(self):
        """Toggle serial connection"""
        if self.is_connected:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def on_list_ports_clicked(self):
        """
        Handle 'Detect Ports' button click.
        Opens port selection dialog (v2.2).
        """
        self.log_status("User clicked 'Detect Ports' button")
        
        # Create and show port selection dialog
        dialog = PortSelectionDialog(self, self.port_detector)
        dialog.port_selected.connect(self.on_port_selected)
        dialog.exec_()
    
    def on_port_selected(self, port_name: str):
        """
        Handle port selection from dialog.
        Updates combo box and status (v2.2).
        
        Args:
            port_name: Selected port name (e.g., 'COM3', '/dev/ttyUSB0')
        """
        self.log_status(f"Port selected from dialog: {port_name}")
        
        # Update combo box with selected port
        self.port_combo.setCurrentText(port_name)
        
        # Update status bar
        self.update_status(f"Selected port: {port_name}")
    
    def connect_serial(self):
        """Connect to serial port or start mock reader"""
        try:
            # Update configuration from UI
            self.serial_config.port = self.port_combo.currentText()
            self.serial_config.baudrate = int(self.baudrate_combo.currentText())
            
            # Create data processor
            self.processor_worker = DataProcessorWorker(self.data_queue, self.parser)
            self.processor_worker.data_processed.connect(self.on_data_received)
            self.processor_worker.status_update.connect(self.log_status)
            self.processor_worker.error_occurred.connect(self.log_error)
            self.processor_worker.start()
            
            # Create serial reader or mock reader
            if self.mock_mode_check.isChecked():
                self.serial_reader = MockSerialReader(
                    self.data_queue,
                    interval=0.5,
                    status_callback=self.log_status
                )
                self.serial_reader.start()
                success = True
            else:
                self.serial_reader = SerialReader(
                    self.serial_config,
                    self.data_queue,
                    status_callback=self.log_status
                )
                success = self.serial_reader.connect()
                if success:
                    self.serial_reader.start()
            
            if success:
                self.is_connected = True
                self.connection_time = time.time()
                self.connect_btn.setText("Disconnect")
                self.connect_btn.setStyleSheet("background-color: #ffcccc")
                self.port_combo.setEnabled(False)
                self.baudrate_combo.setEnabled(False)
                self.mock_mode_check.setEnabled(False)
                
                # Start logger
                log_file = self.logger.start_new_log()
                self.current_log_label.setText(f"Logging to: {self.logger.current_filename}")
                self.save_btn.setEnabled(True)
                self.new_log_btn.setEnabled(True)
                
                # Start plotter
                self.plotter.start_plotting()
                
                # Start watchdog
                self.watchdog.start()
                
                self.update_status("Connected and logging")
                self.log_status("System connected and running")
            else:
                self.log_error("Failed to connect")
                
        except Exception as e:
            self.log_error(f"Connection error: {e}")
            QMessageBox.critical(self, "Connection Error", str(e))
    
    def disconnect_serial(self):
        """Disconnect from serial port"""
        try:
            # Stop watchdog
            self.watchdog.stop()
            
            # Stop plotter
            self.plotter.stop_plotting()
            
            # Stop serial reader
            if self.serial_reader:
                if isinstance(self.serial_reader, SerialReader):
                    self.serial_reader.disconnect()
                else:
                    self.serial_reader.stop()
                self.serial_reader = None
            
            # Stop processor
            if self.processor_worker:
                self.processor_worker.stop()
                self.processor_worker.wait()
                self.processor_worker = None
            
            # Close logger
            self.logger.close_log()
            
            self.is_connected = False
            self.connect_btn.setText("Connect")
            self.connect_btn.setStyleSheet("")
            self.port_combo.setEnabled(True)
            self.baudrate_combo.setEnabled(True)
            self.mock_mode_check.setEnabled(True)
            
            self.update_status("Disconnected")
            self.log_status("System disconnected")
            
        except Exception as e:
            self.log_error(f"Disconnect error: {e}")
    
    def on_data_received(self, data):
        """Handle received and parsed data"""
        # Reset watchdog
        self.watchdog.reset()
        
        # Log data
        self.logger.log_data(data)
        
        # Add to plotter
        self.plotter.add_data(data)
        
        # Check for errors
        if data.has_error():
            error_desc = self.parser.get_error_description(data.error_code)
            self.log_error(f"Cycle {data.cycles}: {error_desc}")
    
    
    def on_watchdog_timeout(self, elapsed):
        """Handle watchdog timeout"""
        self.log_error(f"No data received for {elapsed:.1f} seconds!")
        self.update_status(f"WARNING: No data for {elapsed:.1f}s")
    
    def save_log_file(self):
        """Save current log file with custom name"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log File",
            str(self.logger.output_dir / "fatigue_test.csv"),
            "CSV Files (*.csv)"
        )
        
        if filename:
            # Extract filename without path and extension
            import os
            base_name = os.path.splitext(os.path.basename(filename))[0]
            saved_path = self.logger.save_current_log(base_name)
            if saved_path:
                QMessageBox.information(self, "Success", f"Log saved to:\n{saved_path}")
    
    def start_new_log(self):
        """Start a new log file"""
        reply = QMessageBox.question(
            self,
            "New Log File",
            "Start a new log file? Current log will be closed.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logger.close_log()
            log_file = self.logger.start_new_log()
            self.current_log_label.setText(f"Logging to: {self.logger.current_filename}")
            self.log_status(f"Started new log: {self.logger.current_filename}")
    
    def clear_plots(self):
        """Clear all plot data"""
        self.plotter.clear_plots()
        self.log_status("Plots cleared")
    
    def on_update_interval_changed(self, value):
        """Handle plot update interval change"""
        self.plotter.set_update_interval(value)
    
    def on_auto_range_changed(self, state):
        """Handle auto-range checkbox change"""
        self.plotter.enable_auto_range(state == Qt.Checked)
    
    def on_upper_force_threshold_changed(self):
        """Handle Upper Force threshold changes"""
        enabled = self.upper_force_threshold_check.isChecked()
        
        # Enable/disable spin boxes
        self.upper_force_upper_limit_spin.setEnabled(enabled)
        self.upper_force_lower_limit_spin.setEnabled(enabled)
        
        # Get values
        upper_limit = self.upper_force_upper_limit_spin.value()
        lower_limit = self.upper_force_lower_limit_spin.value()
        
        # Update plotter
        self.plotter.set_upper_force_thresholds(upper_limit, lower_limit, enabled)
        
        if enabled:
            self.log_status(f"Upper Force thresholds enabled: [{lower_limit}, {upper_limit}] N")
        else:
            self.log_status("Upper Force thresholds disabled")
    
    def on_stiffness_threshold_changed(self):
        """Handle Loss of Stiffness threshold changes"""
        enabled = self.stiffness_threshold_check.isChecked()
        
        # Enable/disable spin boxes
        self.stiffness_upper_limit_spin.setEnabled(enabled)
        self.stiffness_lower_limit_spin.setEnabled(enabled)
        
        # Get values
        upper_limit = self.stiffness_upper_limit_spin.value()
        lower_limit = self.stiffness_lower_limit_spin.value()
        
        # Update plotter
        self.plotter.set_stiffness_thresholds(upper_limit, lower_limit, enabled)
        
        if enabled:
            self.log_status(f"Stiffness thresholds enabled: [{lower_limit}, {upper_limit}] %")
        else:
            self.log_status("Stiffness thresholds disabled")
    
    def update_statistics(self):
        """Update statistics display"""
        stats = []
        
        # Connection statistics
        if self.is_connected:
            elapsed = time.time() - self.connection_time
            stats.append(f"Connection Time: {elapsed:.1f}s")
        else:
            stats.append("Status: Disconnected")
        
        # Serial reader statistics
        if self.serial_reader:
            reader_stats = self.serial_reader.get_statistics() if hasattr(self.serial_reader, 'get_statistics') else {}
            if 'lines_received' in reader_stats:
                stats.append(f"Lines Received: {reader_stats['lines_received']}")
        
        # Logger statistics
        logger_stats = self.logger.get_statistics()
        stats.append(f"Points Logged: {logger_stats['total_points_logged']}")
        
        # Plotter statistics
        plotter_stats = self.plotter.get_statistics()
        stats.append(f"Points Plotted: {plotter_stats['points_plotted']}")
        stats.append(f"Buffer Size: {plotter_stats['buffer_size']}")
        
        # Threshold violations
        if plotter_stats['upper_force_thresholds_enabled']:
            total_points = plotter_stats['points_plotted']
            violations = plotter_stats['upper_force_violations']
            stats.append(f"Upper Force Violations: {violations} / {total_points}")
        
        if plotter_stats['stiffness_thresholds_enabled']:
            total_points = plotter_stats['points_plotted']
            violations = plotter_stats['stiffness_violations']
            stats.append(f"Stiffness Violations: {violations} / {total_points}")
        
        # Parser statistics
        stats.append(f"Parse Errors: {self.parser.parse_errors}")
        
        self.stats_text.setText('\n'.join(stats))
    
    def log_status(self, message: str):
        """Log status message"""
        timestamp = time.strftime("%H:%M:%S")
        # Only log if status_log has been created
        if hasattr(self, 'status_log') and self.status_log:
            self.status_log.append(f"[{timestamp}] {message}")
        else:
            print(f"[{timestamp}] {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        timestamp = time.strftime("%H:%M:%S")
        # Only log if status_log has been created
        if hasattr(self, 'status_log') and self.status_log:
            self.status_log.append(f"[{timestamp}] <span style='color: red;'><b>ERROR:</b> {message}</span>")
        else:
            print(f"[{timestamp}] ERROR: {message}")
    
    def update_status(self, message: str):
        """Update status bar"""
        self.statusBar.showMessage(message)
    
    def show_help(self):
        """Show help documentation for v2.2"""
        help_text = """
<h2>Fatigue Tester Data Acquisition System v2.2 - Help</h2>

<h3>Quick Start (5 Minutes)</h3>
<ol>
<li><b>Connect to Hardware:</b>
   <ul>
   <li>Click "Detect Ports" button to find available COM ports</li>
   <li>Select the COM port from the dialog</li>
   <li>Verify baudrate is set to 115200</li>
   <li>Click "Connect" button</li>
   </ul>
</li>
<li><b>Testing Without Hardware:</b>
   <ul>
   <li>Check "Use Mock Data (Testing)" checkbox</li>
   <li>Click "Connect" to see simulated test data</li>
   <li>All features work identically with mock data</li>
   </ul>
</li>
<li><b>Data is automatically logged:</b>
   <ul>
   <li>CSV file created in logs/ directory with timestamp</li>
   <li>Includes device headers and all test data</li>
   <li>Never overwrites existing files</li>
   </ul>
</li>
</ol>

<h3>Three Real-Time Plots</h3>
<ul>
<li><b>Plot 1 - Forces vs Cycles:</b>
   <ul>
   <li>Blue line: Lower Force [N]</li>
   <li>Red line: Upper Force [N]</li>
   </ul>
</li>
<li><b>Plot 2 - Travel Measurements vs Cycles:</b>
   <ul>
   <li>Green line: Travel at Upper Force [mm]</li>
   <li>Cyan line: Additional Travel 1 [mm]</li>
   <li>Magenta line: Additional Travel 2 [mm]</li>
   </ul>
</li>
<li><b>Plot 3 - Loss of Stiffness vs Cycles:</b>
   <ul>
   <li>Orange line: Loss of Stiffness [%]</li>
   <li>Calculated as: (Travel_2 / Travel_at_Upper) Ã— 100</li>
   </ul>
</li>
</ul>

<h3>Threshold Monitoring (New in v2.2)</h3>
<p>Monitor critical parameters with automatic violation detection:</p>
<ul>
<li><b>Upper Force Thresholds:</b>
   <ul>
   <li>Set Upper and Lower limits [N]</li>
   <li>Enable to activate monitoring</li>
   <li>Out-of-range points highlighted in red</li>
   </ul>
</li>
<li><b>Loss of Stiffness Thresholds:</b>
   <ul>
   <li>Set Upper and Lower limits [%]</li>
   <li>Enable to activate monitoring</li>
   <li>Out-of-range points highlighted in orange</li>
   </ul>
</li>
<li><b>Real-time Statistics:</b>
   <ul>
   <li>Violation count displayed automatically</li>
   <li>Updates as new data arrives</li>
   </ul>
</li>
</ul>

<h3>Plot Controls</h3>
<ul>
<li><b>Update Interval [ms]:</b> How often plots refresh (100-5000 ms, default 1000)</li>
<li><b>Auto Range:</b> Automatically adjust axes to show all data</li>
<li><b>Clear Plots:</b> Remove displayed data (does not affect logged CSV)</li>
</ul>

<h3>Data Logging Features (v2.2)</h3>
<ul>
<li><b>Automatic File Creation:</b>
   <ul>
   <li>Files named: fatigue_test_YYYYMMDD_HHMMSS.csv</li>
   <li>Located in: logs/ subdirectory</li>
   </ul>
</li>
<li><b>Complete Header Logging:</b>
   <ul>
   <li>Device identification (ID, model)</li>
   <li>Display information</li>
   <li>Configuration parameters (CNF line)</li>
   <li>Written as comments at top of CSV</li>
   </ul>
</li>
<li><b>Test Traceability:</b>
   <ul>
   <li>Device ID preserved for audit trail</li>
   <li>Setup parameters enable test reproducibility</li>
   <li>Standard CSV comment format (# prefix)</li>
   <li>Compatible with Excel, MATLAB, Python, pandas</li>
   </ul>
</li>
<li><b>Save As Option:</b>
   <ul>
   <li>Save current log with custom filename</li>
   <li>Original log continues running</li>
   </ul>
</li>
<li><b>Start New Log:</b>
   <ul>
   <li>Close current log and start fresh file</li>
   <li>Useful for multi-part tests</li>
   </ul>
</li>
</ul>

<h3>Serial Port Detection (v2.2)</h3>
<ul>
<li><b>Auto-Detection:</b> System automatically finds available COM ports on startup</li>
<li><b>Port Selection Dialog:</b> Click "Detect Ports" for interactive port chooser</li>
<li><b>Port Status:</b> Shows which ports are available (can be opened)</li>
<li><b>Fallback:</b> Manual entry supported if auto-detection fails</li>
</ul>

<h3>Statistics Panel</h3>
<p>Real-time monitoring of system operation:</p>
<ul>
<li><b>Connection Time:</b> Elapsed time since connection</li>
<li><b>Lines Received:</b> Total raw serial data lines</li>
<li><b>Points Logged:</b> Successfully parsed data points in CSV</li>
<li><b>Points Plotted:</b> Data points currently displayed</li>
<li><b>Parse Errors:</b> Malformed data rejected</li>
<li><b>Threshold Violations:</b> When thresholds enabled</li>
</ul>

<h3>Troubleshooting</h3>
<ul>
<li><b>Connection Failed:</b>
   <ul>
   <li>Check COM port is available (not used by other software)</li>
   <li>Verify baudrate matches equipment (usually 115200)</li>
   <li>Try clicking "Detect Ports" to find correct port</li>
   <li>Check cable connection</li>
   </ul>
</li>
<li><b>No Data Received:</b>
   <ul>
   <li>Verify equipment is powered on and transmitting</li>
   <li>Check cable connections</li>
   <li>Try different baudrates (9600, 38400, 57600, 115200)</li>
   <li>Consult equipment manual for settings</li>
   </ul>
</li>
<li><b>Watchdog Timeout Warning:</b>
   <ul>
   <li>Message: "No data received for X seconds!"</li>
   <li>Indicates connection loss or test stopped</li>
   <li>Check equipment status</li>
   <li>Verify cable integrity</li>
   </ul>
</li>
<li><b>Parse Errors:</b>
   <ul>
   <li>Usually indicates baudrate mismatch</li>
   <li>Check Raw_Data column in CSV to see actual received data</li>
   <li>Try different baudrates</li>
   </ul>
</li>
</ul>

<h3>CSV File Format</h3>
<p>Logged CSV files contain three sections:</p>
<ol>
<li><b>Header Section (Comments):</b> Device info, configuration parameters</li>
<li><b>Column Header Row:</b> Field names (Timestamp, Status, Cycles, etc.)</li>
<li><b>Data Rows:</b> One row per cycle with timestamp</li>
</ol>

<h3>Loss of Stiffness Calculation</h3>
<p><code>Loss of Stiffness [%] = (Travel_2 / Travel_at_Upper) Ã— 100</code></p>
<ul>
<li>Indicates material degradation during fatigue test</li>
<li>Increasing trend shows cumulative fatigue damage</li>
<li>Automatically calculated for each data point</li>
<li>Included in CSV export</li>
</ul>

<h3>Data Format (Serial)</h3>
<p>Expected format from fatigue tester:</p>
<p><code>DTA;31422;182;263;0;793;2238;0;611;0;!</code></p>
<ul>
<li>11 semicolon-separated fields</li>
<li>Ending with exclamation mark (!)</li>
<li>Automatically parsed and converted</li>
<li>Supports negative values</li>
</ul>

<h3>Features in v2.2</h3>
<ul>
<li>âœ“ Complete header/configuration logging</li>
<li>âœ“ Test traceability with device ID preservation</li>
<li>âœ“ Threshold monitoring with violation detection</li>
<li>âœ“ COM port auto-detection</li>
<li>âœ“ Intelligent line filtering (no parse errors)</li>
<li>âœ“ Three synchronized real-time plots</li>
<li>âœ“ Unlimited data points</li>
<li>âœ“ Negative value support</li>
<li>âœ“ Watchdog connection monitoring</li>
<li>âœ“ Mock data mode for testing</li>
<li>âœ“ Professional CSV format</li>
<li>âœ“ Comprehensive Help and User Manual</li>
</ul>

<h3>For More Information</h3>
<p>See "Serial Data Logger and Plotter - User Manual" in Help menu for complete documentation.</p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Help - Fatigue Tester v2.2")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_user_manual(self):
        """Show Serial Data Logger and Plotter User Manual (v2.2)"""
        # Load user manual from external HTML file
        import os
        manual_path = os.path.join(os.path.dirname(__file__), 'USER_MANUAL_V22.html')
        
        try:
            with open(manual_path, 'r', encoding='utf-8') as f:
                manual_html = f.read()
            
            # Create a dialog with a text browser for better HTML rendering
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("User Manual - Serial Data Logger and Plotter v2.2")
            dialog.setGeometry(100, 100, 900, 700)
            
            layout = QVBoxLayout()
            
            # Text browser for HTML content
            browser = QTextBrowser()
            browser.setHtml(manual_html)
            browser.setOpenExternalLinks(True)
            layout.addWidget(browser)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec_()
            
        except FileNotFoundError:
            # Fallback if file not found
            QMessageBox.warning(
                self,
                "User Manual Not Found",
                f"Could not find USER_MANUAL_V22.html in application directory.\n\n"
                f"Expected location: {manual_path}\n\n"
                f"Please ensure the file is present in the same directory as the application."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading User Manual",
                f"An error occurred while loading the user manual:\n\n{str(e)}"
            )
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
<h2>Fatigue Tester Data Acquisition System</h2>
<p><b>Version:</b> 2.2 (February 12, 2026)</p>
<p><b>Requirements:</b> V2.2 (Header Logging and Threshold Features)</p>
<p><b>Contact:</b> Uwe Hasenstab and Alexander Waal</p>

<p>A professional data acquisition system for fatigue testing equipment with 
real-time visualization, comprehensive data logging, and test traceability.</p>

<h3>Version 2.2 Features:</h3>
<ul>
<li>Complete header and configuration logging for test traceability</li>
<li>Device ID and setup parameters preserved in every CSV file</li>
<li>Threshold monitoring for Upper Force and Loss of Stiffness</li>
<li>Real-time violation detection and visualization</li>
<li>COM port auto-detection with port selection dialog</li>
<li>Intelligent line filtering (no header parse errors)</li>
<li>Professional CSV format with comment-based metadata</li>
</ul>

<h3>Key Features:</h3>
<ul>
<li>Real-time serial data acquisition (0.1 - 1.0s intervals)</li>
<li>Three synchronized real-time plots with auto-ranging</li>
<li>Automatic CSV logging with timestamp-based naming</li>
<li>Loss of stiffness calculation and monitoring</li>
<li>Watchdog timer for connection monitoring</li>
<li>Mock data mode for testing without hardware</li>
<li>Unlimited data points (no artificial limits)</li>
<li>Negative value support for force and position</li>
<li>Comprehensive Help menu and User Manual</li>
</ul>

<h3>Architecture:</h3>
<p>Layered, event-driven design using the Producer-Consumer pattern 
with thread-safe communication and hardware abstraction.</p>

<h3>Technology Stack:</h3>
<ul>
<li>Python 3.8+</li>
<li>PyQt5 (GUI Framework)</li>
<li>PyQtGraph (Real-time Plotting)</li>
<li>pyserial (Serial Communication)</li>
<li>pandas (Data Management)</li>
<li>numpy (Numerical Operations)</li>
</ul>

<p style="margin-top: 20px;"><i>For detailed documentation, see USER_MANUAL_V22.html</i></p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About - Fatigue Tester v2.2")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_version(self):
        """Show version information for v2.2"""
        version_text = """
<h2>Version Information - Fatigue Tester v2.2</h2>

<table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: #3498db; color: white;">
    <td><b>Application</b></td>
    <td>Fatigue Tester Data Acquisition System</td>
</tr>
<tr>
    <td><b>Current Version</b></td>
    <td>2.2</td>
</tr>
<tr>
    <td><b>Release Date</b></td>
    <td>February 12, 2026</td>
</tr>
<tr>
    <td><b>Requirements</b></td>
    <td>SRS V2.1 (Updated 09 Feb 2026)</td>
</tr>
<tr>
    <td><b>Status</b></td>
    <td>âœ“ Stable and Ready</td>
</tr>
</table>

<h3>Module Versions (v2.2):</h3>
<ul>
<li><b>Main Application:</b> V2.2 - COM port detection, threshold features, header logging</li>
<li><b>Configuration Module:</b> V2 - Field naming, baudrate 115200</li>
<li><b>Data Parser:</b> V2 - Negative values, Loss of Stiffness calculation</li>
<li><b>Live Plotter:</b> V2 - Three plots, unlimited points, threshold visualization</li>
<li><b>Data Logger:</b> V2.2 - Header/configuration logging, test traceability</li>
<li><b>Serial Reader:</b> V1.0 - RS-232 communication with mock support</li>
<li><b>Port Detector:</b> V1.0 - Cross-platform COM port detection</li>
<li><b>Port Selection Dialog:</b> V1.0 - User-friendly port selection UI</li>
</ul>

<h3>Version History:</h3>
<table border="1" cellpadding="6" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: #ecf0f1;">
    <td><b>Version</b></td>
    <td><b>Date</b></td>
    <td><b>Major Changes</b></td>
</tr>
<tr>
    <td><b>2.0</b></td>
    <td>Feb 5, 2026</td>
    <td>Field naming, three plots, Loss of Stiffness, negative values, unlimited points</td>
</tr>
<tr>
    <td><b>2.1</b></td>
    <td>Feb 9, 2026</td>
    <td>Line filtering, parse error elimination, statistics tracking</td>
</tr>
<tr>
    <td><b>2.2</b></td>
    <td>Feb 9, 2026</td>
    <td>Header logging, threshold features, port auto-detection, metadata preservation</td>
</tr>
</table>

<h3>Key Features in v2.2:</h3>
<ul>
<li>âœ“ Header/configuration logging (device ID, setup parameters)</li>
<li>âœ“ Complete test traceability with metadata in CSV</li>
<li>âœ“ Threshold monitoring (Upper Force and Loss of Stiffness)</li>
<li>âœ“ Real-time violation detection with visual markers</li>
<li>âœ“ COM port auto-detection with selection dialog</li>
<li>âœ“ Intelligent line filtering (no header errors)</li>
<li>âœ“ Professional CSV format with comments</li>
<li>âœ“ Three synchronized real-time plots</li>
<li>âœ“ Unlimited data points (no cutoff)</li>
<li>âœ“ Negative value support for forces/positions</li>
<li>âœ“ Watchdog connection monitoring</li>
<li>âœ“ Mock data mode for testing</li>
</ul>

<h3>System Requirements:</h3>
<ul>
<li><b>Python:</b> 3.8 or higher</li>
<li><b>Operating System:</b> Windows 7+, Ubuntu 18.04+, macOS 10.13+</li>
<li><b>RAM:</b> 4 GB minimum recommended</li>
<li><b>Disk Space:</b> 100 MB</li>
</ul>

<h3>Python Dependencies:</h3>
<ul>
<li>pyserial >= 3.5</li>
<li>PyQt5 >= 5.15.0</li>
<li>pyqtgraph >= 0.13.0</li>
<li>pandas >= 1.5.0</li>
<li>numpy >= 1.23.0</li>
</ul>

<h3>Default Configuration:</h3>
<ul>
<li>COM Port: Auto-detected</li>
<li>Baudrate: 115200</li>
<li>Data Bits: 8</li>
<li>Parity: None</li>
<li>Stop Bits: 1</li>
<li>Plot Update Interval: 1000 ms</li>
<li>Watchdog Timeout: 5 seconds</li>
</ul>

<p style="margin-top: 20px; color: #27ae60;"><b>Status:</b> âœ“ Ready for Production</p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Version Information - v2.2")
        msg.setTextFormat(Qt.RichText)
        msg.setText(version_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_advanced_options(self):
        """Show Advanced Options dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        from PyQt5.QtCore import Qt, QTimer
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced Options")
        dialog.setGeometry(200, 200, 500, 350)
        dialog.setAttribute(Qt.WA_DeleteOnClose)  # Clean up when closed
        
        layout = QVBoxLayout()
        
        # === Button: Save Plotted Data as PDF ===
        save_pdf_btn = QPushButton("Save Plotted Data as PDF")
        save_pdf_btn.setMinimumHeight(40)
        save_pdf_btn.setToolTip("Export current plots to PDF file")
        # TODO: Connect to save_plots_to_pdf() when implemented
        layout.addWidget(save_pdf_btn)
        
        # === Separator ===
        separator = QLabel("-" * 60)
        separator.setAlignment(Qt.AlignCenter)
        layout.addWidget(separator)
        
        # === Force Analysis Section ===
        force_analysis_label = QLabel("Force Analysis")
        force_analysis_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(force_analysis_label)
        
        # Calculation: percentage of values exceeding (upper limit * 1.03)
        calculation_layout = QVBoxLayout()
        
        # Title
        calc_title = QLabel("Percentage of values exceeding (Upper Force Limit × 1.03):")
        calc_title.setStyleSheet("font-weight: bold;")
        calculation_layout.addWidget(calc_title)
        
        # Result display
        advanced_force_violation_label = QLabel("N/A")
        advanced_force_violation_label.setStyleSheet(
            "background-color: #f0f0f0; "
            "padding: 10px; "
            "border: 1px solid #cccccc; "
            "border-radius: 2px; "
            "font-size: 14pt; "
            "font-weight: bold; "
            "color: #c62828;"
        )
        advanced_force_violation_label.setAlignment(Qt.AlignCenter)
        advanced_force_violation_label.setMinimumHeight(50)
        calculation_layout.addWidget(advanced_force_violation_label)
        
        layout.addLayout(calculation_layout)
        layout.addStretch()
        
        # === Close Button ===
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        
        # Timer to update calculations every second
        update_timer = QTimer()
        def update_calculations():
            # Get upper force limit from threshold control
            if not self.upper_force_threshold_check.isChecked():
                advanced_force_violation_label.setText("Thresholds not enabled")
                return
            
            upper_limit = self.upper_force_upper_limit_spin.value()
            threshold_value = upper_limit * 1.03
            
            # Get plotter data
            force_upper_list = list(self.plotter.force_upper)
            
            if not force_upper_list:
                advanced_force_violation_label.setText("No data yet")
                return
            
            # Calculate percentage of values exceeding threshold
            exceeding_count = sum(1 for val in force_upper_list if val > threshold_value)
            total_count = len(force_upper_list)
            percentage = (exceeding_count / total_count * 100) if total_count > 0 else 0
            
            # Update label
            advanced_force_violation_label.setText(
                f"{percentage:.2f}%\n({exceeding_count} of {total_count} values)"
            )
        
        update_timer.timeout.connect(update_calculations)
        update_timer.start(500)  # Update every 500ms
        
        # Stop timer when dialog closes
        def on_dialog_closed():
            update_timer.stop()
        
        dialog.finished.connect(on_dialog_closed)
        
        # Initial update
        update_calculations()
        
        dialog.exec_()
    
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_connected:
            reply = QMessageBox.question(
                self,
                "Exit",
                "Connection is active. Disconnect and exit?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.disconnect_serial()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
