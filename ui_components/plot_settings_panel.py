"""
Plot Settings Panel UI Component
Handles plot configuration and threshold settings
"""

from PyQt5.QtWidgets import (QGroupBox, QGridLayout, QLabel, QSpinBox, 
                             QCheckBox, QPushButton, QDoubleSpinBox, QFrame)
from PyQt5.QtCore import pyqtSignal


class PlotSettingsPanel(QGroupBox):
    """
    Plot settings and threshold configuration panel
    
    Signals:
        update_interval_changed: Plot update interval changed (int: ms)
        auto_range_changed: Auto range toggled (bool: checked)
        clear_plots_clicked: User clicked Clear Plots button
        upper_force_threshold_changed: Upper force threshold settings changed
        stiffness_threshold_changed: Loss of stiffness threshold settings changed
    """
    
    update_interval_changed = pyqtSignal(int)
    auto_range_changed = pyqtSignal(bool)
    clear_plots_clicked = pyqtSignal()
    upper_force_threshold_changed = pyqtSignal()
    stiffness_threshold_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Plot Settings", parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI layout"""
        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setRowMinimumHeight(0, 32)
        
        # Update interval
        layout.addWidget(QLabel("Update Interval (ms):"), 0, 0)
        self.update_interval_spin = QSpinBox()
        self.update_interval_spin.setRange(100, 5000)
        self.update_interval_spin.setValue(1000)
        self.update_interval_spin.setSingleStep(100)
        self.update_interval_spin.valueChanged.connect(self.update_interval_changed.emit)
        self.update_interval_spin.setMinimumHeight(28)
        font = self.update_interval_spin.font()
        font.setPointSize(8)
        self.update_interval_spin.setFont(font)
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
        self.auto_range_check.setChecked(True)
        self.auto_range_check.stateChanged.connect(
            lambda state: self.auto_range_changed.emit(state == 2)
        )
        layout.addWidget(self.auto_range_check, 1, 0, 1, 2)
        
        # Clear plots button
        self.clear_plot_btn = QPushButton("Clear Plots")
        self.clear_plot_btn.clicked.connect(self.clear_plots_clicked.emit)
        layout.addWidget(self.clear_plot_btn, 2, 0, 1, 2)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 3, 0, 1, 2)
        
        # Upper Force Thresholds
        layout.addWidget(QLabel("Upper Force Thresholds:"), 4, 0, 1, 2)
        
        self.upper_force_threshold_check = QCheckBox("Enable Thresholds")
        self.upper_force_threshold_check.stateChanged.connect(self._on_upper_force_threshold_toggled)
        layout.addWidget(self.upper_force_threshold_check, 5, 0, 1, 2)
        
        # Upper Force - Upper Limit
        layout.addWidget(QLabel("  Upper Limit [N]:"), 6, 0)
        self.upper_force_upper_limit_spin = QDoubleSpinBox()
        self.upper_force_upper_limit_spin.setRange(-99999.0, 99999.0)
        self.upper_force_upper_limit_spin.setValue(1000.0)
        self.upper_force_upper_limit_spin.setDecimals(2)
        self.upper_force_upper_limit_spin.setSingleStep(10.0)
        self.upper_force_upper_limit_spin.valueChanged.connect(self.upper_force_threshold_changed.emit)
        self.upper_force_upper_limit_spin.setEnabled(False)
        self._style_spinbox(self.upper_force_upper_limit_spin)
        layout.addWidget(self.upper_force_upper_limit_spin, 6, 1)
        
        # Upper Force - Lower Limit
        layout.addWidget(QLabel("  Lower Limit [N]:"), 7, 0)
        self.upper_force_lower_limit_spin = QDoubleSpinBox()
        self.upper_force_lower_limit_spin.setRange(-99999.0, 99999.0)
        self.upper_force_lower_limit_spin.setValue(-1000.0)
        self.upper_force_lower_limit_spin.setDecimals(2)
        self.upper_force_lower_limit_spin.setSingleStep(10.0)
        self.upper_force_lower_limit_spin.valueChanged.connect(self.upper_force_threshold_changed.emit)
        self.upper_force_lower_limit_spin.setEnabled(False)
        self._style_spinbox(self.upper_force_lower_limit_spin)
        layout.addWidget(self.upper_force_lower_limit_spin, 7, 1)
        
        # Separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2, 8, 0, 1, 2)
        
        # Loss of Stiffness Thresholds
        layout.addWidget(QLabel("Loss of Stiffness Thresholds:"), 9, 0, 1, 2)
        
        self.stiffness_threshold_check = QCheckBox("Enable Thresholds")
        self.stiffness_threshold_check.stateChanged.connect(self._on_stiffness_threshold_toggled)
        layout.addWidget(self.stiffness_threshold_check, 10, 0, 1, 2)
        
        # Loss of Stiffness - Upper Limit
        layout.addWidget(QLabel("  Upper Limit [%]:"), 11, 0)
        self.stiffness_upper_limit_spin = QDoubleSpinBox()
        self.stiffness_upper_limit_spin.setRange(-99999.0, 99999.0)
        self.stiffness_upper_limit_spin.setValue(100.0)
        self.stiffness_upper_limit_spin.setDecimals(2)
        self.stiffness_upper_limit_spin.setSingleStep(1.0)
        self.stiffness_upper_limit_spin.valueChanged.connect(self.stiffness_threshold_changed.emit)
        self.stiffness_upper_limit_spin.setEnabled(False)
        self._style_spinbox(self.stiffness_upper_limit_spin)
        layout.addWidget(self.stiffness_upper_limit_spin, 11, 1)
        
        # Loss of Stiffness - Lower Limit
        layout.addWidget(QLabel("  Lower Limit [%]:"), 12, 0)
        self.stiffness_lower_limit_spin = QDoubleSpinBox()
        self.stiffness_lower_limit_spin.setRange(-99999.0, 99999.0)
        self.stiffness_lower_limit_spin.setValue(0.0)
        self.stiffness_lower_limit_spin.setDecimals(2)
        self.stiffness_lower_limit_spin.setSingleStep(1.0)
        self.stiffness_lower_limit_spin.valueChanged.connect(self.stiffness_threshold_changed.emit)
        self.stiffness_lower_limit_spin.setEnabled(False)
        self._style_spinbox(self.stiffness_lower_limit_spin)
        layout.addWidget(self.stiffness_lower_limit_spin, 12, 1)
        
        # Set column stretch
        layout.setColumnStretch(0, 0)
        layout.setColumnMinimumWidth(0, 140)
        layout.setColumnStretch(1, 1)
        
        self.setLayout(layout)
    
    def _style_spinbox(self, spinbox):
        """Apply consistent styling to spinbox"""
        spinbox.setMinimumHeight(28)
        font = spinbox.font()
        font.setPointSize(8)
        spinbox.setFont(font)
        spinbox.setStyleSheet(
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
    
    def _on_upper_force_threshold_toggled(self):
        """Handle upper force threshold checkbox toggle"""
        enabled = self.upper_force_threshold_check.isChecked()
        self.upper_force_upper_limit_spin.setEnabled(enabled)
        self.upper_force_lower_limit_spin.setEnabled(enabled)
        self.upper_force_threshold_changed.emit()
    
    def _on_stiffness_threshold_toggled(self):
        """Handle stiffness threshold checkbox toggle"""
        enabled = self.stiffness_threshold_check.isChecked()
        self.stiffness_upper_limit_spin.setEnabled(enabled)
        self.stiffness_lower_limit_spin.setEnabled(enabled)
        self.stiffness_threshold_changed.emit()
    
    # Getters for threshold settings
    def is_upper_force_threshold_enabled(self) -> bool:
        return self.upper_force_threshold_check.isChecked()
    
    def get_upper_force_upper_limit(self) -> float:
        return self.upper_force_upper_limit_spin.value()
    
    def get_upper_force_lower_limit(self) -> float:
        return self.upper_force_lower_limit_spin.value()
    
    def is_stiffness_threshold_enabled(self) -> bool:
        return self.stiffness_threshold_check.isChecked()
    
    def get_stiffness_upper_limit(self) -> float:
        return self.stiffness_upper_limit_spin.value()
    
    def get_stiffness_lower_limit(self) -> float:
        return self.stiffness_lower_limit_spin.value()
    
    def set_update_interval(self, interval_ms: int):
        """Set the update interval value"""
        self.update_interval_spin.setValue(interval_ms)
    
    def set_auto_range(self, enabled: bool):
        """Set the auto range checkbox"""
        self.auto_range_check.setChecked(enabled)
