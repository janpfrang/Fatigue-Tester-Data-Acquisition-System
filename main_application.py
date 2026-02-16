"""
Main Application - Fatigue Tester Data Acquisition System
Orchestrates all components with PyQt5 GUI

Version 2.2 (Phase 2 Refactored) - February 12, 2026
- Phase 1: UI components extracted (1522 → 667 lines)
- Phase 2: Business logic extracted + PDF export feature
- Final size: ~450 lines (70% reduction from original!)
"""

import sys
import queue
import time
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
        self.setWindowTitle("Fatigue Tester Data Acquisition System v2.2 (Phase 2)")
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
        self.update_status("Ready - Phase 2 with PDF Export")
        
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
    

    # Dialog methods moved to dialogs.py module - see dialogs.py for implementation
    def show_help(self):
        """Show help documentation"""
        from dialogs import show_help_dialog
        show_help_dialog(self)
    
    def show_user_manual(self):
        """Show user manual"""
        from dialogs import show_user_manual_dialog
        show_user_manual_dialog(self)
    
    def show_about(self):
        """Show about dialog"""
        from dialogs import show_about_dialog
        show_about_dialog(self)
    
    def show_version(self):
        """Show version information"""
        from dialogs import show_version_dialog
        show_version_dialog(self)
    
    def show_advanced_options(self):
        """Show advanced options dialog"""
        from dialogs import show_advanced_options_dialog
        show_advanced_options_dialog(self, self.plot_exporter, self.threshold_monitor, 
                                     self.stats_tracker, self.plotter, 
                                     self.plot_settings_panel)
    
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
