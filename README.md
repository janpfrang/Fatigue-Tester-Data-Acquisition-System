# Fatigue Tester Data Acquisition System

Professional data acquisition system for fatigue testing equipment with real-time
visualization, comprehensive data logging, test traceability, and PDF report generation.

**Version:** 2.3 (Phase 2 Refactored + PDF Export) - February 16, 2026  
**Contact:** Uwe Hasenstab and Alexander Waal

## Features

- Real-time serial data acquisition (0.1 - 1.0s intervals)
- Three synchronized live plots (Forces, Travel, Loss of Stiffness)
- Automatic CSV logging with timestamp-based naming
- Professional PDF report generation with matplotlib
- Machine Configuration display (decoded CNF header from device)
- Threshold monitoring for Upper Force and Loss of Stiffness
- Real-time violation detection and visualization
- COM port auto-detection with port selection dialog
- Loss of stiffness calculation and monitoring
- Watchdog timer for connection monitoring
- Mock data mode for testing without hardware
- Unlimited data points (no artificial limits)
- Negative value support for force and position
- Complete test traceability (device ID, setup parameters in every CSV)
- Modular architecture (56% code reduction from v2.2)

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python main_application.py`
3. Click "Detect Ports" and select your COM port (or enable Mock Data for testing)
4. Click "Connect" - data flows, plots update, CSV logging starts automatically
5. Open Advanced Options -> Advanced Settings to view Machine Configuration and export PDF

## Advanced Options Dialog

The Advanced Options dialog (menu: Advanced Options -> Advanced Settings) provides:

- **Export Plots to PDF** - Generate professional multi-page PDF reports
- **Machine Configuration (CNF Header)** - Displays decoded device parameters:
  Kraft @2/@1 (force targets), Kraftabschaltung (emergency cutoff),
  Toleranz (force tolerance band), Nachregelweg (position-correction budgets),
  Betaetigungen (planned cycles), Messen alle N (log interval), Device ID
- **Force Analysis** - Percentage of values exceeding Upper Force Limit x 1.03

## Architecture

Layered, event-driven design using the Producer-Consumer pattern with thread-safe
communication and hardware abstraction.

**Modules:**

- `main_application.py` - Main orchestration and GUI (683 lines)
- `config.py` - Configuration constants
- `data_parser.py` - Serial data and CNF header parsing
- `serial_reader.py` - RS-232 communication with mock support
- `data_logger.py` - CSV logging with header preservation
- `live_plotter.py` - Three synchronized real-time plots
- `threshold_monitor.py` - Violation detection logic
- `statistics_tracker.py` - Statistics tracking
- `plot_exporter.py` - PDF generation with matplotlib
- UI panels: `connection_panel.py`, `logging_panel.py`, `plot_settings_panel.py`,
  `statistics_panel.py`, `status_log_panel.py`
- `serial_port_detector.py` - Cross-platform COM port detection
- `port_selection_dialog.py` - User-friendly port selection UI

## Requirements

- Python 3.8+
- pyserial >= 3.5
- PyQt5 >= 5.15.0
- pyqtgraph >= 0.13.0
- pandas >= 1.5.0
- numpy >= 1.23.0
- matplotlib >= 3.5.0

## Documentation

- `USER_MANUAL_V23.html` - Complete user manual
- `Fatigue_Tester_Architecture.pdf` - System architecture document
- Help menu in application - Built-in help documentation

## Data Format

Serial input: `DTA;[Cycles];[Pos1];[ForceLower];[Travel1];[Pos2];[ForceUpper];[Travel2];[TravelAtUpper];[Reserved];!`

CSV output: Standard CSV with comment-based metadata headers, compatible with
Excel, MATLAB, Python pandas.
