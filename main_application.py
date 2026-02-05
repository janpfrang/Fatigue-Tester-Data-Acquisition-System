"""
Main Application - Fatigue Tester Data Acquisition System
Orchestrates all components with PyQt5 GUI
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
        
    def run(self):
        """Process data from queue"""
        self.running = True
        self.status_update.emit("Data processor started")
        
        while self.running:
            try:
                # Get data from queue with timeout
                raw_data = self.data_queue.get(timeout=0.1)
                
                # Parse data
                parsed_data = self.parser.parse(raw_data)
                
                if parsed_data:
                    # Validate data
                    is_valid, error_msg = self.parser.validate_data(parsed_data)
                    
                    if is_valid:
                        # Emit parsed data to consumers
                        self.data_processed.emit(parsed_data)
                    else:
                        self.error_occurred.emit(f"Validation error: {error_msg}")
                        
                    # Check for test end or errors
                    if parsed_data.is_test_end():
                        self.status_update.emit("Test ended")
                    
                    if parsed_data.has_error():
                        error_desc = self.parser.get_error_description(parsed_data.error_code)
                        self.error_occurred.emit(f"Test error: {error_desc}")
                
            except queue.Empty:
                continue
            except Exception as e:
                self.error_occurred.emit(f"Processing error: {e}")
    
    def stop(self):
        """Stop the processor"""
        self.running = False


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
        self.setWindowTitle("Fatigue Tester Data Acquisition System v2.0")
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
        """Create connection settings group"""
        group = QGroupBox("Connection Settings")
        layout = QGridLayout()
        
        # Port selection
        layout.addWidget(QLabel("COM Port:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        self.port_combo.addItems(['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                                  'COM6', 'COM7', 'COM8', 'COM9', 'COM10'])
        self.port_combo.setCurrentText(self.serial_config.port)
        layout.addWidget(self.port_combo, 0, 1)
        
        # Baudrate
        layout.addWidget(QLabel("Baudrate:"), 1, 0)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(['4800', '9600', '19200', '38400', '57600', '115200'])
        self.baudrate_combo.setCurrentText(str(self.serial_config.baudrate))
        layout.addWidget(self.baudrate_combo, 1, 1)
        
        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn, 2, 0, 1, 2)
        
        # Mock mode checkbox
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
        
        # Update interval
        layout.addWidget(QLabel("Update Interval (ms):"), 0, 0)
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(100, 5000)
        self.update_interval_spin.setValue(self.plot_config.update_interval_ms)
        self.update_interval_spin.setSingleStep(100)
        self.update_interval_spin.valueChanged.connect(self.on_update_interval_changed)
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
        
        group.setLayout(layout)
        return group
    
    def create_statistics_group(self) -> QGroupBox:
        """Create statistics display group"""
        group = QGroupBox("Statistics")
        layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
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
        self.status_log.setMaximumHeight(200)
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
        
        # Parser statistics
        stats.append(f"Parse Errors: {self.parser.parse_errors}")
        
        self.stats_text.setText('\n'.join(stats))
    
    def log_status(self, message: str):
        """Log status message"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_log.append(f"[{timestamp}] {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_log.append(f"[{timestamp}] <span style='color: red;'><b>ERROR:</b> {message}</span>")
    
    def update_status(self, message: str):
        """Update status bar"""
        self.statusBar.showMessage(message)
    
    def show_help(self):
        """Show help documentation"""
        help_text = """
<h2>Fatigue Tester Data Acquisition System - Help</h2>

<h3>Quick Start</h3>
<ol>
<li><b>Connect to Hardware:</b>
   <ul>
   <li>Select COM port from dropdown</li>
   <li>Select baudrate (default: 9600)</li>
   <li>Click "Connect" button</li>
   </ul>
</li>
<li><b>Testing Without Hardware:</b>
   <ul>
   <li>Check "Use Mock Data (Testing)"</li>
   <li>Click "Connect" to see simulated data</li>
   </ul>
</li>
</ol>

<h3>Plot Descriptions</h3>
<ul>
<li><b>Plot 1 - Forces:</b> Lower Force and Upper Force vs. Cycles</li>
<li><b>Plot 2 - Travel Measurements:</b> Travel at Upper Force, Additional Travel 1, and Additional Travel 2 vs. Cycles</li>
<li><b>Plot 3 - Loss of Stiffness:</b> Calculated as (Additional Travel 2 / Travel at Upper Force) Ã— 100%</li>
</ul>

<h3>Data Logging</h3>
<ul>
<li>Data is automatically logged to CSV files in the logs/ directory</li>
<li>Files are named with timestamps: fatigue_test_YYYYMMDD_HHMMSS.csv</li>
<li>Use "Save Log As..." to save with a custom name</li>
<li>Files are never overwritten</li>
</ul>

<h3>Plot Controls</h3>
<ul>
<li><b>Update Interval:</b> Change how often plots refresh (100-5000 ms)</li>
<li><b>Auto Range:</b> Automatically adjust axis ranges</li>
<li><b>Clear Plots:</b> Clear displayed data (does not affect logged data)</li>
</ul>

<h3>Troubleshooting</h3>
<ul>
<li><b>Connection Failed:</b> Check COM port and baudrate settings</li>
<li><b>No Data Received:</b> Check cable connection and equipment settings</li>
<li><b>Watchdog Timeout:</b> No data received for 5 seconds - check connection</li>
</ul>

<h3>Data Format</h3>
Expected serial format: <code>DTA;31422;182;263;0;793;2238;0;611;0;!</code>
<br>
Fields are semicolon-separated with specific decimal place encoding.

<h3>For More Information</h3>
See README.md and QUICKSTART.txt files in the application directory.
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Help")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_user_manual(self):
        """Show Serial Data Logger and Plotter User Manual"""
        manual_text = """
<h2>Serial Data Logger and Plotter - User Manual</h2>
<p><b>Version 2.0</b> - February 2026</p>

<h3>Quick Start</h3>
<ol>
<li>Connect your fatigue test equipment to a COM port</li>
<li>Select the COM port from the dropdown</li>
<li>Verify baudrate is set to <b>115200</b> (default for v2.0)</li>
<li>Click <b>Connect</b> to start data acquisition</li>
<li>Monitor the three real-time plots</li>
<li>Data is automatically logged to CSV files in the logs/ directory</li>
</ol>

<h3>Main Features</h3>
<ul>
<li><b>Real-time Data Acquisition:</b> Receives serial data at 0.1-1.0 second intervals</li>
<li><b>Three Live Plots:</b>
  <ul>
    <li>Plot 1: Lower and Upper Forces [N]</li>
    <li>Plot 2: Travel measurements [mm]</li>
    <li>Plot 3: Loss of Stiffness [%]</li>
  </ul>
</li>
<li><b>Automatic CSV Logging:</b> Timestamp-based filenames, never overwrites existing files</li>
<li><b>Mock Data Mode:</b> Test the application without hardware</li>
<li><b>Watchdog Timer:</b> Alerts if no data received for 5 seconds</li>
<li><b>Unlimited Data Points:</b> No artificial limits on test duration</li>
</ul>

<h3>Data Format</h3>
<p><b>Serial Input:</b><br>
<code>DTA;31422;182;263;0;793;2238;0;611;0;!</code></p>
<p>Fields are semicolon-separated with decimal encoding:
<ul>
<li>Position values: last 2 digits are decimals (182 = 1.82 mm)</li>
<li>Force values: last digit is decimal (263 = 26.3 N)</li>
</ul>
</p>

<h3>CSV Output Columns</h3>
<ul>
<li>Timestamp, Status, Cycles</li>
<li>Position_1_mm, Force_Lower_N, Travel_1_mm</li>
<li>Position_2_mm, Force_Upper_N, Travel_2_mm</li>
<li>Travel_at_Upper_mm, Error_Code</li>
<li>Loss_of_Stiffness_Percent (calculated)</li>
</ul>

<h3>New in Version 2.0</h3>
<ul>
<li>Default baudrate: <b>115200</b> (was 9600)</li>
<li>Added this User Manual menu item</li>
<li>Support for negative force and position values</li>
<li>Unlimited data points (no cutoff)</li>
<li>Loss of Stiffness calculation and Plot 3</li>
</ul>

<h3>Error Codes</h3>
<ul>
<li><b>000:</b> No error</li>
<li><b>010-014:</b> Test failures (path/force violations)</li>
<li><b>101-107:</b> Motor errors</li>
<li><b>201-205:</b> Force search errors</li>
</ul>

<h3>Troubleshooting</h3>
<ul>
<li><b>Connection Failed:</b> Check COM port, baudrate (115200), and USB cable</li>
<li><b>No Data:</b> Verify equipment is transmitting, check Status Log</li>
<li><b>Parse Errors:</b> Check data format and baudrate settings</li>
<li><b>Watchdog Timeout:</b> Check connection, equipment power</li>
</ul>

<h3>Tips</h3>
<ul>
<li>Use "Use Mock Data" mode to test without hardware</li>
<li>CSV files are in ./logs/ directory</li>
<li>Files never overwrite (automatic _01, _02 suffix)</li>
<li>All data points are plotted (no limits)</li>
<li>Status Log shows real-time messages and errors</li>
</ul>

<p><i>For more information, see README.md and QUICKSTART.txt</i></p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("User Manual - Serial Data Logger and Plotter v2.0")
        msg.setTextFormat(Qt.RichText)
        msg.setText(manual_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
<h2>Fatigue Tester Data Acquisition System</h2>
<p><b>Version:</b> 2.0 (Updated for V2 Requirements)</p>
<p><b>Date:</b> February 2026</p>

<p>A professional data acquisition system for fatigue testing equipment with 
real-time visualization and comprehensive data logging capabilities.</p>

<h3>Key Features:</h3>
<ul>
<li>Real-time serial data acquisition</li>
<li>Live plotting with three configurable plots</li>
<li>Automatic CSV logging</li>
<li>Loss of stiffness calculation</li>
<li>Watchdog timer for connection monitoring</li>
<li>Mock data mode for testing</li>
</ul>

<h3>Architecture:</h3>
<p>Layered, event-driven design using the Producer-Consumer pattern 
with thread-safe communication.</p>

<h3>Technology Stack:</h3>
<ul>
<li>Python 3.8+</li>
<li>PyQt5 (GUI)</li>
<li>PyQtGraph (Plotting)</li>
<li>pyserial (Communication)</li>
</ul>

<p><i>For support and documentation, see README.md</i></p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_version(self):
        """Show version information"""
        version_text = """
<h2>Version Information</h2>

<table border="1" cellpadding="5" style="border-collapse: collapse;">
<tr><td><b>Application:</b></td><td>Fatigue Tester Data Acquisition System</td></tr>
<tr><td><b>Version:</b></td><td>2.0</td></tr>
<tr><td><b>Release Date:</b></td><td>February 2026</td></tr>
<tr><td><b>Requirements:</b></td><td>V2 (Updated 05 Feb 2026)</td></tr>
</table>

<h3>Component Versions:</h3>
<ul>
<li><b>Configuration Module:</b> V2 (Updated field names, baudrate 115200)</li>
<li><b>Data Parser:</b> V2 (Allows negative values, Loss of Stiffness calc)</li>
<li><b>Live Plotter:</b> V2 (Three plots, unlimited points)</li>
<li><b>Data Logger:</b> V2 (Updated CSV headers)</li>
<li><b>Serial Reader:</b> 1.0</li>
<li><b>Main Application:</b> V2 (Added Help and Version menus, User Manual)</li>
</ul>

<h3>Updates in V2:</h3>
<ul>
<li>âœ“ Updated field naming (position 1, position 2, travel 1, travel 2)</li>
<li>âœ“ New Plot 2: Travel at Upper + Travel 1 + Travel 2</li>
<li>âœ“ New Plot 3: Loss of Stiffness % calculation</li>
<li>âœ“ Allow negative values for force and position</li>
<li>âœ“ Plot unlimited data points (no cutoff)</li>
<li>âœ“ Added Help menu</li>
<li>âœ“ Added Version menu</li>
<li>✓ Default baudrate changed to 115200</li>
<li>✓ Added "Serial Data Logger and Plotter - User Manual" menu item</li>
</ul>

<h3>Python Requirements:</h3>
<ul>
<li>Python: 3.8 or higher</li>
<li>pyserial: â‰¥3.5</li>
<li>PyQt5: â‰¥5.15.0</li>
<li>pyqtgraph: â‰¥0.13.0</li>
<li>pandas: â‰¥1.5.0</li>
<li>numpy: â‰¥1.23.0</li>
</ul>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Version Information")
        msg.setTextFormat(Qt.RichText)
        msg.setText(version_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
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
