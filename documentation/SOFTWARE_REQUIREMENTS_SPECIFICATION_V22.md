# Software Requirements Specification (SRS)
## Fatigue Tester Data Acquisition System - V2.2

---

## Document Information

| Field | Value |
|-------|-------|
| **Project** | Fatigue Tester Data Acquisition System |
| **Document Type** | Software Requirements Specification (SRS) |
| **Document Version** | 2.2 |
| **Date** | February 12, 2026 |
| **Status** | Current - Production Ready |
| **Author** | Uwe Hasenstab and Alexander Waal |

---

## Revision History

| Version | Date | Key Changes |
|---------|------|------------|
| 1.0 | [Original] | Initial requirements |
| 2.0 | Feb 5, 2026 | Three plots, unlimited points, negative values support |
| 2.1 | Feb 12, 2026 | Line filtering for headers/config (no parse errors) |
| 2.2 | Feb 12, 2026 | Header logging, port detection, threshold monitoring |

---

## Executive Summary

The Fatigue Tester Data Acquisition System V2.2 is a comprehensive desktop application for acquiring, logging, and visualizing real-time data from fatigue testing equipment. It implements professional-grade data handling with complete test traceability, intelligent port detection, and threshold-based violation monitoring.

**Key Features:**
- Real-time serial data acquisition (0.1-1.0 second intervals)
- Automatic CSV logging with device headers and configuration preservation
- Three synchronized real-time plots with unlimited data points
- Threshold monitoring with violation detection and visualization
- Intelligent COM port auto-detection with selection dialog
- Professional GUI with Help/Version documentation system
- Mock data mode for testing without hardware
- Complete backward compatibility with existing data formats

---

## 1. Functional Requirements

### 1.1 Serial Data Acquisition [REQ-001]

**Requirement:**  
The system shall receive serial data from fatigue testing equipment via RS-232/USB-Serial communication at configurable parameters.

**Acceptance Criteria:**
- ✅ Connect to specified COM port successfully
- ✅ Receive data at intervals between 0.1-1.0 seconds (10 Hz to 1 Hz)
- ✅ Handle data transmission errors gracefully
- ✅ Display connection status to user
- ✅ Support multiple OS (Windows, Linux, macOS)

**Sub-Requirements:**

#### 1.1.1 Port Detection [REQ-001.1] - NEW in V2.2
**Requirement:**  
The system shall automatically detect available serial ports on startup.

**Acceptance Criteria:**
- ✅ Auto-detect COM ports without user intervention
- ✅ Display detected ports in dropdown
- ✅ Provide "Detect Ports" button for manual re-scan
- ✅ Show port descriptions when available
- ✅ Handle port enumeration failures gracefully with fallback

**Implementation:**
- `SerialPortDetector` module for cross-platform detection
- Windows: COM1-COM16 enumeration
- Linux: /dev/ttyUSB*, /dev/ttyACM*, /dev/ttyS* scanning
- macOS: /dev/tty.*, /dev/cu.* pattern matching

#### 1.1.2 Port Selection Dialog [REQ-001.2] - NEW in V2.2
**Requirement:**  
The system shall provide an interactive port selection dialog for choosing from detected ports.

**Acceptance Criteria:**
- ✅ Dialog shows all detected ports with descriptions
- ✅ Indicate port availability status (✓ Available)
- ✅ Double-click port to select and auto-connect
- ✅ Select button for confirmation
- ✅ Refresh button to re-detect ports

**Implementation:**
- `PortSelectionDialog` class with professional UI
- Color-coded status indicators
- Real-time port enumeration
- Smart fallback to Fatigue Tester if found

#### 1.1.3 Configurable Serial Parameters [REQ-001.3]
**Requirement:**  
Serial connection parameters shall be user-configurable via GUI.

**Acceptance Criteria:**
- ✅ COM port selectable from dropdown (auto-populated)
- ✅ Baudrate selectable: 4800, 9600, 19200, 38400, 57600, 115200
- ✅ Default baudrate: 115200
- ✅ Settings applied before connection
- ✅ Invalid settings rejected with error message

#### 1.1.4 Connection Management [REQ-001.4]
**Requirement:**  
The system shall provide controls to establish and terminate connections.

**Acceptance Criteria:**
- ✅ "Connect" button initiates connection
- ✅ "Disconnect" button terminates connection
- ✅ Button text changes to indicate state
- ✅ Settings locked while connected
- ✅ Safe disconnect on application close

#### 1.1.5 Mock Data Mode [REQ-001.5]
**Requirement:**  
The system shall provide mock data mode for testing without hardware.

**Acceptance Criteria:**
- ✅ Checkbox to enable mock mode
- ✅ Generates realistic test data
- ✅ Same processing pipeline as real hardware
- ✅ Useful for training and UI testing

### 1.2 Data Logging [REQ-002]

**Requirement:**  
The system shall log all received and successfully parsed data to CSV files with complete metadata preservation.

**Sub-Requirements:**

#### 1.2.1 CSV File Creation [REQ-002.1]
**Requirement:**  
CSV files shall be created automatically upon connection with timestamp-based naming.

**Acceptance Criteria:**
- ✅ File created immediately on connection
- ✅ Filename format: `fatigue_test_YYYYMMDD_HHMMSS.csv`
- ✅ Location: `logs/` subdirectory
- ✅ Directory created automatically if not present

#### 1.2.2 Header & Configuration Logging [REQ-002.2] - NEW in V2.2
**Requirement:**  
The system shall capture and preserve all device header information and configuration data transmitted before the first data line.

**Acceptance Criteria:**
- ✅ All header lines captured (### VoiceCoilTestStand, For display, Loading, CNF)
- ✅ Headers written as comment lines (# prefix) at top of CSV
- ✅ Comment section clearly marked:
  - `# ===== DEVICE HEADER INFORMATION =====`
  - `# ===== DATA BEGINS BELOW =====`
- ✅ Headers written only once per file
- ✅ Standard CSV tools ignore comment lines
- ✅ Excel/pandas/MATLAB compatible (comments auto-skipped)

**Purpose:**
- Preserve device serial number/ID for equipment traceability
- Preserve complete test configuration (CNF line with ~196 parameters)
- Enable test reproducibility from configuration
- Provide complete audit trail

**CSV Format Example:**
```csv
# ===== DEVICE HEADER INFORMATION =====
# ### VoiceCoilTestStand V1.5 ID=2BC4D630 ###
# For display ceSID-48339C75
# Loading... Adr: '1' (0x31). Ok!
# CNF;49;0;0;0;0;220;0;152;8;152;8;44;1;44;1;...;!
# ===== DATA BEGINS BELOW =====
Timestamp,Status,Cycles,...
```

#### 1.2.3 Data Completeness [REQ-002.3]
**Requirement:**  
The system shall log all successfully parsed data without gaps or omissions.

**Acceptance Criteria:**
- ✅ Every valid data point logged
- ✅ Points Logged counter matches valid data received
- ✅ Malformed data excluded but counted
- ✅ Timestamp for each data point
- ✅ 3 millisecond precision in timestamps

#### 1.2.4 No Data Overwriting [REQ-002.4]
**Requirement:**  
The system shall never overwrite existing data files.

**Acceptance Criteria:**
- ✅ If filename exists, append counter (_01, _02, etc.)
- ✅ User warned before potential data loss
- ✅ Previous test data remains intact
- ✅ Each session creates unique file

#### 1.2.5 CSV Format Specification [REQ-002.5]
**Requirement:**  
CSV files shall use standardized format compatible with common analysis tools.

**Acceptance Criteria:**
- ✅ Standard comma-separated values format
- ✅ Header row with column names
- ✅ Consistent column order
- ✅ No missing or extra columns
- ✅ Compatible with Excel, MATLAB, Python pandas

**Columns:**
```
Timestamp, Status, Cycles, Position_1_mm, Force_Lower_N, Travel_1_mm,
Position_2_mm, Force_Upper_N, Travel_2_mm, Travel_at_Upper_mm,
Loss_of_Stiffness_Percent, Error_Code, Error_Description, Raw_Data
```

### 1.3 Live Data Visualization [REQ-003]

**Requirement:**  
The system shall provide real-time visualization of test data with three coordinated plots.

**Sub-Requirements:**

#### 1.3.1 Plot 1: Forces vs Cycles [REQ-003.1]
**Requirement:**  
Display Lower Force and Upper Force versus cycle count.

**Specifications:**
- **Traces:**
  - Lower Force [N] (blue line)
  - Upper Force [N] (red line)
  - Upper Force Violations (red circles, when thresholds enabled)
- **Axes:** X = Cycles, Y = Force [N]
- **Features:** Legend, grid, auto-range

#### 1.3.2 Plot 2: Travel Measurements vs Cycles [REQ-003.2]
**Requirement:**  
Display three travel measurements versus cycle count.

**Specifications:**
- **Traces:**
  - Travel at Upper Force [mm] (green line)
  - Additional Travel 1 [mm] (cyan line)
  - Additional Travel 2 [mm] (magenta line)
- **Axes:** X = Cycles, Y = Travel [mm]
- **Features:** Legend, grid, auto-range

#### 1.3.3 Plot 3: Loss of Stiffness vs Cycles [REQ-003.3]
**Requirement:**  
Display calculated Loss of Stiffness percentage versus cycle count.

**Specifications:**
- **Trace:**
  - Loss of Stiffness [%] (orange line)
  - Violations (orange circles, when thresholds enabled)
- **Calculation:** `(Travel_2 / Travel_at_Upper) × 100`
- **Axes:** X = Cycles, Y = Loss of Stiffness [%]
- **Special Handling:** Division by zero returns 0%

#### 1.3.4 Auto-Ranging [REQ-003.4]
**Requirement:**  
Automatically adjust axis ranges as data is received.

**Acceptance Criteria:**
- ✅ Axes expand to show all data
- ✅ No data clipped off screen
- ✅ Auto-ranging can be toggled on/off
- ✅ Manual panning/zooming possible

#### 1.3.5 Plot Update Rate [REQ-003.5]
**Requirement:**  
Update plots at configurable maximum rate of 1 Hz.

**Acceptance Criteria:**
- ✅ Default update interval: 1000 ms
- ✅ If data slower than 1 Hz, update at data rate
- ✅ User-configurable: 100-5000 ms
- ✅ No excessive CPU usage

#### 1.3.6 Negative Value Support [REQ-003.6]
**Requirement:**  
Plot negative values for force and position without error.

**Acceptance Criteria:**
- ✅ Negative force values plotted correctly
- ✅ Negative position values plotted correctly
- ✅ No error messages for negative values
- ✅ Axes scale appropriately

#### 1.3.7 Unlimited Data Points [REQ-003.7]
**Requirement:**  
Plot all received data without artificial point limits.

**Acceptance Criteria:**
- ✅ No cutoff (e.g., not limited to 1000 points)
- ✅ All data from test start visible
- ✅ Points Plotted counter continues increasing
- ✅ Graceful handling if memory limits reached

#### 1.3.8 Threshold Visualization [REQ-003.8] - NEW in V2.2
**Requirement:**  
Display threshold limits and violation markers on plots.

**Acceptance Criteria:**
- ✅ Threshold limit lines displayed (dashed)
- ✅ Upper Force thresholds: red dashed lines
- ✅ Stiffness thresholds: orange dashed lines
- ✅ Lines positioned at threshold values
- ✅ Lines visible when thresholds enabled, hidden when disabled
- ✅ Violation markers (circles) overlaid on violations

### 1.4 Threshold Monitoring [REQ-004] - NEW in V2.2

**Requirement:**  
The system shall monitor Upper Force and Loss of Stiffness against user-defined limits with violation detection and reporting.

**Sub-Requirements:**

#### 1.4.1 Upper Force Thresholds [REQ-004.1]
**Requirement:**  
Users shall set upper and lower limits for Upper Force values.

**Specifications:**
- **Upper Limit [N]:** -99999 to 99999 (default: 1000.0)
- **Lower Limit [N]:** -99999 to 99999 (default: -1000.0)
- **Step:** 10.0 N
- **Precision:** 2 decimal places
- **Enable/Disable:** Checkbox to activate monitoring
- **Visual Feedback:** Red threshold lines and violation markers

**Violation Detection:**
```python
violation = (Upper_Force > upper_limit) OR (Upper_Force < lower_limit)
```

#### 1.4.2 Loss of Stiffness Thresholds [REQ-004.2]
**Requirement:**  
Users shall set upper and lower limits for Loss of Stiffness values.

**Specifications:**
- **Upper Limit [%]:** -99999 to 99999 (default: 100.0)
- **Lower Limit [%]:** -99999 to 99999 (default: 0.0)
- **Step:** 1.0 %
- **Precision:** 2 decimal places
- **Enable/Disable:** Checkbox to activate monitoring
- **Visual Feedback:** Orange threshold lines and violation markers

**Violation Detection:**
```python
violation = (Stiffness > upper_limit) OR (Stiffness < lower_limit)
```

#### 1.4.3 Real-Time Violation Counting [REQ-004.3]
**Requirement:**  
The system shall count and display violations in real-time.

**Acceptance Criteria:**
- ✅ Violation counter increments immediately
- ✅ Statistics panel shows: "Violations: X / Total Points"
- ✅ Separate counters for each threshold set
- ✅ Counters reset when thresholds enabled/disabled
- ✅ Counters update with each new data point

#### 1.4.4 Violation Visualization [REQ-004.4]
**Requirement:**  
Out-of-range data points shall be highlighted on plots.

**Acceptance Criteria:**
- ✅ Violation markers appear at out-of-range points
- ✅ Upper Force violations: red circles (size 10)
- ✅ Stiffness violations: orange circles (size 10)
- ✅ Markers clearly visible against line plots
- ✅ Markers update in real-time as violations detected

#### 1.4.5 Dynamic Threshold Adjustment [REQ-004.5]
**Requirement:**  
Thresholds shall be adjustable during test operation.

**Acceptance Criteria:**
- ✅ Changes take effect immediately
- ✅ Plot visualization updates immediately
- ✅ Violation counters reset on threshold change
- ✅ Previous data re-evaluated against new limits
- ✅ No data loss during threshold change

### 1.5 User Interface [REQ-005]

**Requirement:**  
Provide intuitive GUI for all system operations.

**Sub-Requirements:**

#### 1.5.1 Connection Controls [REQ-005.1]
**Specifications:**
- COM port dropdown (auto-populated from detection)
- Baudrate dropdown (default: 115200)
- Connect/Disconnect toggle button
- "🔋 Detect Ports" button for port selection dialog - NEW in V2.2
- "Use Mock Data (Testing)" checkbox
- Connection status indicator

#### 1.5.2 Data Logging Controls [REQ-005.2]
**Specifications:**
- Current log filename display (updated in real-time)
- "Save Log As..." button
- "Start New Log" button
- Logging status indicator

#### 1.5.3 Plot Settings Group [REQ-005.3]
**Specifications:**
- Update Interval spin box (100-5000 ms, default: 1000)
- Auto Range checkbox (default: enabled)
- Clear Plots button
- Separator line
- **Upper Force Thresholds Section:** - NEW in V2.2
  - Enable checkbox
  - Upper Limit spin box
  - Lower Limit spin box
- Separator line
- **Loss of Stiffness Thresholds Section:** - NEW in V2.2
  - Enable checkbox
  - Upper Limit spin box
  - Lower Limit spin box

#### 1.5.4 Statistics Panel [REQ-005.4]
**Specifications:**
- Connection Time
- Lines Received
- Points Logged
- Points Plotted
- Buffer Size
- Parse Errors
- Upper Force Violations (when enabled) - NEW in V2.2
- Stiffness Violations (when enabled) - NEW in V2.2
- Updates approximately every 1 second

#### 1.5.5 Status Log [REQ-005.5]
**Specifications:**
- Timestamped status messages
- Error messages in red
- Scrollable history
- Clear Log button
- Shows all significant events

#### 1.5.6 Menu Bar [REQ-005.6]
**Specifications:**
- **Help Menu:**
  - Help Documentation
  - About
  - (Version menu is separate)
- **Version Menu:**
  - Version Information

#### 1.5.7 Help Documentation [REQ-005.7]
**Requirement:**  
Comprehensive user manual shall be accessible from GUI.

**Acceptance Criteria:**
- ✅ Help Documentation opens in dialog
- ✅ Content displayed in HTML format
- ✅ Scrollable with readable font
- ✅ Includes quick start, operations, troubleshooting
- ✅ Contact information included

#### 1.5.8 About & Version Dialogs [REQ-005.8]
**Specifications:**
- About: Application name, version, date, contact, description
- Version Information: Version number, release date, component versions, Python requirements

### 1.6 Data Processing [REQ-006]

**Requirement:**  
Parse, validate, and process incoming serial data.

**Sub-Requirements:**

#### 1.6.1 Data Format Parsing [REQ-006.1]
**Requirement:**  
Parse serial data according to device format specification.

**Format:**
```
DTA;31422;182;263;0;793;2238;0;611;0;!
```

**Fields (11 total):**
1. Status: "DTA" or "END"
2. Cycles: Integer
3. Position 1: Integer (÷100 = mm)
4. Force Lower: Integer (÷10 = N)
5. Travel 1: Integer (÷100 = mm)
6. Position 2: Integer (÷100 = mm)
7. Force Upper: Integer (÷10 = N)
8. Travel 2: Integer (÷100 = mm)
9. Travel at Upper: Integer (÷100 = mm)
10. Error Code: Integer (0-999)
11. End Marker: "!"

#### 1.6.2 Header Line Filtering [REQ-006.2]
**Requirement:**  
Filter header and configuration lines to prevent parse errors.

**Lines Filtered:**
- Empty lines
- Lines starting with ### (device headers)
- Lines starting with "For display" (display info)
- Lines starting with "Loading" (status messages)
- Lines starting with "CNF;" (configuration)

**Lines Accepted:**
- Lines starting with "DTA;" (data)
- Lines starting with "END;" (end markers)

#### 1.6.3 Data Validation [REQ-006.3]
**Requirement:**  
Validate parsed data for correctness.

**Acceptance Criteria:**
- ✅ Verify field count (10 data fields)
- ✅ Validate status field ("DTA" or "END")
- ✅ Validate cycle count (non-negative)
- ✅ Allow negative values for force/position
- ✅ Reject invalid data with explanation

#### 1.6.4 Error Code Interpretation [REQ-006.4]
**Requirement:**  
Map error codes to human-readable descriptions.

**Acceptance Criteria:**
- ✅ All error codes mapped to descriptions
- ✅ Descriptions included in CSV output
- ✅ Unknown codes handled gracefully
- ✅ Critical errors highlighted in status log

#### 1.6.5 Loss of Stiffness Calculation [REQ-006.5]
**Requirement:**  
Calculate Loss of Stiffness for each data point.

**Formula:**
```
Loss_of_Stiffness [%] = (Travel_2 / Travel_at_Upper) × 100

If Travel_at_Upper = 0: return 0%
```

**Acceptance Criteria:**
- ✅ Formula applied correctly
- ✅ Division by zero handled
- ✅ Result in percentage
- ✅ Included in CSV output
- ✅ Plotted in Plot 3

---

## 2. Non-Functional Requirements

### 2.1 Performance [REQ-NFR-001]

**Requirement:**  
The system shall handle data rates up to 10 Hz without data loss.

**Acceptance Criteria:**
- ✅ No data loss at 10 Hz continuous
- ✅ Parse success rate > 95% (excluding equipment errors)
- ✅ CPU usage < 25% on modern hardware
- ✅ Memory usage < 500 MB for 24-hour test
- ✅ Plot rendering < 100 ms per update
- ✅ Startup time < 5 seconds
- ✅ GUI responsive during operations

### 2.2 Reliability [REQ-NFR-002]

**Requirement:**  
The system shall operate continuously without crashes.

**Acceptance Criteria:**
- ✅ MTBF > 100 hours
- ✅ Graceful error recovery
- ✅ No memory leaks
- ✅ Stable over extended periods
- ✅ Watchdog timer monitors data reception
- ✅ Alerts if no data > 5 seconds

### 2.3 Data Integrity [REQ-NFR-003]

**Requirement:**  
The system shall never corrupt or lose logged data.

**Acceptance Criteria:**
- ✅ No data overwriting
- ✅ All valid data preserved
- ✅ File system errors detected/reported
- ✅ Graceful disk full handling
- ✅ Safe shutdown without data loss

### 2.4 Usability [REQ-NFR-004]

**Requirement:**  
The system shall be easy to use for target engineers.

**Acceptance Criteria:**
- ✅ New users can start operation within 5 minutes
- ✅ Help easily accessible
- ✅ Clear error messages
- ✅ Intuitive controls
- ✅ Professional UI design

### 2.5 Portability [REQ-NFR-005]

**Requirement:**  
The system shall operate on multiple operating systems.

**Acceptance Criteria:**
- ✅ Windows 7+
- ✅ Ubuntu Linux 18.04+
- ✅ macOS 10.13+
- ✅ Consistent behavior across platforms

### 2.6 Maintainability [REQ-NFR-006]

**Requirement:**  
The system shall be easy to maintain and modify.

**Acceptance Criteria:**
- ✅ Modular architecture
- ✅ Code documentation present
- ✅ Configuration externalized
- ✅ Changes localized to modules

### 2.7 Backward Compatibility [REQ-NFR-007]

**Requirement:**  
The system shall be 100% backward compatible with previous versions.

**Acceptance Criteria:**
- ✅ Existing CSV files still load correctly
- ✅ Comment lines auto-skipped by standard tools
- ✅ All previous features functional
- ✅ No breaking changes
- ✅ Old configuration files work

---

## 3. Data Specifications

### 3.1 Serial Data Format

**Example:**
```
DTA;31422;182;263;0;793;2238;0;611;0;!
```

**Field Breakdown:**

| Field | Name | Type | Conversion | Example |
|-------|------|------|-----------|---------|
| 1 | Status | String | - | DTA/END |
| 2 | Cycles | Integer | - | 31422 |
| 3 | Position 1 | Integer | ÷100 | 182→1.82mm |
| 4 | Force Lower | Integer | ÷10 | 263→26.3N |
| 5 | Travel 1 | Integer | ÷100 | 0→0.00mm |
| 6 | Position 2 | Integer | ÷100 | 793→7.93mm |
| 7 | Force Upper | Integer | ÷10 | 2238→223.8N |
| 8 | Travel 2 | Integer | ÷100 | 0→0.00mm |
| 9 | Travel at Upper | Integer | ÷100 | 611→6.11mm |
| 10 | Error Code | Integer | - | 0 |
| 11 | End Marker | Char | - | ! |

**Validation Rules:**
- Exactly 10 semicolons (11 fields)
- Must end with "!"
- Field 1: "DTA" or "END"
- Fields 2-10: valid integers
- Field 2: non-negative
- Fields 3-9: can be negative
- Field 10: 0-999

### 3.2 CSV File Structure - V2.2 Format

```csv
# ===== DEVICE HEADER INFORMATION =====
# ### VoiceCoilTestStand V1.5 ID=2BC4D630 ###
# For display ceSID-48339C75
# Loading... Adr: '1' (0x31). Ok!
# CNF;49;0;0;0;0;220;0;152;8;...;!
# ===== DATA BEGINS BELOW =====
Timestamp,Status,Cycles,Position_1_mm,Force_Lower_N,Travel_1_mm,Position_2_mm,Force_Upper_N,Travel_2_mm,Travel_at_Upper_mm,Loss_of_Stiffness_Percent,Error_Code,Error_Description,Raw_Data
2026-02-09 14:30:22.145,DTA,11,0.78,2.9,0.00,11.95,219.9,0.00,11.17,0.00,0,No Error,DTA;11;78;29;0;1195;2199;0;1117;0;!
```

### 3.3 Error Codes

| Code | Category | Description |
|------|----------|-------------|
| 000 | No Error | Everything OK |
| 010 | Test Failed | Test completed with error |
| 011 | Path Violation | Path 1 exceeded tolerance |
| 012 | Path Violation | Path 2 exceeded tolerance |
| 101 | Motor Error | Voice Coil init failed |
| 102 | Motor Error | Communication error |
| 103 | Reference | No reference position |
| 201-205 | Force Search | Various force search errors |

---

## 4. Technical Architecture

### 4.1 Layered Architecture

```
┌─────────────────────────────────────────┐
│         User Interface (GUI)             │
│      MainWindow, Dialogs, Controls       │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│     Data Processing & Brokering          │
│  DataProcessorWorker, Statistics         │
└──────────────────┬──────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
┌──────────┐ ┌─────────┐ ┌──────────┐
│ Logger   │ │ Plotter │ │  Parser  │
│ (CSV)    │ │(PyQtGrph│ │(Validate)│
└──────────┘ └─────────┘ └──────────┘
      │            │            │
      └────────────┼────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Hardware Abstraction Layer          │
│  SerialReader, PortDetector, Mocking    │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Physical Layer / External System    │
│   Serial Port, File System, OS APIs      │
└──────────────────────────────────────────┘
```

### 4.2 Threading Model

- **Main Thread:** GUI, user interaction
- **SerialReader Thread:** Hardware I/O (background)
- **DataProcessorWorker Thread:** Parsing, validation (background)
- **Plot Update Timer:** Refresh plots at 1 Hz (main thread)

### 4.3 Data Flow

```
Serial Device → SerialReader → Queue → DataProcessor → 
  (Logger + Plotter + Statistics Display)
```

---

## 5. Implementation Status

### ✅ Implemented Features

| Feature | Status | Version |
|---------|--------|---------|
| Serial data acquisition | ✅ Complete | v2.0 |
| CSV logging | ✅ Complete | v2.0 |
| Three real-time plots | ✅ Complete | v2.0 |
| Loss of Stiffness calc | ✅ Complete | v2.0 |
| Negative value support | ✅ Complete | v2.0 |
| Unlimited data points | ✅ Complete | v2.0 |
| Line filtering | ✅ Complete | v2.1 |
| Header logging | ✅ Complete | v2.2 |
| COM port detection | ✅ Complete | v2.2 |
| Port selection dialog | ✅ Complete | v2.2 |
| Threshold monitoring | ✅ Complete | v2.2 |
| Violation visualization | ✅ Complete | v2.2 |
| Help documentation | ✅ Complete | v2.0+ |
| Mock data mode | ✅ Complete | v2.0 |

---

## 6. Dependencies

### Python Packages (requirements.txt)

```
pyserial>=3.5
PyQt5>=5.15.0
pyqtgraph>=0.13.0
pandas>=1.5.0
numpy>=1.23.0
```

### Operating System Requirements

- **Windows:** 7 or later
- **Linux:** Ubuntu 18.04 or later (other distros compatible)
- **macOS:** 10.13 or later
- **Python:** 3.8 or higher

### Hardware Minimum

- RAM: 4 GB
- Disk Space: 100 MB
- Serial Port/USB adapter

---

## 7. Document Control

**Status:** ✅ Production Ready - V2.2  
**Last Updated:** February 12, 2026  
**Version:** 2.2  

For updates and changes, refer to:
- `MAIN_APPLICATION_V22_CHANGELOG.md` - Detailed change log
- `USER_MANUAL.html` - User documentation
- Project source code - Implementation details

---

## Appendix A: Requirements Traceability

All functional requirements (REQ-001 through REQ-006) map to:
- Implementation code modules
- Test cases
- User documentation sections
- GUI controls and dialogs

All non-functional requirements (REQ-NFR-001 through REQ-NFR-007) address:
- Performance metrics
- Reliability standards
- Data protection
- User experience
- System compatibility
- Code quality
- Version continuity

---

**End of Software Requirements Specification - V2.2**
