"""
Live Plotter module - Consumer for real-time visualization
Handles plotting of test data with PyQtGraph
"""

import pyqtgraph as pg
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from collections import deque
from typing import Optional
import numpy as np
from config import PlotConfig
from data_parser import FatigueTestData


class LivePlotter(QObject):
    """
    Consumer that handles real-time plotting
    Implements decoupled plotting with configurable update rate
    """
    
    # Signals for thread-safe GUI updates
    update_requested = pyqtSignal()
    
    def __init__(self, config: PlotConfig):
        """
        Initialize live plotter
        
        Args:
            config: Plot configuration
        """
        super().__init__()
        self.config = config
        
        # Data buffers - no maxlen for unlimited points (V2 requirement)
        self.cycles = deque()
        self.force_lower = deque()
        self.force_upper = deque()
        self.travel_1 = deque()
        self.travel_2 = deque()
        self.travel_at_upper = deque()
        self.loss_of_stiffness = deque()
        
        # Threshold settings for Upper Force
        self.upper_force_upper_limit = None
        self.upper_force_lower_limit = None
        self.upper_force_thresholds_enabled = False
        
        # Threshold settings for Loss of Stiffness
        self.stiffness_upper_limit = None
        self.stiffness_lower_limit = None
        self.stiffness_thresholds_enabled = False
        
        # Violation counters
        self.upper_force_violations = 0
        self.stiffness_violations = 0
        
        # Plot widgets
        self.plot_widget: Optional[pg.GraphicsLayoutWidget] = None
        self.plots = {}
        self.curves = {}
        self.threshold_lines = {}  # Store threshold line items
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.setInterval(config.update_interval_ms)
        self.update_timer.timeout.connect(self._update_plots)
        
        # Statistics
        self.points_received = 0
        self.points_plotted = 0
        self.last_update_time = None
        
    def setup_plots(self, parent_widget: pg.GraphicsLayoutWidget):
        """
        Setup plot widgets and layout per V2 requirements
        
        Args:
            parent_widget: Parent GraphicsLayoutWidget
        """
        self.plot_widget = parent_widget
        self.plot_widget.clear()
        
        # Plot 1: Forces vs Cycles (Lower Force + Upper Force)
        self.plots['forces'] = self.plot_widget.addPlot(row=0, col=0, title="Forces vs Cycles")
        self.plots['forces'].setLabel('left', 'Force', units='N')
        self.plots['forces'].setLabel('bottom', 'Cycles')
        self.plots['forces'].showGrid(x=True, y=True, alpha=0.3)
        self.plots['forces'].addLegend()
        
        # Create curves for forces plot
        self.curves['force_lower'] = self.plots['forces'].plot(
            pen=pg.mkPen(color='b', width=2), name='Lower Force [N]')
        self.curves['force_upper'] = self.plots['forces'].plot(
            pen=pg.mkPen(color='r', width=2), name='Upper Force [N]')
        
        # Add scatter plot for Upper Force violations (initially empty)
        self.curves['force_upper_violations'] = self.plots['forces'].plot(
            pen=None, 
            symbol='o', 
            symbolBrush='r', 
            symbolPen='r',
            symbolSize=10, 
            name='Upper Force Violations')
        
        # Add threshold lines for Upper Force (initially invisible)
        self.threshold_lines['upper_force_upper'] = pg.InfiniteLine(
            angle=0, movable=False, 
            pen=pg.mkPen(color='r', width=2, style=pg.QtCore.Qt.DashLine))
        self.threshold_lines['upper_force_lower'] = pg.InfiniteLine(
            angle=0, movable=False, 
            pen=pg.mkPen(color='r', width=2, style=pg.QtCore.Qt.DashLine))
        self.plots['forces'].addItem(self.threshold_lines['upper_force_upper'])
        self.plots['forces'].addItem(self.threshold_lines['upper_force_lower'])
        self.threshold_lines['upper_force_upper'].setVisible(False)
        self.threshold_lines['upper_force_lower'].setVisible(False)
        
        # Plot 2: Travel measurements vs Cycles (Travel at Upper + Travel 1 + Travel 2)
        self.plots['travel'] = self.plot_widget.addPlot(row=1, col=0, title="Travel Measurements vs Cycles")
        self.plots['travel'].setLabel('left', 'Travel', units='mm')
        self.plots['travel'].setLabel('bottom', 'Cycles')
        self.plots['travel'].showGrid(x=True, y=True, alpha=0.3)
        self.plots['travel'].addLegend()
        
        # Create curves for travel plot
        self.curves['travel_at_upper'] = self.plots['travel'].plot(
            pen=pg.mkPen(color='g', width=2), name='Travel at Upper Force [mm]')
        self.curves['travel_1'] = self.plots['travel'].plot(
            pen=pg.mkPen(color='c', width=2), name='Additional Travel 1 [mm]')
        self.curves['travel_2'] = self.plots['travel'].plot(
            pen=pg.mkPen(color='m', width=2), name='Additional Travel 2 [mm]')
        
        # Plot 3: Loss of Stiffness % vs Cycles
        self.plots['stiffness'] = self.plot_widget.addPlot(row=2, col=0, title="Loss of Stiffness vs Cycles")
        self.plots['stiffness'].setLabel('left', 'Loss of Stiffness', units='%')
        self.plots['stiffness'].setLabel('bottom', 'Cycles')
        self.plots['stiffness'].showGrid(x=True, y=True, alpha=0.3)
        
        # Create curve for stiffness plot
        self.curves['loss_stiffness'] = self.plots['stiffness'].plot(
            pen=pg.mkPen(color=(255, 140, 0), width=2))
        
        # Add scatter plot for Stiffness violations (initially empty)
        self.curves['stiffness_violations'] = self.plots['stiffness'].plot(
            pen=None, 
            symbol='o', 
            symbolBrush=(255, 140, 0), 
            symbolPen=(255, 140, 0),
            symbolSize=10, 
            name='Stiffness Violations')
        
        # Add threshold lines for Loss of Stiffness (initially invisible)
        self.threshold_lines['stiffness_upper'] = pg.InfiniteLine(
            angle=0, movable=False, 
            pen=pg.mkPen(color=(255, 140, 0), width=2, style=pg.QtCore.Qt.DashLine))
        self.threshold_lines['stiffness_lower'] = pg.InfiniteLine(
            angle=0, movable=False, 
            pen=pg.mkPen(color=(255, 140, 0), width=2, style=pg.QtCore.Qt.DashLine))
        self.plots['stiffness'].addItem(self.threshold_lines['stiffness_upper'])
        self.plots['stiffness'].addItem(self.threshold_lines['stiffness_lower'])
        self.threshold_lines['stiffness_upper'].setVisible(False)
        self.threshold_lines['stiffness_lower'].setVisible(False)
        
        # Configure auto-ranging
        if self.config.auto_range:
            for plot in self.plots.values():
                plot.enableAutoRange()
    
    def add_data(self, data: FatigueTestData):
        """
        Add new data point to buffers
        
        Args:
            data: Parsed fatigue test data
        """
        self.cycles.append(data.cycles)
        self.force_lower.append(data.force_lower_n)
        self.force_upper.append(data.force_upper_n)
        self.travel_1.append(data.travel_1_mm)
        self.travel_2.append(data.travel_2_mm)
        self.travel_at_upper.append(data.travel_at_upper_mm)
        self.loss_of_stiffness.append(data.calculate_loss_of_stiffness())
        
        self.points_received += 1
    
    def start_plotting(self):
        """Start the plot update timer"""
        self.update_timer.start()
        print(f"[LivePlotter] Started plotting with {self.config.update_interval_ms}ms interval")
    
    def stop_plotting(self):
        """Stop the plot update timer"""
        self.update_timer.stop()
        print("[LivePlotter] Stopped plotting")
    
    def _update_plots(self):
        """Update all plots with current data (called by timer)"""
        if not self.plot_widget or len(self.cycles) == 0:
            return
        
        try:
            # Convert deques to numpy arrays for efficient plotting
            cycles_array = np.array(self.cycles)
            force_upper_array = np.array(self.force_upper)
            stiffness_array = np.array(self.loss_of_stiffness)
            
            # Update forces plot (Plot 1)
            self.curves['force_lower'].setData(cycles_array, np.array(self.force_lower))
            self.curves['force_upper'].setData(cycles_array, force_upper_array)
            
            # Check Upper Force thresholds and highlight violations
            if self.upper_force_thresholds_enabled:
                # Find violations
                violations_mask = (force_upper_array > self.upper_force_upper_limit) | \
                                 (force_upper_array < self.upper_force_lower_limit)
                
                # Count violations
                self.upper_force_violations = np.sum(violations_mask)
                
                # Get violation points
                if self.upper_force_violations > 0:
                    violation_cycles = cycles_array[violations_mask]
                    violation_forces = force_upper_array[violations_mask]
                    self.curves['force_upper_violations'].setData(violation_cycles, violation_forces)
                else:
                    self.curves['force_upper_violations'].setData([], [])
            else:
                # Clear violations if thresholds disabled
                self.curves['force_upper_violations'].setData([], [])
                self.upper_force_violations = 0
            
            # Update travel plot (Plot 2)
            self.curves['travel_at_upper'].setData(cycles_array, np.array(self.travel_at_upper))
            self.curves['travel_1'].setData(cycles_array, np.array(self.travel_1))
            self.curves['travel_2'].setData(cycles_array, np.array(self.travel_2))
            
            # Update loss of stiffness plot (Plot 3)
            self.curves['loss_stiffness'].setData(cycles_array, stiffness_array)
            
            # Check Stiffness thresholds and highlight violations
            if self.stiffness_thresholds_enabled:
                # Find violations
                violations_mask = (stiffness_array > self.stiffness_upper_limit) | \
                                 (stiffness_array < self.stiffness_lower_limit)
                
                # Count violations
                self.stiffness_violations = np.sum(violations_mask)
                
                # Get violation points
                if self.stiffness_violations > 0:
                    violation_cycles = cycles_array[violations_mask]
                    violation_stiffness = stiffness_array[violations_mask]
                    self.curves['stiffness_violations'].setData(violation_cycles, violation_stiffness)
                else:
                    self.curves['stiffness_violations'].setData([], [])
            else:
                # Clear violations if thresholds disabled
                self.curves['stiffness_violations'].setData([], [])
                self.stiffness_violations = 0
            
            self.points_plotted = len(cycles_array)
            
        except Exception as e:
            print(f"[LivePlotter] Error updating plots: {e}")
    
    def clear_plots(self):
        """Clear all plot data"""
        self.cycles.clear()
        self.force_lower.clear()
        self.force_upper.clear()
        self.travel_1.clear()
        self.travel_2.clear()
        self.travel_at_upper.clear()
        self.loss_of_stiffness.clear()
        
        # Clear curves
        for curve in self.curves.values():
            curve.setData([], [])
        
        # Reset counters
        self.points_received = 0
        self.points_plotted = 0
        self.upper_force_violations = 0
        self.stiffness_violations = 0
        
        print("[LivePlotter] Cleared all plots")
    
    def get_statistics(self) -> dict:
        """Get plotting statistics including threshold violations"""
        return {
            'points_received': self.points_received,
            'points_plotted': self.points_plotted,
            'buffer_size': len(self.cycles),
            'update_interval_ms': self.config.update_interval_ms,
            'upper_force_violations': self.upper_force_violations,
            'upper_force_thresholds_enabled': self.upper_force_thresholds_enabled,
            'stiffness_violations': self.stiffness_violations,
            'stiffness_thresholds_enabled': self.stiffness_thresholds_enabled
        }
    
    def set_update_interval(self, interval_ms: int):
        """
        Change plot update interval
        
        Args:
            interval_ms: Update interval in milliseconds
        """
        self.config.update_interval_ms = interval_ms
        self.update_timer.setInterval(interval_ms)
        print(f"[LivePlotter] Update interval set to {interval_ms}ms")
    
    def enable_auto_range(self, enable: bool):
        """
        Enable or disable auto-ranging
        
        Args:
            enable: True to enable auto-range, False to disable
        """
        self.config.auto_range = enable
        for plot in self.plots.values():
            if enable:
                plot.enableAutoRange()
            else:
                plot.disableAutoRange()
    
    def set_upper_force_thresholds(self, upper_limit: float, lower_limit: float, enabled: bool):
        """
        Set thresholds for Upper Force plot
        
        Args:
            upper_limit: Upper threshold value [N]
            lower_limit: Lower threshold value [N]
            enabled: Enable threshold checking
        """
        self.upper_force_upper_limit = upper_limit
        self.upper_force_lower_limit = lower_limit
        self.upper_force_thresholds_enabled = enabled
        
        # Show/hide threshold lines
        if enabled and self.threshold_lines:
            self.threshold_lines['upper_force_upper'].setVisible(True)
            self.threshold_lines['upper_force_upper'].setValue(upper_limit)
            self.threshold_lines['upper_force_lower'].setVisible(True)
            self.threshold_lines['upper_force_lower'].setValue(lower_limit)
        elif self.threshold_lines:
            self.threshold_lines['upper_force_upper'].setVisible(False)
            self.threshold_lines['upper_force_lower'].setVisible(False)
        
        # Reset violation counter
        self.upper_force_violations = 0
        
        print(f"[LivePlotter] Upper Force thresholds: [{lower_limit}, {upper_limit}] N, Enabled: {enabled}")
    
    def set_stiffness_thresholds(self, upper_limit: float, lower_limit: float, enabled: bool):
        """
        Set thresholds for Loss of Stiffness plot
        
        Args:
            upper_limit: Upper threshold value [%]
            lower_limit: Lower threshold value [%]
            enabled: Enable threshold checking
        """
        self.stiffness_upper_limit = upper_limit
        self.stiffness_lower_limit = lower_limit
        self.stiffness_thresholds_enabled = enabled
        
        # Show/hide threshold lines
        if enabled and self.threshold_lines:
            self.threshold_lines['stiffness_upper'].setVisible(True)
            self.threshold_lines['stiffness_upper'].setValue(upper_limit)
            self.threshold_lines['stiffness_lower'].setVisible(True)
            self.threshold_lines['stiffness_lower'].setValue(lower_limit)
        elif self.threshold_lines:
            self.threshold_lines['stiffness_upper'].setVisible(False)
            self.threshold_lines['stiffness_lower'].setVisible(False)
        
        # Reset violation counter
        self.stiffness_violations = 0
        
        print(f"[LivePlotter] Stiffness thresholds: [{lower_limit}, {upper_limit}] %, Enabled: {enabled}")
