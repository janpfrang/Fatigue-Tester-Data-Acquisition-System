# Software Requirements Specification
## Fatigue Tester Data Acquisition System

---

## Document Information

| Field | Value |
|-------|-------|
| **Project** | Fatigue Tester Data Acquisition System |
| **Document Type** | Software Requirements Specification (SRS) |
| **Document Version** | 2.0 |
| **Date** | February 5, 2026 |
| **Status** | Approved |
| **Author** | [Your Name/Team] |
| **Approved By** | [Approver Name] |
| **Next Review Date** | [Date] |

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | [Original] | [Author] | Initial requirements |
| 2.0 | Feb 5, 2026 | [Author] | Updated plotting requirements, added Help/Version menus, unlimited points |

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 Purpose
   - 1.2 Scope
   - 1.3 Definitions and Acronyms
   - 1.4 References
   - 1.5 Overview

2. [Overall Description](#2-overall-description)
   - 2.1 Product Perspective
   - 2.2 Product Functions
   - 2.3 User Characteristics
   - 2.4 Constraints
   - 2.5 Assumptions and Dependencies

3. [Functional Requirements](#3-functional-requirements)
   - 3.1 Serial Data Acquisition
   - 3.2 Data Logging
   - 3.3 Live Data Plotting
   - 3.4 User Interface
   - 3.5 Data Processing

4. [Non-Functional Requirements](#4-non-functional-requirements)
   - 4.1 Performance Requirements
   - 4.2 Safety Requirements
   - 4.3 Security Requirements
   - 4.4 Software Quality Attributes
   - 4.5 Other Requirements

5. [Data Specifications](#5-data-specifications)
   - 5.1 Serial Data Format
   - 5.2 CSV File Format
   - 5.3 Error Codes

6. [Interface Requirements](#6-interface-requirements)
   - 6.1 User Interfaces
   - 6.2 Hardware Interfaces
   - 6.3 Software Interfaces
   - 6.4 Communications Interfaces

7. [Appendices](#7-appendices)
   - 7.1 Requirements Traceability Matrix
   - 7.2 Change Log

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document describes the functional and non-functional requirements for the Fatigue Tester Data Acquisition System. This system is designed to receive, log, and visualize real-time data from fatigue testing equipment via serial communication.

**Intended audience for this document includes:**
- Software developers implementing the system
- Test engineers validating the system
- Quality assurance personnel
- Project stakeholders
- Maintenance personnel

### 1.2 Scope

**Product Name:** Fatigue Tester Data Acquisition System

**The system shall provide:**
- Real-time serial data acquisition from fatigue testing equipment
- Automatic CSV logging with timestamp-based file naming
- Live visualization with three configurable plots
- Loss of stiffness calculation and monitoring
- User-friendly GUI with help system
- Mock data mode for testing without hardware

**Out of Scope:**
- Control of fatigue testing equipment
- Advanced data analysis beyond Loss of Stiffness
- Database integration
- Network/remote access capabilities
- Multi-device simultaneous monitoring

### 1.3 Definitions and Acronyms

| Acronym | Definition |
|---------|------------|
| **CSV** | Comma-Separated Values |
| **GUI** | Graphical User Interface |
| **Hz** | Hertz (frequency unit, cycles per second) |
| **mm** | Millimeter |
| **N** | Newton (force unit) |
| **PC** | Personal Computer |
| **SRS** | Software Requirements Specification |
| **UI** | User Interface |

### 1.4 References

- [1] "Fatigue Tester Architecture" - Software architecture document
- [2] IEEE Std 830-1998 - IEEE Recommended Practice for Software Requirements Specifications

### 1.5 Overview

This document is organized into seven sections:
- **Section 1:** Introduction (this section)
- **Section 2:** Overall description of the system
- **Section 3:** Detailed functional requirements
- **Section 4:** Non-functional requirements
- **Section 5:** Data format specifications
- **Section 6:** Interface requirements
- **Section 7:** Appendices

---

## 2. Overall Description

### 2.1 Product Perspective

The Fatigue Tester Data Acquisition System is a standalone desktop application that interfaces with fatigue testing equipment via serial communication. It operates on Windows, Linux, or macOS platforms and requires no server infrastructure.

**System Context:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   Fatigue       â”‚  Serial  â”‚  Data            â”‚
â”‚   Testing    â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€>â”‚  Acquisition  â”€â”€â”€â”¼â”€â”€> CSV Files
â”‚   Equipment     â”‚  Data    â”‚  System          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜          â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                      â”‚
                                      â””â”€â”€> Real-time Plots
```

### 2.2 Product Functions

The system provides the following major functions:

**1. Serial Data Acquisition**
- Connects to test equipment via serial port
- Receives data at 0.1 to 1.0 second intervals
- Configurable serial parameters

**2. Data Logging**
- Automatic CSV file creation with timestamps
- No overwriting of existing files
- Complete data preservation

**3. Live Visualization**
- Three real-time plots (Forces, Travel, Loss of Stiffness)
- Auto-ranging axes
- Unlimited data points
- 1-second update interval

**4. Data Processing**
- Parsing and validation of serial data
- Loss of stiffness calculation
- Error detection and reporting

**5. User Interface**
- Graphical controls for connection management
- Help and version information menus
- Statistics display
- Status logging

### 2.3 User Characteristics

**Primary Users:** Test engineers and laboratory technicians

**Characteristics:**
- Familiar with fatigue testing procedures
- Basic computer skills
- May not have programming experience
- Require reliable, easy-to-use interface
- Need to focus on test execution, not software operation

**Secondary Users:** Data analysts

**Characteristics:**
- Work with exported CSV files
- Require consistent data format
- May use various analysis tools (Excel, MATLAB, Python, etc.)

### 2.4 Constraints

**Hardware Constraints:**
- Requires serial port or USB-to-Serial adapter
- Minimum 4 GB RAM recommended
- 100 MB disk space required

**Software Constraints:**
- Requires Python 3.8 or higher
- Requires specific Python packages (pyserial, PyQt5, etc.)
- Operating System: Windows 7+, Linux (Ubuntu 18.04+), macOS 10.13+

**Regulatory Constraints:**
- None identified

**Standards Compliance:**
- CSV files must use standard format for interoperability
- Serial communication follows RS-232 standard

### 2.5 Assumptions and Dependencies

**Assumptions:**
- Test equipment sends data in the specified format
- Serial communication is stable and reliable
- User has appropriate permissions to access serial ports
- User has basic understanding of fatigue testing

**Dependencies:**
- Python runtime environment
- PyQt5 GUI framework
- pyserial library for serial communication
- pyqtgraph for plotting
- pandas for data management
- Test equipment must be configured to send data in specified format

---

## 3. Functional Requirements

Requirements are organized hierarchically with the following structure:
- **REQ-XXX:** High-level requirement
  - **REQ-XXX.Y:** Detailed sub-requirement

**Priority Levels:**
- **[MUST]** - Critical requirement, system cannot function without it
- **[SHOULD]** - Important requirement, significant value
- **[COULD]** - Desirable requirement, nice to have

### 3.1 Serial Data Acquisition

#### REQ-001: Serial Communication [MUST]

**Description:**  
The system shall receive serial data from fatigue testing equipment via RS-232 serial communication.

**Acceptance Criteria:**
- System can connect to specified COM port
- System receives data successfully
- Data transmission errors are detected and logged
- Connection status is visible to user

##### REQ-001.1: Data Reception Rate [MUST]

**Description:**  
The system shall receive data at intervals between 0.1 and 1.0 seconds.

**Acceptance Criteria:**
- System handles data arriving every 0.1 seconds (10 Hz)
- System handles data arriving every 1.0 seconds (1 Hz)
- System handles variable data rates within this range
- No data loss occurs at any supported rate

**Test Method:**
- Connect with mock data at 10 Hz â†’ Verify all data received
- Connect with mock data at 1 Hz â†’ Verify all data received
- Verify Lines Received counter matches expected count

##### REQ-001.2: Serial Parameter Configuration [MUST]

**Description:**  
The system shall allow configuration of serial communication parameters within the application.

**Acceptance Criteria:**
- User can select COM port from available ports
- User can select baudrate (common rates: 9600, 19200, 38400, 57600, 115200)
- Default baudrate is 115200 (v2.0)
- Settings are applied before connection
- Invalid settings are rejected with clear error message

**Test Method:**
- Select different COM ports â†’ Verify selection saved
- Select different baudrates â†’ Verify connection works
- Test with invalid port â†’ Verify error message displayed

##### REQ-001.3: Connection Management [MUST]

**Description:**  
The system shall provide controls to establish and terminate serial connections.

**Acceptance Criteria:**
- "Connect" button initiates connection
- "Disconnect" button terminates connection
- Connection status is clearly indicated
- User cannot modify settings while connected
- Application can be closed safely while connected

**Test Method:**
- Click Connect â†’ Verify connection established
- Click Disconnect â†’ Verify connection terminated
- Verify settings locked while connected

##### REQ-001.4: Data Reception Buffer [MUST]

**Description:**  
The system shall use buffered data reception to prevent data loss during temporary system delays.

**Acceptance Criteria:**
- Incoming data queued if processing temporarily delayed
- Buffer size adequate for expected data rates
- Buffer overflow detected and logged
- No data loss under normal operating conditions

**Test Method:**
- Simulate high data rate â†’ Verify no data loss
- Monitor queue size during operation

### 3.2 Data Logging

#### REQ-002: CSV Data Logging [MUST]

**Description:**  
The system shall log all received and successfully parsed data to CSV files.

**Acceptance Criteria:**
- Data logged in CSV format
- CSV files created automatically
- All valid data points are logged
- Files are accessible after test completion

##### REQ-002.1: CSV File Creation [MUST]

**Description:**  
The system shall create CSV files with timestamp-based naming upon connection.

**Acceptance Criteria:**
- File created when connection established
- Filename format: `fatigue_test_YYYYMMDD_HHMMSS.csv`
- File created in `logs/` subdirectory
- `logs/` directory created automatically if not present

**Test Method:**
- Connect to mock data â†’ Verify file created
- Verify filename format matches specification
- Check file location in `logs/` directory

##### REQ-002.2: No Data Overwriting [MUST]

**Description:**  
The system shall never overwrite existing data files.

**Acceptance Criteria:**
- If filename exists, append counter (e.g., `_01`, `_02`)
- User warned before any potential data loss
- Previous test data remains intact
- Each test session creates unique file

**Test Method:**
- Create file with timestamp name
- Connect again with same timestamp â†’ Verify `_01` appended
- Verify original file unchanged

##### REQ-002.3: CSV Format Specification [MUST]

**Description:**  
The system shall use standardized CSV format compatible with common analysis tools.

**Acceptance Criteria:**
- Standard comma-separated values format
- Header row with column names
- Consistent column order across all files
- No missing or extra columns
- Compatible with Excel, MATLAB, Python pandas

**Test Method:**
- Open CSV in Excel â†’ Verify readable
- Import into Python pandas â†’ Verify successful parse
- Verify all specified columns present

##### REQ-002.4: Data Completeness [MUST]

**Description:**  
The system shall log all successfully parsed data without gaps or omissions.

**Acceptance Criteria:**
- Every valid data point is logged
- Points Logged counter matches valid data received
- Malformed data is excluded (but counted as parse error)
- Timestamp for each data point

**Test Method:**
- Send 1000 valid data points â†’ Verify 1000 in CSV
- Send mix of valid/invalid â†’ Verify only valid logged
- Check Parse Errors counter matches discarded data

##### REQ-002.5: User-Requested Save [SHOULD]

**Description:**  
The system shall allow users to save current log with custom filename.

**Acceptance Criteria:**
- "Save Log As..." button available
- File dialog allows custom filename selection
- Original log file remains
- Copy created with user-specified name

**Test Method:**
- Click "Save Log As..."
- Enter custom filename
- Verify both files exist (original and copy)

### 3.3 Live Data Plotting

#### REQ-003: Real-Time Visualization [MUST]

**Description:**  
The system shall provide real-time visualization of test data with three separate plots.

**Acceptance Criteria:**
- Three plots displayed simultaneously
- Data updates in real-time
- All plots clearly labeled
- Axes auto-range as data changes

##### REQ-003.1: Plot 1 - Forces [MUST]

**Description:**  
Plot 1 shall display Lower Force and Upper Force versus Cycles.

**Acceptance Criteria:**
- Two traces: Lower Force (blue) and Upper Force (red)
- X-axis: Cycles (number)
- Y-axis: Force [N]
- Legend identifying each trace
- Grid lines for readability

**Test Method:**
- Connect to mock data
- Verify two traces appear
- Verify colors match specification
- Verify axis labels correct

##### REQ-003.2: Plot 2 - Travel Measurements [MUST]

**Description:**  
Plot 2 shall display Travel at Upper Force, Additional Travel 1, and Additional Travel 2 versus Cycles.

**Acceptance Criteria:**
- Three traces displayed:
  - Travel at Upper Force [mm] (green)
  - Additional Travel 1 [mm] (cyan)
  - Additional Travel 2 [mm] (magenta)
- X-axis: Cycles
- Y-axis: Travel [mm]
- Legend identifying all traces

**Test Method:**
- Connect to mock data
- Verify three traces appear
- Verify correct data on each trace
- Verify axis labels

##### REQ-003.3: Plot 3 - Loss of Stiffness [MUST]

**Description:**  
Plot 3 shall display Loss of Stiffness percentage versus Cycles.

**Acceptance Criteria:**
- Single trace: Loss of Stiffness [%] (orange)
- X-axis: Cycles
- Y-axis: Loss of Stiffness [%]
- Value calculated as: (Travel 2 / Travel at Upper) Ã— 100
- Handle division by zero (display 0%)

**Test Method:**
- Connect to mock data
- Verify calculation correct
- Test with Travel at Upper = 0 â†’ Verify no crash
- Verify percentage values displayed

##### REQ-003.4: Auto-Ranging [MUST]

**Description:**  
The system shall automatically adjust X and Y axis ranges as data is received and plotted.

**Acceptance Criteria:**
- Axes expand to show all data
- No data clipped off screen
- User can see latest data without manual adjustment
- Auto-ranging can be toggled on/off by user

**Test Method:**
- Start with small data range â†’ Add large values
- Verify axes expand to show all data
- Disable auto-range â†’ Verify axes fixed
- Enable auto-range â†’ Verify axes resume adjustment

##### REQ-003.5: Plot Update Rate [MUST]

**Description:**  
The system shall update plots at maximum rate of 1 Hz (once per second) or at data reception rate if lower.

**Acceptance Criteria:**
- Default update interval: 1000 ms (1 second)
- If data arrives slower than 1 Hz, update at data rate
- Update rate configurable by user (100-5000 ms)
- No excessive CPU usage from plotting

**Test Method:**
- Connect with 10 Hz data â†’ Verify plots update at 1 Hz
- Connect with 0.5 Hz data â†’ Verify plots update at 0.5 Hz
- Change update interval setting â†’ Verify applied

##### REQ-003.6: Negative Value Support [MUST]

**Description:**  
The system shall plot negative values for force and position measurements without error.

**Acceptance Criteria:**
- Negative force values plotted correctly
- Negative position values plotted correctly
- No error messages for negative values
- Axes scale appropriately for negative ranges

**Test Method:**
- Send data with negative force â†’ Verify plotted
- Send data with negative position â†’ Verify plotted
- Verify no error messages in console
- Verify axis range includes negative values

##### REQ-003.7: Unlimited Data Points [MUST]

**Description:**  
The system shall plot all received data without imposing artificial point limits, subject to system memory constraints.

**Acceptance Criteria:**
- No arbitrary cutoff (e.g., not limited to 1000 points)
- All data from test start remains visible
- Points Plotted counter continues increasing
- Graceful handling if memory limits reached

**Test Method:**
- Run test with 10,000+ data points
- Verify all points visible in plots
- Verify no old data dropped
- Monitor memory usage remains reasonable

##### REQ-003.8: Plot Controls [SHOULD]

**Description:**  
The system shall provide user controls for plot customization.

**Acceptance Criteria:**
- Update interval adjustable (100-5000 ms)
- Auto-range toggle available
- "Clear Plots" button available
- Controls clearly labeled

**Test Method:**
- Adjust update interval â†’ Verify change applied
- Toggle auto-range â†’ Verify behavior changes
- Click Clear Plots â†’ Verify plots cleared

### 3.4 User Interface

#### REQ-004: Graphical User Interface [MUST]

**Description:**  
The system shall provide a graphical user interface for all user interactions.

**Acceptance Criteria:**
- All functions accessible via GUI
- No command-line interaction required for normal operation
- Interface intuitive for target users
- Consistent layout and design

##### REQ-004.1: Connection Controls [MUST]

**Description:**  
The GUI shall provide controls for establishing and terminating connections.

**Acceptance Criteria:**
- COM port selection dropdown
- Baudrate selection dropdown
- Connect/Disconnect button (toggle)
- Connection status indicator
- Mock data mode checkbox

**Test Method:**
- Verify all controls present
- Test each control functions correctly
- Verify status updates appropriately

##### REQ-004.2: Data Logging Controls [MUST]

**Description:**  
The GUI shall provide controls for data logging operations.

**Acceptance Criteria:**
- Current log filename displayed
- "Save Log As..." button
- "Start New Log" button
- Logging status clearly indicated

**Test Method:**
- Verify filename display updates
- Test each button functions correctly

##### REQ-004.3: Help Menu [MUST]

**Description:**  
The GUI shall provide a Help menu with documentation access.

**Acceptance Criteria:**
- "Help" menu in menu bar
- "Help Documentation" option opens help dialog
- "About" option shows application information
- Help content includes:
  - Quick start guide
  - Plot descriptions
  - Data logging instructions
  - Troubleshooting tips

**Test Method:**
- Click Help menu â†’ Verify opens
- Click Help Documentation â†’ Verify dialog displays
- Verify content completeness

##### REQ-004.4: Version Menu [MUST]

**Description:**  
The GUI shall provide a Version menu showing version information.

**Acceptance Criteria:**
- "Version" menu in menu bar
- "Version Information" option opens version dialog
- Version dialog includes:
  - Application version number
  - Release date
  - Requirements version
  - Component versions
  - Update history

**Test Method:**
- Click Version menu â†’ Verify opens
- Click Version Information â†’ Verify dialog displays
- Verify all information present and accurate

##### REQ-004.5: Statistics Display [MUST]

**Description:**  
The GUI shall display real-time statistics about system operation.

**Acceptance Criteria:**
- Statistics panel always visible
- Updates automatically (approximately 1 Hz)
- Displays:
  - Connection time
  - Lines received
  - Points logged
  - Points plotted
  - Parse errors
- Values formatted clearly

**Test Method:**
- Connect to mock data
- Verify all statistics present
- Verify statistics update in real-time
- Verify values accurate

##### REQ-004.6: Status Log [SHOULD]

**Description:**  
The GUI shall display a log of system events and errors.

**Acceptance Criteria:**
- Status log area visible
- Shows timestamped events
- Errors displayed in red
- Scrollable for long logs
- "Clear Log" button available

**Test Method:**
- Connect/disconnect â†’ Verify events logged
- Trigger error â†’ Verify displayed in red
- Verify timestamps present

### 3.5 Data Processing

#### REQ-005: Data Parsing and Validation [MUST]

**Description:**  
The system shall parse incoming serial data and validate its correctness.

**Acceptance Criteria:**
- All valid data parsed successfully
- Invalid data detected and rejected
- Parse errors logged and counted
- System continues operating after parse errors

##### REQ-005.1: Data Format Parsing [MUST]

**Description:**  
The system shall parse serial data according to specified format.

**Acceptance Criteria:**
- Correctly interprets 11-field semicolon-separated format
- Applies proper decimal conversion (e.g., 182 â†’ 1.82 mm)
- Extracts all fields correctly
- Handles end marker (!)

**Test Method:**
- Send valid data â†’ Verify all fields extracted correctly
- Verify decimal conversions accurate
- Check parsed values match expected

##### REQ-005.2: Data Validation [MUST]

**Description:**  
The system shall validate parsed data for basic correctness.

**Acceptance Criteria:**
- Verifies correct field count (10 data fields)
- Validates status field (DTA or END)
- Validates cycle count (non-negative)
- Allows negative values for force and position
- Invalid data rejected with explanation

**Test Method:**
- Send data with wrong field count â†’ Verify rejected
- Send data with invalid status â†’ Verify rejected
- Send data with negative force â†’ Verify accepted
- Check console for error explanations

##### REQ-005.3: Parse Error Handling [MUST]

**Description:**  
The system shall handle parse errors gracefully without crashing.

**Acceptance Criteria:**
- Parse errors logged to console with data shown
- Parse error counter incremented
- Invalid data discarded (not logged or plotted)
- System continues processing subsequent data
- Error rate displayed to user

**Test Method:**
- Send invalid data â†’ Verify system continues
- Verify parse error counter increments
- Verify invalid data not in CSV or plots
- Check console for error messages

##### REQ-005.4: Loss of Stiffness Calculation [MUST]

**Description:**  
The system shall calculate Loss of Stiffness for each data point.

**Acceptance Criteria:**
- Formula: (Additional Travel 2 / Travel at Upper) Ã— 100
- Result in percentage (%)
- Handle division by zero (return 0%)
- Calculation included in CSV output
- Value plotted in Plot 3

**Test Method:**
- Verify calculation formula correct
- Test with Travel at Upper = 0 â†’ Verify returns 0%
- Check CSV contains Loss_of_Stiffness_Percent column
- Verify Plot 3 shows calculated values

##### REQ-005.5: Error Code Interpretation [SHOULD]

**Description:**  
The system shall interpret error codes and provide descriptions.

**Acceptance Criteria:**
- Error code mapped to human-readable description
- Description included in CSV output
- Critical errors highlighted in status log
- Unknown error codes handled gracefully

**Test Method:**
- Send data with error code 0 â†’ Verify "No Error"
- Send data with error code 11 â†’ Verify correct description
- Send data with unknown code â†’ Verify graceful handling

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

#### REQ-NFR-001: Data Throughput [MUST]

**Description:**  
The system shall handle data rates up to 10 Hz (0.1 second intervals) without data loss.

**Acceptance Criteria:**
- No data loss at 10 Hz continuous operation
- Parse success rate > 95% (excluding equipment errors)
- CPU usage < 25% on modern hardware
- Memory usage < 500 MB for 24-hour test

**Test Method:**
- Run 1-hour test at 10 Hz â†’ Verify data complete
- Monitor CPU and memory usage

#### REQ-NFR-002: Plot Rendering Performance [MUST]

**Description:**  
The system shall maintain responsive plotting even with large datasets.

**Acceptance Criteria:**
- Plot updates complete within 100 ms
- No GUI freezing during updates
- Smooth operation with 10,000+ data points
- Interactive controls remain responsive

**Test Method:**
- Run test with 10,000+ points
- Verify plots update smoothly
- Test user controls during operation

#### REQ-NFR-003: Startup Time [SHOULD]

**Description:**  
The system shall start and be ready for operation quickly.

**Acceptance Criteria:**
- Application launches within 5 seconds
- GUI fully responsive within 10 seconds
- No excessive delay before connection possible

**Test Method:**
- Measure time from launch to GUI ready
- Verify meets criteria on target hardware

### 4.2 Safety Requirements

#### REQ-NFR-004: Data Integrity [MUST]

**Description:**  
The system shall never corrupt or lose logged data.

**Acceptance Criteria:**
- No data overwriting
- All valid data preserved
- File system errors detected and reported
- Graceful handling of disk full condition

**Test Method:**
- Fill disk to near capacity â†’ Verify error handling
- Force close application â†’ Verify data preserved
- Check data integrity after abnormal shutdown

#### REQ-NFR-005: Error Detection [MUST]

**Description:**  
The system shall detect and report all error conditions.

**Acceptance Criteria:**
- Parse errors detected and counted
- Communication errors reported
- File system errors reported
- No silent failures

**Test Method:**
- Introduce various error conditions
- Verify all are detected and reported

### 4.3 Security Requirements

#### REQ-NFR-006: Data Access [SHOULD]

**Description:**  
The system shall use appropriate file permissions for logged data.

**Acceptance Criteria:**
- Files created with standard user permissions
- No unnecessary elevated privileges required
- CSV files readable by data analysis tools

**Test Method:**
- Check file permissions on created files
- Verify application runs without admin rights

### 4.4 Software Quality Attributes

#### REQ-NFR-007: Reliability [MUST]

**Description:**  
The system shall operate continuously without crashing.

**Acceptance Criteria:**
- Mean Time Between Failures (MTBF) > 100 hours
- Graceful error recovery
- No memory leaks
- Stable operation over extended periods

**Test Method:**
- 24-hour continuous operation test
- Monitor memory usage over time
- Verify no crashes or hangs

#### REQ-NFR-008: Usability [MUST]

**Description:**  
The system shall be easy to use for target users.

**Acceptance Criteria:**
- New users can start basic operation within 5 minutes
- Help documentation readily accessible
- Clear error messages
- Intuitive controls

**Test Method:**
- User testing with representative users
- Measure time to first successful test
- Collect user feedback

#### REQ-NFR-009: Maintainability [SHOULD]

**Description:**  
The system shall be easy to maintain and modify.

**Acceptance Criteria:**
- Modular architecture
- Code documentation present
- Configuration externalized
- Changes localized to specific modules

**Test Method:**
- Code review
- Test modification scenarios
- Verify documentation completeness

#### REQ-NFR-010: Portability [SHOULD]

**Description:**  
The system shall operate on multiple operating systems.

**Acceptance Criteria:**
- Works on Windows 10/11
- Works on Ubuntu Linux 18.04+
- Works on macOS 10.13+
- Consistent behavior across platforms

**Test Method:**
- Install and test on each platform
- Verify all features work consistently

### 4.5 Other Requirements

#### REQ-NFR-011: Mock Data Mode [MUST]

**Description:**  
The system shall provide mock data mode for testing without hardware.

**Acceptance Criteria:**
- Checkbox to enable mock mode
- Generates realistic test data
- Same data flow as real hardware
- Useful for training and testing

**Test Method:**
- Enable mock mode â†’ Connect
- Verify data generated and processed
- Verify all features work in mock mode

---

## 5. Data Specifications

### 5.1 Serial Data Format

#### Format Description

The serial data consists of 11 semicolon-separated fields ending with an exclamation mark.

**Format Template:**
```
<STATUS>;<CYCLES>;<POS1>;<FORCE_L>;<TRAV1>;<POS2>;<FORCE_U>;<TRAV2>;<TRAV_U>;<CODE>;!
```

**Example:**
```
DTA;31422;182;263;0;793;2238;0;611;0;!
```

#### Field Specifications

| Field # | Name | Type | Description | Conversion | Example |
|---------|------|------|-------------|------------|---------|
| 1 | Status | String | Test status | - | `DTA` or `END` |
| 2 | Cycles | Integer | Number of test cycles | - | `31422` |
| 3 | Position 1 | Integer | Position 1 in mm | Ã· 100 | `182` â†’ 1.82 mm |
| 4 | Force Lower | Integer | Lower force in N | Ã· 10 | `263` â†’ 26.3 N |
| 5 | Travel 1 | Integer | Additional travel 1 in mm | Ã· 100 | `0` â†’ 0.00 mm |
| 6 | Position 2 | Integer | Position 2 in mm | Ã· 100 | `793` â†’ 7.93 mm |
| 7 | Force Upper | Integer | Upper force in N | Ã· 10 | `2238` â†’ 223.8 N |
| 8 | Travel 2 | Integer | Additional travel 2 in mm | Ã· 100 | `0` â†’ 0.00 mm |
| 9 | Travel at Upper | Integer | Total travel at Upper Force in mm | Ã· 100 | `611` â†’ 6.11 mm |
| 10 | Error Code | Integer | Error/status code (see Section 5.3) | - | `0` |
| 11 | End Marker | Character | End of transmission | - | `!` |

**Note:** Fields 5, 8 can be negative values.

#### Line Ending

Lines may end with any standard line ending (`\n`, `\r\n`, or `\r`). The parser strips whitespace and the "!" marker before processing.

#### Data Validation Rules

1. Must have exactly 10 semicolons (creating 11 fields)
2. Must end with "!" character
3. Field 1 must be "DTA" or "END"
4. Fields 2-10 must be valid integers
5. Field 2 (Cycles) must be non-negative
6. Fields 3-9 can be negative (per V2 requirements)
7. Field 10 must be a valid error code (0-999)

### 5.2 CSV File Format

#### CSV Structure

The CSV file contains a header row followed by data rows.

**Header Row:**
```
Timestamp,Status,Cycles,Position_1_mm,Force_Lower_N,Travel_1_mm,Position_2_mm,Force_Upper_N,Travel_2_mm,Travel_at_Upper_mm,Loss_of_Stiffness_Percent,Error_Code,Error_Description,Raw_Data
```

#### Column Descriptions

| Column | Format | Type | Description |
|--------|--------|------|-------------|
| Timestamp | `YYYY-MM-DD HH:MM:SS.mmm` | String | Date and time when data was received |
| Status | `DTA` or `END` | String | Test status |
| Cycles | - | Integer | Number of cycles |
| Position_1_mm | 2 decimal places | Float | Position 1 in millimeters |
| Force_Lower_N | 1 decimal place | Float | Lower force in Newtons |
| Travel_1_mm | 2 decimal places | Float | Additional travel 1 in millimeters |
| Position_2_mm | 2 decimal places | Float | Position 2 in millimeters |
| Force_Upper_N | 1 decimal place | Float | Upper force in Newtons |
| Travel_2_mm | 2 decimal places | Float | Additional travel 2 in millimeters |
| Travel_at_Upper_mm | 2 decimal places | Float | Travel at Upper Force in millimeters |
| Loss_of_Stiffness_Percent | 2 decimal places | Float | (Travel_2_mm / Travel_at_Upper_mm) Ã— 100 |
| Error_Code | - | Integer | Numeric error code |
| Error_Description | - | String | Human-readable error description |
| Raw_Data | - | String | Original unprocessed serial data |

#### File Naming Convention

**Base Format:** `fatigue_test_<TIMESTAMP>.csv`  
Where `<TIMESTAMP>` is: `YYYYMMDD_HHMMSS`

**Example:** `fatigue_test_20260205_143215.csv`

**If file exists, append counter:**
- `fatigue_test_20260205_143215_01.csv`
- `fatigue_test_20260205_143215_02.csv`

#### File Location

**Default Directory:** `./logs/`  
**Full Path Example:** `./logs/fatigue_test_20260205_143215.csv`

The `logs/` directory is created automatically if it does not exist.

### 5.3 Error Codes

#### Error Code Table

| Code | Category | Description |
|------|----------|-------------|
| 000 | No Error | Everything is OK |
| 010 | Test Failed | The test was completed with an error |
| 011 | Path Violation | Additional path 1 exceeded permissible tolerance |
| 012 | Path Violation | Additional path 2 exceeded permissible tolerance |
| 013 | Force Limit | Force 2 fell below the permissible limit |
| 014 | Force Limit | Force 2 exceeded the permissible limit |
| 101 | Motor Error | Voice Coil drive could not be initialized |
| 102 | Motor Error | Communication error with Voice Coil drive |
| 103 | Reference | No reference position was set |
| 104 | Motor Error | Voice Coil drive is not ready |
| 106 | Motor Error | Voice Coil drive not initialized correctly |
| 107 | Motor Error | Voice Coil drive is blocked |
| 201 | Travel Error | Resulting actuation travel is too small |
| 202 | Force Search | Target force 1 already reached at start of search |
| 203 | Force Search | Target force 2 already reached at start of search |
| 204 | Force Search | Target force 1 could not be built up |
| 205 | Force Search | Target force 2 could not be built up |

**Note:** Error codes in the range 1-999 are valid. Unknown codes should be handled gracefully with a generic "Unknown Error" description.

---

## 6. Interface Requirements

### 6.1 User Interfaces

#### Main Window Layout

The main window is divided into two primary sections:

**Left Panel (Control Area):**
- Connection settings group
- Data logging controls group
- Plot settings group
- Statistics display
- Status log

**Right Panel (Visualization Area):**
- Three vertically stacked plots
- Equal height allocation
- Synchronized X-axes (Cycles)

#### Menu Bar

**Help Menu:**
- Help Documentation (opens help dialog)
- About (shows application info)

**Version Menu:**
- Version Information (opens version dialog)

#### Dialog Windows

**1. Help Dialog**
- HTML-formatted content
- Scrollable
- OK button to close

**2. Version Dialog**
- Version information table
- Component versions
- OK button to close

**3. Save File Dialog**
- Standard file save dialog
- Default to `logs/` directory
- Filter: CSV files (`*.csv`)

### 6.2 Hardware Interfaces

#### Serial Port Interface

**Physical Interface:** RS-232 serial port or USB-to-Serial adapter

**Connection Parameters:**
- **Baud Rate:** Configurable (common: 9600, 19200, 38400, 57600, 115200), default 115200 (v2.0)
- **Data Bits:** 8
- **Parity:** None
- **Stop Bits:** 1
- **Flow Control:** None

**Electrical Specifications:** Per RS-232 standard

### 6.3 Software Interfaces

#### Python Libraries

| Library | Version | Purpose | Interface |
|---------|---------|---------|-----------|
| pyserial | â‰¥3.5 | Serial port communication | `serial.Serial` class |
| PyQt5 | â‰¥5.15.0 | GUI framework | Qt widgets and signals/slots |
| pyqtgraph | â‰¥0.13.0 | Real-time plotting | `PlotWidget`, `PlotItem` classes |
| pandas | â‰¥1.5.0 | Data manipulation | `DataFrame` class |
| numpy | â‰¥1.23.0 | Numerical operations | Array operations |

#### Operating System Interfaces

**File System:**
- Read/Write access to application directory
- Create and write to `logs/` subdirectory
- Standard file permissions

**Serial Port Access:**
- Platform-specific serial port enumeration
- Permission to access serial devices (may require user to be in dialout group on Linux)

### 6.4 Communications Interfaces

#### Serial Communication Protocol

**Protocol:** ASCII text over RS-232  
**Data Format:** Semicolon-separated values  
**Line Termination:** Any standard (CRLF, LF, or CR)  
**Error Detection:** None at protocol level (handled by application)  
**Flow Control:** None  
**Timing:** Asynchronous, data-driven

**Data Flow:**  
Test Equipment â†’ Serial Port â†’ Application

No bidirectional communication required. Application is receive-only for data acquisition.

---

## 7. Appendices

### 7.1 Requirements Traceability Matrix

This matrix maps requirements to implementation modules and test cases.

| Requirement | Module | Test Case | Status |
|-------------|--------|-----------|--------|
| REQ-001 | serial_reader.py | TC-001 | Implemented |
| REQ-001.1 | serial_reader.py | TC-001.1 | Implemented |
| REQ-001.2 | config.py, GUI | TC-001.2 | Implemented |
| REQ-001.3 | main_application.py | TC-001.3 | Implemented |
| REQ-001.4 | serial_reader.py | TC-001.4 | Implemented |
| REQ-002 | data_logger.py | TC-002 | Implemented |
| REQ-002.1 | data_logger.py | TC-002.1 | Implemented |
| REQ-002.2 | data_logger.py | TC-002.2 | Implemented |
| REQ-002.3 | data_logger.py | TC-002.3 | Implemented |
| REQ-002.4 | data_logger.py | TC-002.4 | Implemented |
| REQ-002.5 | main_application.py | TC-002.5 | Implemented |
| REQ-003 | live_plotter.py | TC-003 | Implemented |
| REQ-003.1 | live_plotter.py | TC-003.1 | Implemented |
| REQ-003.2 | live_plotter.py | TC-003.2 | Implemented |
| REQ-003.3 | live_plotter.py | TC-003.3 | Implemented |
| REQ-003.4 | live_plotter.py | TC-003.4 | Implemented |
| REQ-003.5 | live_plotter.py | TC-003.5 | Implemented |
| REQ-003.6 | data_parser.py | TC-003.6 | Implemented |
| REQ-003.7 | live_plotter.py | TC-003.7 | Implemented |
| REQ-003.8 | main_application.py | TC-003.8 | Implemented |
| REQ-004 | main_application.py | TC-004 | Implemented |
| REQ-004.1 | main_application.py | TC-004.1 | Implemented |
| REQ-004.2 | main_application.py | TC-004.2 | Implemented |
| REQ-004.3 | main_application.py | TC-004.3 | Implemented |
| REQ-004.4 | main_application.py | TC-004.4 | Implemented |
| REQ-004.5 | main_application.py | TC-004.5 | Implemented |
| REQ-004.6 | main_application.py | TC-004.6 | Implemented |
| REQ-005 | data_parser.py | TC-005 | Implemented |
| REQ-005.1 | data_parser.py | TC-005.1 | Implemented |
| REQ-005.2 | data_parser.py | TC-005.2 | Implemented |
| REQ-005.3 | data_parser.py | TC-005.3 | Implemented |
| REQ-005.4 | data_parser.py | TC-005.4 | Implemented |
| REQ-005.5 | config.py | TC-005.5 | Implemented |
| REQ-NFR-001 | All modules | TC-NFR-001 | Implemented |
| REQ-NFR-002 | live_plotter.py | TC-NFR-002 | Implemented |
| REQ-NFR-011 | serial_reader.py | TC-NFR-011 | Implemented |

### 7.2 Change Log

#### Version 2.0 (February 5, 2026)

**Changes from Version 1.0:**

**1. Field Naming Updates:**
- `Position_0_mm` â†’ `Position_1_mm`
- `Travel_Lower_mm` â†’ `Travel_1_mm`
- `Position_Upper_mm` â†’ `Position_2_mm`
- `Travel_Upper_mm` â†’ `Travel_2_mm`

**2. Plot Requirements Changed:**
- **REQ-003.2:** Plot 2 now shows Travel measurements instead of Positions
- **REQ-003.3:** Added new Plot 3 for Loss of Stiffness

**3. Data Processing Updates:**
- **REQ-003.6:** Added requirement to accept negative values
- **REQ-003.7:** Added requirement for unlimited data points
- **REQ-005.4:** Added Loss of Stiffness calculation

**4. User Interface Updates:**
- **REQ-004.3:** Added Help menu requirement
- **REQ-004.4:** Added Version menu requirement
- **New:** Added "Serial Data Logger and Plotter - User Manual" menu item (v2.0 final)

**5. Configuration Updates:**
- **config.py:** Default baudrate changed from 9600 to 115200 (v2.0 final)
- **REQ-001.2:** Updated baudrate default to 115200

**6. CSV Format Updates:**
- **Section 5.2:** Added `Loss_of_Stiffness_Percent` column
- Updated field names to match new nomenclature

**Rationale:**
- Improved field naming clarity
- Enhanced monitoring capabilities with Loss of Stiffness
- Better support for long-duration tests (unlimited points)
- Improved user support (Help and Version menus, User Manual)
- More flexible data acceptance (negative values)
- Higher baudrate (115200) for better performance with modern equipment

---

## Document Approval

This document has been reviewed and approved by:

| Name | Role | Signature | Date |
|------|------|-----------|------|
| ____________________ | Project Manager | ______________ | __________ |
| ____________________ | Technical Lead | ______________ | __________ |
| ____________________ | Quality Assurance | ______________ | __________ |

---

**END OF REQUIREMENTS SPECIFICATION**
