"""
Live Plotter module - Consumer for real-time visualization
Handles plotting of test data with PyQtGraph - changed on 6 feb in the comment to test workflow
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
        
        # Plot widgets
        self.plot_widget: Optional[pg.GraphicsLayoutWidget] = None
        self.plots = {}
        self.curves = {}
        
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
            
            # Update forces plot (Plot 1)
            self.curves['force_lower'].setData(cycles_array, np.array(self.force_lower))
            self.curves['force_upper'].setData(cycles_array, np.array(self.force_upper))
            
            # Update travel plot (Plot 2)
            self.curves['travel_at_upper'].setData(cycles_array, np.array(self.travel_at_upper))
            self.curves['travel_1'].setData(cycles_array, np.array(self.travel_1))
            self.curves['travel_2'].setData(cycles_array, np.array(self.travel_2))
            
            # Update loss of stiffness plot (Plot 3)
            self.curves['loss_stiffness'].setData(cycles_array, np.array(self.loss_of_stiffness))
            
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
        
        self.points_received = 0
        self.points_plotted = 0
        
        print("[LivePlotter] Cleared all plots")
    
    def get_statistics(self) -> dict:
        """Get plotting statistics"""
        return {
            'points_received': self.points_received,
            'points_plotted': self.points_plotted,
            'buffer_size': len(self.cycles),
            'update_interval_ms': self.config.update_interval_ms
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
