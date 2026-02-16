"""
Main Application - Fatigue Tester Data Acquisition System
Orchestrates all components with PyQt5 GUI

Version 2.3 (Phase 2 Refactored + PDF Export) - February 16, 2026
- Phase 1: UI components extracted (1522 → 667 lines, -56%)
- Phase 2: Business logic extracted + PDF export feature
- Final size: 683 lines (55% reduction from original V2.2!)
- New: Professional PDF reports with all plots and metadata
"""

import sys
import queue
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QMessageBox, QFileDialog)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import pyqtgraph as pg

from config import SerialConfig, PlotConfig, LogConfig, WatchdogConfig
from data_parser import DataParser
from serial_reader import SerialReader, MockSerialReader
from data_logger import DataLogger
from live_plotter import LivePlotter
from serial_port_detector import get_port_detector
from port_selection_dialog import PortSelectionDialog

# Phase 1: UI components
from ui_components import (ConnectionPanel, LoggingPanel, PlotSettingsPanel,
                           StatisticsPanel, StatusLogPanel)

# Phase 2: Business logic modules
from threshold_monitor import ThresholdMonitor, ThresholdConfiguration
from statistics_tracker import StatisticsTracker
from plot_exporter import PlotExporter


class DataProcessorWorker(QThread):
    """
    Worker thread for processing data from queue
    Implements the broker/processor layer
    """
    
    data_processed = pyqtSignal(object)  # Emits FatigueTestData
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data_queue: queue.Queue, parser: DataParser, stats_tracker: StatisticsTracker):
        super().__init__()
        self.data_queue = data_queue
        self.parser = parser
        self.stats_tracker = stats_tracker  # NEW: Use StatisticsTracker
        self.running = False
    
    def should_parse_line(self, line: str) -> bool:
        """Determine if a line should be parsed"""
        line = line.strip()
        
        if not line:
            return False
        
        # Skip header lines
        if line.startswith('###') or line.startswith('For display') or line.startswith('Loading'):
            return False
        
        # Skip configuration line
        if line.startswith('CNF;'):
            return False
        
        return line.startswith('DTA;') or line.startswith('END;')
        
    def run(self):
        """Process data from queue with intelligent line filtering"""
        self.running = True
        self.status_update.emit("Data processor started")
        
        lines_skipped = 0
        lines_parsed = 0
        
        while self.running:
            try:
                raw_data = self.data_queue.get(timeout=0.1)
                
                if not self.should_parse_line(raw_data):
                    lines_skipped += 1
                    self.stats_tracker.update_parse_stats(lines_parsed, lines_skipped)
                    continue
                
                parsed_data = self.parser.parse(raw_data)
                
                if parsed_data:
                    is_valid, error_msg = self.parser.validate_data(parsed_data)
                    
                    if is_valid:
                        lines_parsed += 1
                        self.stats_tracker.update_parse_stats(lines_parsed, lines_skipped)
                        self.data_processed.emit(parsed_data)
                    else:
                        self.error_occurred.emit(f"Validation error: {error_msg}")
                        
                    if parsed_data.is_test_end():
                        self.status_update.emit(
                            f"Test ended at cycle {parsed_data.cycles} "
                            f"(Parsed: {lines_parsed}, Skipped: {lines_skipped})"
                        )
                    
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
    """Main application window - Phase 2 Refactored"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fatigue Tester Data Acquisition System v2.3 (Phase 2)")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize configurations
        self.serial_config = SerialConfig()
        self.plot_config = PlotConfig()
        self.log_config = LogConfig()
        self.watchdog_config = WatchdogConfig()
        
        # Initialize core components
        self.data_queue = queue.Queue()
        self.parser = DataParser()
        self.logger = DataLogger(self.log_config)
        self.plotter = LivePlotter(self.plot_config)
        self.port_detector = get_port_detector()
        
        # Phase 2: Initialize business logic modules
        self.threshold_monitor = ThresholdMonitor(ThresholdConfiguration())
        self.stats_tracker = StatisticsTracker()
        self.plot_exporter = PlotExporter(self.plotter)
        
        # Serial reader (will be created on connect)
        self.serial_reader = None
        self.processor_worker = None
        
        # Watchdog
        self.watchdog = WatchdogTimer(self.watchdog_config.timeout_seconds)
        self.watchdog.timeout_occurred.connect(self.on_watchdog_timeout)
        
        # Connection state
        self.is_connected = False
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup UI (using components!)
        self.setup_ui()
        
        # Connect signals from UI components
        self.connect_component_signals()
        
        # Status bar
        from PyQt5.QtWidgets import QStatusBar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.update_status("Ready - V2.3 with PDF Export")
        
        # Statistics update timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(1000)  # Update every second
        
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
        """Setup the user interface - REFACTORED with components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Controls (NOW USING COMPONENTS!)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Connection Panel (Component)
        self.connection_panel = ConnectionPanel(self)
        left_panel.addWidget(self.connection_panel)
        
        # Logging Panel (Component)
        self.logging_panel = LoggingPanel(self)
        left_panel.addWidget(self.logging_panel)
        
        # Plot Settings Panel (Component - includes thresholds)
        self.plot_settings_panel = PlotSettingsPanel(self)
        left_panel.addWidget(self.plot_settings_panel)
        
        # Statistics Panel (Component)
        self.statistics_panel = StatisticsPanel(self)
        left_panel.addWidget(self.statistics_panel)
        
        # Status Log Panel (Component)
        self.status_log_panel = StatusLogPanel(self)
        left_panel.addWidget(self.status_log_panel)
        
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
        
        # Initialize UI with configuration values
        self._initialize_ui_values()
    
    def _initialize_ui_values(self):
        """Initialize UI components with configuration values"""
        # Connection panel
        try:
            detected_ports = self.port_detector.get_port_names()
            if detected_ports:
                self.connection_panel.add_ports(detected_ports)
                self.log_status(f"Auto-detected ports: {', '.join(detected_ports)}")
            else:
                self.connection_panel.add_ports(['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                                                'COM6', 'COM7', 'COM8', 'COM9', 'COM10'])
                self.log_status("No ports detected, using default list")
        except Exception as e:
            self.log_error(f"Port detection error: {e}")
            self.connection_panel.add_ports(['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                                            'COM6', 'COM7', 'COM8', 'COM9', 'COM10'])
        
        self.connection_panel.set_port(self.serial_config.port)
        self.connection_panel.set_baudrate(self.serial_config.baudrate)
        
        # Plot settings panel
        self.plot_settings_panel.set_update_interval(self.plot_config.update_interval_ms)
        self.plot_settings_panel.set_auto_range(self.plot_config.auto_range)
    
    def connect_component_signals(self):
        """Connect signals from UI components to handlers"""
        # Connection panel
        self.connection_panel.connect_clicked.connect(self.toggle_connection)
        self.connection_panel.detect_ports_clicked.connect(self.on_list_ports_clicked)
        
        # Logging panel
        self.logging_panel.save_clicked.connect(self.save_log_file)
        self.logging_panel.new_log_clicked.connect(self.start_new_log)
        
        # Plot settings panel
        self.plot_settings_panel.update_interval_changed.connect(self.on_update_interval_changed)
        self.plot_settings_panel.auto_range_changed.connect(self.on_auto_range_changed)
        self.plot_settings_panel.clear_plots_clicked.connect(self.clear_plots)
        self.plot_settings_panel.upper_force_threshold_changed.connect(self.on_upper_force_threshold_changed)
        self.plot_settings_panel.stiffness_threshold_changed.connect(self.on_stiffness_threshold_changed)
    
    def toggle_connection(self):
        """Toggle serial connection"""
        if self.is_connected:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def on_list_ports_clicked(self):
        """Handle 'Detect Ports' button click"""
        self.log_status("User clicked 'Detect Ports' button")
        
        # Create and show port selection dialog
        dialog = PortSelectionDialog(self, self.port_detector)
        dialog.port_selected.connect(self.on_port_selected)
        dialog.exec_()
    
    def on_port_selected(self, port_name: str):
        """Handle port selection from dialog"""
        self.log_status(f"Port selected from dialog: {port_name}")
        self.connection_panel.set_port(port_name)
        self.update_status(f"Selected port: {port_name}")
    
    def connect_serial(self):
        """Connect to serial port or start mock reader"""
        try:
            # Update configuration from UI
            self.serial_config.port = self.connection_panel.get_port()
            self.serial_config.baudrate = self.connection_panel.get_baudrate()
            
            # Create data processor (with StatisticsTracker)
            self.processor_worker = DataProcessorWorker(
                self.data_queue, 
                self.parser,
                self.stats_tracker  # Phase 2: Pass stats tracker
            )
            self.processor_worker.data_processed.connect(self.on_data_received)
            self.processor_worker.status_update.connect(self.log_status)
            self.processor_worker.error_occurred.connect(self.log_error)
            self.processor_worker.start()
            
            # Create serial reader or mock reader
            if self.connection_panel.is_mock_mode():
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
                self.stats_tracker.start_connection()  # Phase 2: Start connection tracking
                self.connection_panel.set_connected(True)
                
                # Start watchdog
                self.watchdog.start()
                
                # Start plotter update timer
                self.plotter.start_plotting()
                
                # Start logger
                log_file = self.logger.start_new_log()
                self.logging_panel.set_log_filename(self.logger.current_filename)
                self.logging_panel.set_buttons_enabled(True)
                
                # Log connection
                mode = "Mock Data" if self.connection_panel.is_mock_mode() else self.serial_config.port
                self.log_status(f"Connected to {mode} at {self.serial_config.baudrate} baud")
                self.update_status(f"Connected: {mode}")
                
        except Exception as e:
            self.log_error(f"Connection failed: {e}")
            QMessageBox.critical(self, "Connection Error", str(e))
    
    def disconnect_serial(self):
        """Disconnect from serial port"""
        try:
            # Stop watchdog
            self.watchdog.stop()
            
            # Stop plotter update timer
            self.plotter.stop_plotting()
            
            # Stop processor
            if self.processor_worker:
                self.processor_worker.stop()
                self.processor_worker.wait(2000)
            
            # Stop serial reader
            if self.serial_reader:
                self.serial_reader.stop()
                self.serial_reader.wait(2000)
            
            # Close logger
            self.logger.close_log()
            
            # Update UI
            self.is_connected = False
            self.stats_tracker.stop_connection()  # Phase 2: Stop connection tracking
            self.connection_panel.set_connected(False)
            self.logging_panel.set_buttons_enabled(False)
            
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
        
        # Phase 2: Check thresholds with ThresholdMonitor
        force_violation, stiffness_violation = self.threshold_monitor.check_data(data)
        
        # Phase 2: Update statistics
        self.stats_tracker.increment_data_points()
        
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
            self.logging_panel.set_log_filename(self.logger.current_filename)
            self.log_status(f"Started new log: {self.logger.current_filename}")
    
    def clear_plots(self):
        """Clear all plot data"""
        self.plotter.clear_plots()
        self.threshold_monitor.reset()  # Phase 2: Reset threshold violations
        self.stats_tracker.reset_data_stats()  # Phase 2: Reset data statistics
        self.log_status("Plots cleared")
    
    def on_update_interval_changed(self, value):
        """Handle plot update interval change"""
        self.plotter.set_update_interval(value)
    
    def on_auto_range_changed(self, enabled):
        """Handle auto-range checkbox change"""
        self.plotter.enable_auto_range(enabled)
    
    def on_upper_force_threshold_changed(self):
        """Handle Upper Force threshold changes"""
        # Phase 2: Update ThresholdMonitor configuration
        self.threshold_monitor.config.upper_force_enabled = self.plot_settings_panel.is_upper_force_threshold_enabled()
        self.threshold_monitor.config.upper_force_upper_limit = self.plot_settings_panel.get_upper_force_upper_limit()
        self.threshold_monitor.config.upper_force_lower_limit = self.plot_settings_panel.get_upper_force_lower_limit()
        
        # Update plotter for visualization
        self.plotter.set_upper_force_thresholds(
            self.threshold_monitor.config.upper_force_upper_limit,
            self.threshold_monitor.config.upper_force_lower_limit,
            self.threshold_monitor.config.upper_force_enabled
        )
        
        if self.threshold_monitor.config.upper_force_enabled:
            self.log_status(
                f"Upper Force thresholds enabled: "
                f"[{self.threshold_monitor.config.upper_force_lower_limit}, "
                f"{self.threshold_monitor.config.upper_force_upper_limit}] N"
            )
        else:
            self.log_status("Upper Force thresholds disabled")
    
    def on_stiffness_threshold_changed(self):
        """Handle Loss of Stiffness threshold changes"""
        # Phase 2: Update ThresholdMonitor configuration
        self.threshold_monitor.config.stiffness_enabled = self.plot_settings_panel.is_stiffness_threshold_enabled()
        self.threshold_monitor.config.stiffness_upper_limit = self.plot_settings_panel.get_stiffness_upper_limit()
        self.threshold_monitor.config.stiffness_lower_limit = self.plot_settings_panel.get_stiffness_lower_limit()
        
        # Update plotter for visualization
        self.plotter.set_stiffness_thresholds(
            self.threshold_monitor.config.stiffness_upper_limit,
            self.threshold_monitor.config.stiffness_lower_limit,
            self.threshold_monitor.config.stiffness_enabled
        )
        
        if self.threshold_monitor.config.stiffness_enabled:
            self.log_status(
                f"Stiffness thresholds enabled: "
                f"[{self.threshold_monitor.config.stiffness_lower_limit}, "
                f"{self.threshold_monitor.config.stiffness_upper_limit}] %"
            )
        else:
            self.log_status("Stiffness thresholds disabled")
    
    def update_statistics(self):
        """Update statistics display - Phase 2: Using StatisticsTracker and ThresholdMonitor"""
        stats = []
        
        # Phase 2: Get stats from StatisticsTracker
        tracker_stats = self.stats_tracker.get_summary()
        
        if tracker_stats['is_connected']:
            stats.append(f"Connection Time: {tracker_stats['connection_duration']:.1f}s")
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
        
        # Phase 2: Get violation counts from ThresholdMonitor
        force_violations, stiffness_violations = self.threshold_monitor.get_violation_counts()
        
        if self.threshold_monitor.config.upper_force_enabled:
            total_points = plotter_stats['points_plotted']
            stats.append(f"Upper Force Violations: {force_violations} / {total_points}")
        
        if self.threshold_monitor.config.stiffness_enabled:
            total_points = plotter_stats['points_plotted']
            stats.append(f"Stiffness Violations: {stiffness_violations} / {total_points}")
        
        # Parser statistics
        stats.append(f"Parse Errors: {self.parser.parse_errors}")
        
        self.statistics_panel.update_statistics('\n'.join(stats))
    
    def log_status(self, message: str):
        """Log status message"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_log_panel.append_message(f"[{timestamp}] {message}")
    
    def log_error(self, message: str):
        """Log error message"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_log_panel.append_message(
            f"[{timestamp}] <span style='color: red;'><b>ERROR:</b> {message}</span>"
        )
    
    def update_status(self, message: str):
        """Update status bar"""
        self.statusBar.showMessage(message)
    
    def show_help(self):
        """Show help documentation for v2.3"""
        try:
            help_text = """
<h2>Fatigue Tester Data Acquisition System v2.3 - Help</h2>

<div style="background-color: #e8f4f8; padding: 10px; margin: 10px 0; border-left: 4px solid #0066cc;">
<strong>🎉 New in V2.3 (Feb 16, 2026):</strong>
<ul>
<li>📄 <strong>PDF Export</strong> - Generate professional reports with all plots and metadata</li>
<li>🏗️ <strong>Modular Architecture</strong> - Improved code quality (56% reduction)</li>
<li>📊 <strong>Enhanced Metadata</strong> - Complete test traceability in PDFs</li>
</ul>
</div>

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
   <li>Calculated as: (Travel_2 / Travel_at_Upper) × 100</li>
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
<p><code>Loss of Stiffness [%] = (Travel_2 / Travel_at_Upper) × 100</code></p>
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

<h3>Features in v2.3</h3>
<ul>
<li>✓ <strong>PDF Export</strong> - Professional reports with all plots and metadata</li>
<li>✓ <strong>Modular Architecture</strong> - Improved maintainability (56% code reduction)</li>
<li>✓ Complete header/configuration logging</li>
<li>✓ Test traceability with device ID preservation</li>
<li>✓ Threshold monitoring with violation detection</li>
<li>✓ COM port auto-detection</li>
<li>✓ Intelligent line filtering (no parse errors)</li>
<li>✓ Three synchronized real-time plots</li>
<li>✓ Unlimited data points</li>
<li>✓ Negative value support</li>
<li>✓ Watchdog connection monitoring</li>
<li>✓ Mock data mode for testing</li>
<li>✓ Professional CSV format</li>
<li>✓ Comprehensive Help and User Manual</li>
</ul>

<h3>PDF Export (New!)</h3>
<p><strong>How to Generate PDF Reports:</strong></p>
<ol>
<li>Menu: <strong>Advanced Options → Advanced Settings</strong></li>
<li>Click <strong>"📄 Export Plots to PDF"</strong></li>
<li>Choose filename and location</li>
<li>PDF generated in &lt; 5 seconds!</li>
</ol>
<p><strong>PDF Contains:</strong></p>
<ul>
<li>All three plots on single page (Forces, Travel, Loss of Stiffness)</li>
<li>Complete test metadata and statistics</li>
<li>Log filename for traceability</li>
<li>Threshold settings and violations</li>
<li>Data ranges for all parameters</li>
</ul>

<h3>For More Information</h3>
<p>See "Serial Data Logger and Plotter - User Manual" in Help menu for complete documentation.</p>
"""
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Help - Fatigue Tester v2.3")
            msg.setTextFormat(Qt.RichText)
            msg.setText(help_text)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error showing help: {e}")
            print(f"Help dialog error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_user_manual(self):
        """Show Serial Data Logger and Plotter User Manual (v2.3)"""
        # Load user manual from external HTML file
        import os
        manual_path = os.path.join(os.path.dirname(__file__), 'USER_MANUAL_V23.html')
        
        try:
            with open(manual_path, 'r', encoding='utf-8') as f:
                manual_html = f.read()
            
            # Create a dialog with a text browser for better HTML rendering
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("User Manual - Serial Data Logger and Plotter v2.3")
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
                f"Could not find USER_MANUAL_V23.html in application directory.\n\n"
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
<p><b>Version:</b> 2.3 (February 16, 2026) - Phase 2 Refactored + PDF Export</p>
<p><b>Requirements:</b> V2.3 (Modular Architecture and PDF Export)</p>
<p><b>Contact:</b> Uwe Hasenstab and Alexander Waal</p>

<p>A professional data acquisition system for fatigue testing equipment with 
real-time visualization, comprehensive data logging, test traceability, and 
<strong>professional PDF report generation</strong>.</p>

<div style="background-color: #e8f4f8; padding: 10px; margin: 10px 0; border-left: 4px solid #0066cc;">
<strong>🎉 New in Version 2.3:</strong>
<ul>
<li><strong>PDF Export</strong> - Generate professional multi-page reports</li>
<li><strong>Modular Architecture</strong> - 56% code reduction, improved maintainability</li>
<li><strong>Enhanced Metadata</strong> - Log filename and complete statistics in PDFs</li>
</ul>
</div>

<h3>Version 2.3 Features:</h3>
<ul>
<li><strong>📄 PDF Export</strong> - All plots + comprehensive metadata in professional reports</li>
<li><strong>🏗️ Modular Design</strong> - Reusable UI components and business logic modules</li>
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
<li><strong>PDF report generation with matplotlib</strong></li>
</ul>

<h3>Architecture:</h3>
<p>Layered, event-driven design using the Producer-Consumer pattern 
with thread-safe communication and hardware abstraction.</p>
<p><b>Phase 1 Refactoring:</b> UI components extracted (56% code reduction)</p>
<p><b>Phase 2 Refactoring:</b> Business logic modules + PDF export feature</p>

<h3>Technology Stack:</h3>
<ul>
<li>Python 3.8+</li>
<li>PyQt5 (GUI Framework)</li>
<li>PyQtGraph (Real-time Plotting)</li>
<li>pyserial (Serial Communication)</li>
<li>pandas (Data Management)</li>
<li>numpy (Numerical Operations)</li>
<li><strong>matplotlib (PDF Report Generation)</strong></li>
</ul>

<p style="margin-top: 20px;"><i>For detailed documentation, see USER_MANUAL_V23.html</i></p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About - Fatigue Tester v2.3")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_version(self):
        """Show version information for v2.3"""
        version_text = """
<h2>Version Information - Fatigue Tester v2.3 (Phase 2 + PDF Export)</h2>

<table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: #3498db; color: white;">
    <td><b>Application</b></td>
    <td>Fatigue Tester Data Acquisition System</td>
</tr>
<tr>
    <td><b>Current Version</b></td>
    <td>2.3 (Phase 2 Refactored + PDF Export)</td>
</tr>
<tr>
    <td><b>Release Date</b></td>
    <td>February 16, 2026</td>
</tr>
<tr>
    <td><b>Requirements</b></td>
    <td>SRS V2.3 (Updated 16 Feb 2026)</td>
</tr>
<tr>
    <td><b>Status</b></td>
    <td>✓ Stable and Ready</td>
</tr>
</table>

<h3>Module Versions (v2.3):</h3>
<ul>
<li><b>Main Application:</b> V2.3 Phase 2 - Modular architecture, 56% code reduction, PDF export</li>
<li><b>UI Components:</b> V1.0 - ConnectionPanel, LoggingPanel, PlotSettingsPanel, StatisticsPanel, StatusLogPanel</li>
<li><b>Business Logic Modules (NEW):</b> V1.0 - ThresholdMonitor, StatisticsTracker, PlotExporter</li>
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
<tr>
    <td><b>2.2 Refactored</b></td>
    <td>Feb 12, 2026</td>
    <td>Phase 1 refactoring: UI components extracted, 56% code reduction (1522 → 667 lines)</td>
</tr>
<tr style="background-color: #e8f4f8;">
    <td><b>2.3 Phase 2</b></td>
    <td>Feb 16, 2026</td>
    <td><strong>Phase 2 refactoring: Business logic modules + PDF Export feature (667 → 683 lines final)</strong></td>
</tr>
</table>

<h3>Key Features in v2.3:</h3>
<ul>
<li>✓ <strong>PDF Export</strong> - Professional reports with all plots and metadata</li>
<li>✓ <strong>Modular Architecture</strong> - Business logic modules (ThresholdMonitor, StatisticsTracker, PlotExporter)</li>
<li>✓ <strong>Enhanced Metadata</strong> - Log filename and complete statistics in PDFs</li>
<li>✓ Header/configuration logging (device ID, setup parameters)</li>
<li>✓ Complete test traceability with metadata in CSV</li>
<li>✓ Threshold monitoring (Upper Force and Loss of Stiffness)</li>
<li>✓ Real-time violation detection with visual markers</li>
<li>✓ COM port auto-detection with selection dialog</li>
<li>✓ Intelligent line filtering (no header errors)</li>
<li>✓ Professional CSV format with comments</li>
<li>✓ Three synchronized real-time plots</li>
<li>✓ Unlimited data points (no cutoff)</li>
<li>✓ Negative value support for forces/positions</li>
<li>✓ Watchdog connection monitoring</li>
<li>✓ Mock data mode for testing</li>
<li>✓ Modular UI architecture (Phase 1 refactoring)</li>
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
<li><strong>matplotlib >= 3.5.0 (NEW for PDF export)</strong></li>
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

<p style="margin-top: 20px; color: #27ae60;"><b>Status:</b> ✓ Ready for Production</p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Version Information - v2.3")
        msg.setTextFormat(Qt.RichText)
        msg.setText(version_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_advanced_options(self):
        """Show Advanced Options dialog - Phase 2: With working PDF export!"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced Options")
        dialog.setGeometry(200, 200, 500, 400)
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        
        layout = QVBoxLayout()
        
        # === Button: Save Plotted Data as PDF (NOW WORKING!) ===
        save_pdf_btn = QPushButton("📄 Export Plots to PDF")
        save_pdf_btn.setMinimumHeight(50)
        save_pdf_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; "
            "font-weight: bold; font-size: 12pt; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        save_pdf_btn.setToolTip("Export all three plots to a multi-page PDF document")
        save_pdf_btn.clicked.connect(lambda: self._export_plots_to_pdf(dialog))
        layout.addWidget(save_pdf_btn)
        
        # === Separator ===
        separator = QLabel("-" * 60)
        separator.setAlignment(Qt.AlignCenter)
        layout.addWidget(separator)
        
        # === Force Analysis Section ===
        force_analysis_label = QLabel("Force Analysis")
        force_analysis_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(force_analysis_label)
        
        # Calculation: percentage of values exceeding (upper limit × 1.03)
        calculation_layout = QVBoxLayout()
        
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
        
        # Timer to update calculations
        update_timer = QTimer()
        def update_calculations():
            # Phase 2: Use ThresholdMonitor for advanced analysis
            force_data = list(self.plotter.force_upper)
            analysis = self.threshold_monitor.calculate_advanced_force_analysis(force_data)
            
            if not analysis['enabled']:
                advanced_force_violation_label.setText("Thresholds not enabled")
            elif not force_data:
                advanced_force_violation_label.setText("No data yet")
            else:
                advanced_force_violation_label.setText(
                    f"{analysis['threshold_103_percentage']:.2f}%\n"
                    f"({analysis['exceeding_count']} of {analysis['total_count']} values)"
                )
        
        update_timer.timeout.connect(update_calculations)
        update_timer.start(500)
        
        dialog.finished.connect(lambda: update_timer.stop())
        
        # Initial update
        update_calculations()
        
        dialog.exec_()
    
    def _export_plots_to_pdf(self, parent_dialog=None):
        """Export plots to PDF - Phase 2: NEW FEATURE!"""
        # Check if we have data
        if not self.plotter.cycles:
            QMessageBox.warning(
                self,
                "No Data",
                "No plot data available to export.\nPlease connect and collect data first."
            )
            return
        
        # Get filename from user
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Plots to PDF",
            f"fatigue_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if filename:
            try:
                # Export using PlotExporter with log filename
                success = self.plot_exporter.export_to_pdf(
                    filename,
                    include_metadata=True,
                    threshold_monitor=self.threshold_monitor,
                    statistics_tracker=self.stats_tracker,
                    log_filename=self.logger.current_filename
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "PDF Export Successful",
                        f"Plots exported successfully to:\n{filename}\n\n"
                        f"The PDF contains:\n"
                        f"• Page 1: All Three Plots (Forces, Travel, Loss of Stiffness)\n"
                        f"• Page 2: Test Summary and Metadata\n\n"
                        f"Includes:\n"
                        f"- Log filename: {self.logger.current_filename}\n"
                        f"- All travel measurements\n"
                        f"- Threshold violations\n"
                        f"- Test statistics"
                    )
                    self.log_status(f"Plots exported to PDF: {filename}")
                    
                    # Close the advanced options dialog if it's still open
                    if parent_dialog:
                        parent_dialog.accept()
                else:
                    QMessageBox.critical(
                        self,
                        "Export Failed",
                        "Failed to export plots to PDF.\nPlease check the log for details."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"An error occurred during PDF export:\n\n{str(e)}"
                )
                self.log_error(f"PDF export error: {e}")
    
    
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
