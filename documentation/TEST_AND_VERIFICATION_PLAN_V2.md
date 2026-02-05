# Test and Verification Plan

## Fatigue Tester Data Acquisition System

---

## Document Information

|Field|Value|
|-|-|
|**Project**|Fatigue Tester Data Acquisition System|
|**Document Type**|Test and Verification Plan (TVP)|
|**Document Version**|2.0|
|**Date**|February 5, 2026|
|**Status**|Draft|
|**Author**|\[Your Name/Team]|
|**Related Documents**|Software Requirements Specification V2.0|

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Test Strategy](#2-test-strategy)
3. [Test Environment](#3-test-environment)
4. [Functional Requirements Tests](#4-functional-requirements-tests)
5. [Non-Functional Requirements Tests](#5-non-functional-requirements-tests)
6. [Test Traceability Matrix](#6-test-traceability-matrix)
7. [Test Execution Schedule](#7-test-execution-schedule)
8. [Test Results Summary](#8-test-results-summary)

---

## 1\. Introduction

### 1.1 Purpose

This Test and Verification Plan provides detailed test cases, acceptance criteria, and test methods for verifying that the Fatigue Tester Data Acquisition System meets all specified requirements.

### 1.2 Scope

This document covers:

* Unit testing of individual modules
* Integration testing of system components
* System testing of complete functionality
* Performance and reliability testing
* User acceptance testing criteria

### 1.3 Test Approach

Tests are organized by requirement ID and include:

* **Test ID**: Unique identifier for each test
* **Requirement ID**: Traced to SRS requirement
* **Acceptance Criteria**: Conditions that must be met
* **Test Method**: Procedure to verify requirement
* **Expected Result**: What should happen if system is correct
* **Pass/Fail Criteria**: How to determine test success

---

## 2\. Test Strategy

### 2.1 Test Levels

|Test Level|Description|Responsibility|
|-|-|-|
|**Unit Testing**|Test individual functions and classes|Developer|
|**Integration Testing**|Test module interactions|Developer/QA|
|**System Testing**|Test complete system functionality|QA Team|
|**Performance Testing**|Test system under load|QA Team|
|**User Acceptance Testing**|Validate with end users|Test Engineers|

### 2.2 Test Types

|Test Type|Purpose|Frequency|
|-|-|-|
|**Functional**|Verify feature correctness|Every build|
|**Performance**|Verify speed and resource usage|Weekly|
|**Reliability**|Verify stability over time|Before release|
|**Usability**|Verify ease of use|Before release|
|**Regression**|Verify no new defects|Every build|

### 2.3 Test Tools

|Tool|Purpose|
|-|-|
|**pytest**|Python unit testing framework|
|**Mock Serial Port**|Simulate hardware for testing|
|**PyQt Test Utils**|GUI testing utilities|
|**Memory Profiler**|Monitor memory usage|
|**CPU Monitor**|Monitor CPU usage|

---

## 3\. Test Environment

### 3.1 Hardware Requirements

|Component|Specification|
|-|-|
|**Processor**|Intel Core i5 or equivalent|
|**RAM**|8 GB minimum|
|**Storage**|200 MB free space|
|**Serial Port**|USB-to-Serial adapter or RS-232 port|

### 3.2 Software Requirements

|Software|Version|
|-|-|
|**Python**|3.8+|
|**PyQt5**|5.15.0+|
|**pyserial**|3.5+|
|**pyqtgraph**|0.13.0+|
|**pandas**|1.5.0+|
|**numpy**|1.23.0+|

### 3.3 Test Data

|Data Set|Description|Source|
|-|-|-|
|**Valid Serial Data**|Correctly formatted test data|Mock data generator|
|**Invalid Serial Data**|Malformed data for error testing|Test scripts|
|**Boundary Data**|Edge cases (zero, negative, large values)|Test scripts|
|**Long Duration Data**|10,000+ data points|Mock data generator|

---

## 4\. Functional Requirements Tests

### 4.1 Serial Data Acquisition Tests

#### TC-001: Serial Communication

|Field|Value|
|-|-|
|**Test ID**|TC-001|
|**Requirement**|REQ-001|
|**Priority**|MUST|
|**Description**|Verify system can receive serial data from equipment|

**Acceptance Criteria:**

* \[ ] System can connect to specified COM port
* \[ ] System receives data successfully
* \[ ] Data transmission errors are detected and logged
* \[ ] Connection status is visible to user

**Test Procedure:**

1. Launch application
2. Select available COM port from dropdown
3. Click "Connect" button
4. Observe connection status indicator
5. Verify data reception begins
6. Introduce transmission error (disconnect cable)
7. Verify error is detected and logged

**Expected Results:**

* Connection status shows "Connected"
* Data counter increments
* Errors are logged in status window

**Pass/Fail Criteria:**

* PASS: All acceptance criteria met
* FAIL: Any acceptance criterion not met

---

#### TC-001.1: Data Reception Rate

|Field|Value|
|-|-|
|**Test ID**|TC-001.1|
|**Requirement**|REQ-001.1|
|**Priority**|MUST|
|**Test Type**|Performance|

**Acceptance Criteria:**

* \[ ] System handles data arriving every 0.1 seconds (10 Hz)
* \[ ] System handles data arriving every 1.0 seconds (1 Hz)
* \[ ] System handles variable data rates within range
* \[ ] No data loss occurs at any supported rate

**Test Method:**

|Test Case|Data Rate|Duration|Expected Lines Received|
|-|-|-|-|
|High Rate|10 Hz|60 seconds|600|
|Low Rate|1 Hz|60 seconds|60|
|Variable|0.1-1.0 Hz|60 seconds|60-600|

**Test Procedure:**

1. Enable mock data mode
2. Configure mock data rate to 10 Hz
3. Connect and run for 60 seconds
4. Verify "Lines Received" counter = 600 ± 2
5. Repeat with 1 Hz rate
6. Verify "Lines Received" counter = 60 ± 1
7. Test with variable rate

**Pass/Fail Criteria:**

* PASS: Lines received matches expected ± 2 for all rates
* FAIL: More than 2 lines lost at any rate

---

#### TC-001.2: Serial Parameter Configuration

|Field|Value|
|-|-|
|**Test ID**|TC-001.2|
|**Requirement**|REQ-001.2|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] User can select COM port from available ports
* \[ ] User can select baudrate (9600, 19200, 38400, 57600, 115200)
* \[ ] Settings are applied before connection
* \[ ] Invalid settings rejected with clear error message

**Test Method:**

|Parameter|Test Values|Expected Behavior|
|-|-|-|
|COM Port|COM1, COM3, /dev/ttyUSB0|Dropdown shows available ports|
|Baudrate|9600, 19200, 38400, 57600, 115200|All rates selectable|
|Invalid Port|COM999|Error message displayed|

**Test Procedure:**

1. Open application
2. Click COM port dropdown
3. Verify all available ports listed
4. Select each baudrate from dropdown
5. Verify selection saved
6. Attempt connection with invalid port
7. Verify error message displayed

**Pass/Fail Criteria:**

* PASS: All valid settings accepted, invalid settings rejected with clear message
* FAIL: Valid settings rejected or invalid settings accepted

---

#### TC-001.3: Connection Management

|Field|Value|
|-|-|
|**Test ID**|TC-001.3|
|**Requirement**|REQ-001.3|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] "Connect" button initiates connection
* \[ ] "Disconnect" button terminates connection
* \[ ] Connection status clearly indicated
* \[ ] User cannot modify settings while connected
* \[ ] Application can be closed safely while connected

**Test Procedure:**

|Step|Action|Expected Result|
|-|-|-|
|1|Click Connect button|Connection established, status shows "Connected"|
|2|Try to change COM port|Controls disabled/grayed out|
|3|Try to change baudrate|Controls disabled/grayed out|
|4|Click Disconnect button|Connection terminated, status shows "Disconnected"|
|5|Connect again, close app|Application closes gracefully without errors|

**Pass/Fail Criteria:**

* PASS: All steps execute as expected
* FAIL: Any step fails to meet expected result

---

#### TC-001.4: Data Reception Buffer

|Field|Value|
|-|-|
|**Test ID**|TC-001.4|
|**Requirement**|REQ-001.4|
|**Priority**|MUST|
|**Test Type**|Performance|

**Acceptance Criteria:**

* \[ ] Incoming data queued if processing temporarily delayed
* \[ ] Buffer size adequate for expected data rates
* \[ ] Buffer overflow detected and logged
* \[ ] No data loss under normal operating conditions

**Test Method:**

1. Connect with mock data at 10 Hz
2. Simulate processing delay (add artificial pause)
3. Verify data continues to be queued
4. Resume normal processing
5. Verify no data lost
6. Monitor queue size in debug output

**Pass/Fail Criteria:**

* PASS: No data loss with temporary delays up to 5 seconds
* FAIL: Any data loss occurs during temporary delays

---

### 4.2 Data Logging Tests

#### TC-002: CSV Data Logging

|Field|Value|
|-|-|
|**Test ID**|TC-002|
|**Requirement**|REQ-002|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Data logged in CSV format
* \[ ] CSV files created automatically
* \[ ] All valid data points are logged
* \[ ] Files are accessible after test completion

**Test Procedure:**

1. Connect to mock data source
2. Run for 60 seconds (receive ~600 data points at 10 Hz)
3. Disconnect
4. Navigate to logs/ directory
5. Open CSV file
6. Verify all data points present

**Pass/Fail Criteria:**

* PASS: CSV file exists, contains all expected data points
* FAIL: CSV file missing or data points missing

---

#### TC-002.1: CSV File Creation

|Field|Value|
|-|-|
|**Test ID**|TC-002.1|
|**Requirement**|REQ-002.1|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] File created when connection established
* \[ ] Filename format: `fatigue\_test\_YYYYMMDD\_HHMMSS.csv`
* \[ ] File created in `logs/` subdirectory
* \[ ] `logs/` directory created automatically if not present

**Test Method:**

|Test Case|Initial State|Expected Result|
|-|-|-|
|New logs dir|logs/ does not exist|logs/ created, file inside|
|Existing logs dir|logs/ exists|File created in existing logs/|
|Filename format|Any date/time|Filename matches `fatigue\_test\_YYYYMMDD\_HHMMSS.csv`|

**Test Procedure:**

1. Delete logs/ directory if exists
2. Launch application and connect
3. Verify logs/ directory created
4. Verify CSV file created with correct naming format
5. Check timestamp in filename matches connection time (± 1 second)

**Pass/Fail Criteria:**

* PASS: Directory and file created with correct format
* FAIL: Directory not created or filename incorrect

---

#### TC-002.2: No Data Overwriting

|Field|Value|
|-|-|
|**Test ID**|TC-002.2|
|**Requirement**|REQ-002.2|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] If filename exists, append counter (e.g., `\_01`, `\_02`)
* \[ ] User warned before any potential data loss
* \[ ] Previous test data remains intact
* \[ ] Each test session creates unique file

**Test Method:**

|Iteration|Expected Filename|File Should Exist|
|-|-|-|
|1st connection|`fatigue\_test\_20260205\_143215.csv`|Created|
|2nd connection (same second)|`fatigue\_test\_20260205\_143215\_01.csv`|Created|
|3rd connection (same second)|`fatigue\_test\_20260205\_143215\_02.csv`|Created|

**Test Procedure:**

1. Connect and disconnect (creates file 1)
2. Manually set system time to same second
3. Connect again (should create file with \_01)
4. Verify original file unchanged
5. Compare file sizes and contents
6. Repeat to verify \_02, \_03 sequence

**Pass/Fail Criteria:**

* PASS: Each connection creates unique file, no overwriting
* FAIL: Any file overwritten or not created

---

#### TC-002.3: CSV Format Specification

|Field|Value|
|-|-|
|**Test ID**|TC-002.3|
|**Requirement**|REQ-002.3|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Standard comma-separated values format
* \[ ] Header row with column names
* \[ ] Consistent column order across all files
* \[ ] No missing or extra columns
* \[ ] Compatible with Excel, MATLAB, Python pandas

**Expected CSV Header:**

```
Timestamp,Status,Cycles,Position\_1\_mm,Force\_Lower\_N,Travel\_1\_mm,Position\_2\_mm,Force\_Upper\_N,Travel\_2\_mm,Travel\_at\_Upper\_mm,Loss\_of\_Stiffness\_Percent,Error\_Code,Error\_Description,Raw\_Data
```

**Test Method:**

|Tool|Test|Expected Result|
|-|-|-|
|Excel|Open CSV file|File opens correctly, 14 columns visible|
|Python pandas|`pd.read\_csv()`|DataFrame created without errors|
|Text editor|View raw file|Proper comma separation, no extra delimiters|

**Test Procedure:**

1. Generate CSV file with test data
2. Open in Microsoft Excel
3. Verify 14 columns present
4. Import into Python using pandas
5. Verify no parsing errors
6. Check column names match specification
7. Verify data types correct (numbers as numbers)

**Pass/Fail Criteria:**

* PASS: File compatible with all three tools
* FAIL: Any tool fails to read file correctly

---

#### TC-002.4: Data Completeness

|Field|Value|
|-|-|
|**Test ID**|TC-002.4|
|**Requirement**|REQ-002.4|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Every valid data point is logged
* \[ ] Points Logged counter matches valid data received
* \[ ] Malformed data excluded (but counted as parse error)
* \[ ] Timestamp for each data point

**Test Method:**

|Test Scenario|Valid Lines|Invalid Lines|Expected CSV Rows|
|-|-|-|-|
|All valid|1000|0|1000|
|Mixed data|900|100|900|
|With errors|800|200|800|

**Test Procedure:**

1. Send 1000 valid data lines
2. Verify Points Logged counter = 1000
3. Verify CSV contains 1000 data rows (+ 1 header)
4. Send 900 valid + 100 invalid lines
5. Verify Points Logged = 900
6. Verify Parse Errors = 100
7. Verify CSV contains 900 data rows
8. Check each row has valid timestamp

**Pass/Fail Criteria:**

* PASS: Logged count matches CSV rows, all valid data present
* FAIL: Missing data or invalid data included in CSV

---

#### TC-002.5: User-Requested Save

|Field|Value|
|-|-|
|**Test ID**|TC-002.5|
|**Requirement**|REQ-002.5|
|**Priority**|SHOULD|

**Acceptance Criteria:**

* \[ ] "Save Log As..." button available
* \[ ] File dialog allows custom filename selection
* \[ ] Original log file remains
* \[ ] Copy created with user-specified name

**Test Procedure:**

1. Connect and collect some data
2. Click "Save Log As..." button
3. Verify file dialog opens
4. Enter custom filename: `my\_test\_data.csv`
5. Click Save
6. Verify original log file still exists in logs/
7. Verify copy created with custom name
8. Compare both files (should be identical)

**Pass/Fail Criteria:**

* PASS: Copy created, original unchanged, files identical
* FAIL: Original deleted or copy not created

---

### 4.3 Live Data Plotting Tests

#### TC-003: Real-Time Visualization

|Field|Value|
|-|-|
|**Test ID**|TC-003|
|**Requirement**|REQ-003|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Three plots displayed simultaneously
* \[ ] Data updates in real-time
* \[ ] All plots clearly labeled
* \[ ] Axes auto-range as data changes

**Test Procedure:**

1. Connect to mock data at 1 Hz
2. Verify three plot panels visible
3. Verify each plot has title
4. Verify each plot has axis labels
5. Verify data appears in all three plots
6. Observe plots update approximately every 1 second

**Pass/Fail Criteria:**

* PASS: All three plots visible, labeled, updating
* FAIL: Any plot missing or not updating

---

#### TC-003.1: Plot 1 - Forces

|Field|Value|
|-|-|
|**Test ID**|TC-003.1|
|**Requirement**|REQ-003.1|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Two traces: Lower Force (blue) and Upper Force (red)
* \[ ] X-axis: Cycles (number)
* \[ ] Y-axis: Force \[N]
* \[ ] Legend identifying each trace
* \[ ] Grid lines for readability

**Test Data:**

```
Cycles: 100, 200, 300
Lower Force: 26.3 N, 26.5 N, 26.2 N
Upper Force: 223.8 N, 224.1 N, 223.5 N
```

**Test Procedure:**

1. Connect to mock data
2. Wait for 3 data points
3. Verify Plot 1 shows two traces
4. Verify blue line represents Lower Force
5. Verify red line represents Upper Force
6. Check legend shows "Lower Force \[N]" and "Upper Force \[N]"
7. Verify X-axis labeled "Cycles"
8. Verify Y-axis labeled "Force \[N]"
9. Verify grid lines visible

**Pass/Fail Criteria:**

* PASS: All elements present and correct
* FAIL: Missing elements or incorrect colors/labels

---

#### TC-003.2: Plot 2 - Travel Measurements

|Field|Value|
|-|-|
|**Test ID**|TC-003.2|
|**Requirement**|REQ-003.2|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Three traces: Travel at Upper Force (green), Travel 1 (cyan), Travel 2 (magenta)
* \[ ] X-axis: Cycles
* \[ ] Y-axis: Travel \[mm]
* \[ ] Legend identifying all traces

**Test Data:**

```
Cycles: 100, 200, 300
Travel at Upper: 6.11 mm, 6.15 mm, 6.20 mm
Travel 1: 0.00 mm, 0.02 mm, 0.05 mm
Travel 2: 0.00 mm, 0.03 mm, 0.08 mm
```

**Test Procedure:**

1. Connect to mock data
2. Wait for 3 data points
3. Verify Plot 2 shows three traces
4. Verify green line = Travel at Upper Force
5. Verify cyan line = Additional Travel 1
6. Verify magenta line = Additional Travel 2
7. Check legend accuracy
8. Verify axes labeled correctly

**Pass/Fail Criteria:**

* PASS: Three traces with correct colors and labels
* FAIL: Missing traces or incorrect visualization

---

#### TC-003.3: Plot 3 - Loss of Stiffness

|Field|Value|
|-|-|
|**Test ID**|TC-003.3|
|**Requirement**|REQ-003.3|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Single trace: Loss of Stiffness \[%] (orange)
* \[ ] X-axis: Cycles
* \[ ] Y-axis: Loss of Stiffness \[%]
* \[ ] Value calculated as: (Travel 2 / Travel at Upper) × 100
* \[ ] Handle division by zero (display 0%)

**Test Data:**

|Cycles|Travel 2|Travel at Upper|Expected Loss of Stiffness|
|-|-|-|-|
|100|0.00 mm|6.11 mm|0.00%|
|200|0.10 mm|6.15 mm|1.63%|
|300|0.20 mm|6.20 mm|3.23%|
|400|0.00 mm|0.00 mm|0.00% (division by zero)|

**Test Procedure:**

1. Configure mock data with test values above
2. Connect and collect data
3. Verify Plot 3 shows single orange trace
4. For cycle 200: verify value ≈ 1.63%
5. For cycle 300: verify value ≈ 3.23%
6. For cycle 400: verify value = 0.00% (no crash)
7. Verify axis labels correct

**Pass/Fail Criteria:**

* PASS: Calculations correct, division by zero handled
* FAIL: Incorrect calculations or crash on division by zero

---

#### TC-003.4: Auto-Ranging

|Field|Value|
|-|-|
|**Test ID**|TC-003.4|
|**Requirement**|REQ-003.4|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Axes expand to show all data
* \[ ] No data clipped off screen
* \[ ] User can see latest data without manual adjustment
* \[ ] Auto-ranging can be toggled on/off by user

**Test Procedure:**

|Phase|Data Range|Expected Axis Range|
|-|-|-|
|Initial|Force: 0-100 N|Y-axis: ~0-110 N|
|Expanded|Force: 0-500 N|Y-axis: ~0-550 N|
|Auto-range OFF|Force: 0-1000 N|Y-axis: stays at 0-550 N|
|Auto-range ON|Force: 0-1000 N|Y-axis: ~0-1100 N|

**Test Steps:**

1. Start with mock data range 0-100 N
2. Verify axes show appropriate range
3. Change mock data to 0-500 N
4. Verify axes automatically expand
5. Disable auto-range checkbox
6. Change mock data to 0-1000 N
7. Verify axes do NOT expand
8. Enable auto-range checkbox
9. Verify axes now expand to show all data

**Pass/Fail Criteria:**

* PASS: Axes expand/fixed according to auto-range setting
* FAIL: Axes don't respond to auto-range toggle

---

#### TC-003.5: Plot Update Rate

|Field|Value|
|-|-|
|**Test ID**|TC-003.5|
|**Requirement**|REQ-003.5|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Default update interval: 1000 ms (1 second)
* \[ ] If data arrives slower than 1 Hz, update at data rate
* \[ ] Update rate configurable by user (100-5000 ms)
* \[ ] No excessive CPU usage from plotting

**Test Method:**

|Data Rate|Update Interval Setting|Expected Plot Update Rate|
|-|-|-|
|10 Hz|1000 ms|1 Hz (1 second)|
|0.5 Hz|1000 ms|0.5 Hz (2 seconds)|
|10 Hz|500 ms|2 Hz (0.5 seconds)|
|10 Hz|2000 ms|0.5 Hz (2 seconds)|

**Test Procedure:**

1. Connect with 10 Hz mock data
2. Set update interval to 1000 ms
3. Observe plot updates approximately once per second
4. Monitor CPU usage (should be < 10%)
5. Change update interval to 500 ms
6. Observe plot updates approximately twice per second
7. Connect with 0.5 Hz mock data
8. Verify plot updates at data rate (every 2 seconds)

**Pass/Fail Criteria:**

* PASS: Update rate matches setting or data rate (whichever is slower), CPU < 25%
* FAIL: Update rate incorrect or CPU usage excessive

---

#### TC-003.6: Negative Value Support

|Field|Value|
|-|-|
|**Test ID**|TC-003.6|
|**Requirement**|REQ-003.6|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Negative force values plotted correctly
* \[ ] Negative position values plotted correctly
* \[ ] No error messages for negative values
* \[ ] Axes scale appropriately for negative ranges

**Test Data:**

|Cycles|Lower Force|Upper Force|Position 1|Position 2|
|-|-|-|-|-|
|100|26.3 N|223.8 N|1.82 mm|7.93 mm|
|200|-15.0 N|200.0 N|-2.50 mm|5.00 mm|
|300|-30.0 N|180.0 N|-5.00 mm|3.00 mm|

**Test Procedure:**

1. Configure mock data with negative values
2. Connect and collect data
3. Verify negative forces display in Plot 1
4. Verify no error messages in console
5. Verify no error dialogs appear
6. Check Y-axis range includes negative values
7. Verify negative positions handled correctly
8. Check status log for any warnings (should be none)

**Pass/Fail Criteria:**

* PASS: Negative values plotted, no errors, axes scaled correctly
* FAIL: Errors occur or negative values not displayed

---

#### TC-003.7: Unlimited Data Points

|Field|Value|
|-|-|
|**Test ID**|TC-003.7|
|**Requirement**|REQ-003.7|
|**Priority**|MUST|
|**Test Type**|Performance|

**Acceptance Criteria:**

* \[ ] No arbitrary cutoff (e.g., not limited to 1000 points)
* \[ ] All data from test start remains visible
* \[ ] Points Plotted counter continues increasing
* \[ ] Graceful handling if memory limits reached

**Test Method:**

|Data Points|Expected Behavior|Memory Limit|
|-|-|-|
|1,000|All points visible|< 50 MB|
|10,000|All points visible|< 200 MB|
|50,000|All points visible|< 500 MB|
|100,000|All points visible or warning|< 1 GB|

**Test Procedure:**

1. Connect to mock data at 10 Hz
2. Run for 100 seconds (collect 1,000 points)
3. Verify all points visible in plots
4. Run for 1,000 seconds (collect 10,000 points)
5. Verify all points visible
6. Monitor memory usage
7. Continue to 50,000 points if memory allows
8. Verify Points Plotted counter matches data received

**Pass/Fail Criteria:**

* PASS: At least 10,000 points plotted without limits, memory < 500 MB
* FAIL: Arbitrary point limit before 10,000 or excessive memory usage

---

#### TC-003.8: Plot Controls

|Field|Value|
|-|-|
|**Test ID**|TC-003.8|
|**Requirement**|REQ-003.8|
|**Priority**|SHOULD|

**Acceptance Criteria:**

* \[ ] Update interval adjustable (100-5000 ms)
* \[ ] Auto-range toggle available
* \[ ] "Clear Plots" button available
* \[ ] Controls clearly labeled

**Test Procedure:**

|Control|Test Action|Expected Result|
|-|-|-|
|Update Interval|Change from 1000 to 500 ms|Plot updates faster|
|Update Interval|Change from 1000 to 3000 ms|Plot updates slower|
|Auto-range toggle|Uncheck|Axes fixed|
|Auto-range toggle|Check|Axes adjust to data|
|Clear Plots|Click button|All plot data cleared|

**Test Steps:**

1. Connect to mock data
2. Locate plot control panel
3. Verify Update Interval spinbox present (100-5000 ms range)
4. Change value and verify plot behavior changes
5. Verify Auto-range checkbox present and labeled
6. Toggle and verify behavior
7. Verify "Clear Plots" button present
8. Click and verify plots cleared (data logging continues)

**Pass/Fail Criteria:**

* PASS: All controls present, functional, and clearly labeled
* FAIL: Any control missing or non-functional

---

### 4.4 User Interface Tests

#### TC-004: Graphical User Interface

|Field|Value|
|-|-|
|**Test ID**|TC-004|
|**Requirement**|REQ-004|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] All functions accessible via GUI
* \[ ] No command-line interaction required for normal operation
* \[ ] Interface intuitive for target users
* \[ ] Consistent layout and design

**Test Procedure:**

1. Launch application
2. Verify main window appears
3. Identify all major functional areas
4. Verify no console/command line needed for operation
5. Ask test engineer to perform basic tasks without training
6. Measure time to complete basic connection

**Pass/Fail Criteria:**

* PASS: All functions accessible via GUI, intuitive design
* FAIL: Command line required or interface confusing

---

#### TC-004.1: Connection Controls

|Field|Value|
|-|-|
|**Test ID**|TC-004.1|
|**Requirement**|REQ-004.1|
|**Priority**|MUST|

**Required Controls:**

* \[ ] COM port selection dropdown
* \[ ] Baudrate selection dropdown
* \[ ] Connect/Disconnect button (toggle)
* \[ ] Connection status indicator
* \[ ] Mock data mode checkbox

**Test Procedure:**

1. Launch application
2. Locate connection control panel
3. Verify all required controls present
4. Check COM port dropdown shows available ports
5. Check baudrate dropdown shows: 9600, 19200, 38400, 57600, 115200
6. Verify Connect button present and labeled
7. Verify connection status indicator visible
8. Verify Mock data mode checkbox present

**Visual Inspection Checklist:**

* \[ ] Controls grouped logically
* \[ ] Labels clear and readable
* \[ ] Adequate spacing between controls
* \[ ] Status indicator clearly visible (color or text)

**Pass/Fail Criteria:**

* PASS: All required controls present and clearly labeled
* FAIL: Any control missing or poorly labeled

---

#### TC-004.2: Data Logging Controls

|Field|Value|
|-|-|
|**Test ID**|TC-004.2|
|**Requirement**|REQ-004.2|
|**Priority**|MUST|

**Required Controls:**

* \[ ] Current log filename displayed
* \[ ] "Save Log As..." button
* \[ ] "Start New Log" button
* \[ ] Logging status clearly indicated

**Test Procedure:**

1. Connect to mock data
2. Locate data logging control panel
3. Verify current filename displayed
4. Verify "Save Log As..." button present
5. Click and verify file dialog opens
6. Verify "Start New Log" button present
7. Click and verify new log file created
8. Verify logging status shows "Logging Active" or similar

**Pass/Fail Criteria:**

* PASS: All controls present and functional
* FAIL: Any control missing or non-functional

---

#### TC-004.3: Help Menu

|Field|Value|
|-|-|
|**Test ID**|TC-004.3|
|**Requirement**|REQ-004.3|
|**Priority**|MUST|

**Required Elements:**

* \[ ] "Help" menu in menu bar
* \[ ] "Help Documentation" option opens help dialog
* \[ ] "About" option shows application information
* \[ ] Help content includes all required sections

**Help Content Requirements:**

* \[ ] Quick start guide
* \[ ] Plot descriptions
* \[ ] Data logging instructions
* \[ ] Troubleshooting tips

**Test Procedure:**

1. Click on menu bar
2. Verify "Help" menu present
3. Click "Help" menu
4. Verify dropdown shows "Help Documentation" and "About"
5. Click "Help Documentation"
6. Verify help dialog opens
7. Verify all required content sections present
8. Click "About"
9. Verify application info displayed

**Pass/Fail Criteria:**

* PASS: Help menu complete with all required content
* FAIL: Help menu missing or content incomplete

---

#### TC-004.4: Version Menu

|Field|Value|
|-|-|
|**Test ID**|TC-004.4|
|**Requirement**|REQ-004.4|
|**Priority**|MUST|

**Required Information:**

* \[ ] Application version number
* \[ ] Release date
* \[ ] Requirements version
* \[ ] Component versions (PyQt, pyserial, etc.)
* \[ ] Update history

**Test Procedure:**

1. Click "Version" menu
2. Click "Version Information"
3. Verify dialog opens
4. Check all required information present:

   * Application version (e.g., 2.0)
   * Release date
   * Requirements version (2.0)
   * Python version
   * PyQt5 version
   * pyserial version
   * pyqtgraph version

5. Verify information is accurate

**Pass/Fail Criteria:**

* PASS: All version information present and accurate
* FAIL: Any information missing or incorrect

---

#### TC-004.5: Statistics Display

|Field|Value|
|-|-|
|**Test ID**|TC-004.5|
|**Requirement**|REQ-004.5|
|**Priority**|MUST|

**Required Statistics:**

* \[ ] Connection time (duration)
* \[ ] Lines received (count)
* \[ ] Points logged (count)
* \[ ] Points plotted (count)
* \[ ] Parse errors (count)

**Test Method:**

|Statistic|Test Condition|Expected Display|
|-|-|-|
|Connection time|After 60 seconds connected|"00:01:00" or "60 s"|
|Lines received|After 100 lines|"100"|
|Points logged|After 95 valid lines|"95"|
|Points plotted|After 95 valid lines|"95"|
|Parse errors|After 5 invalid lines|"5"|

**Test Procedure:**

1. Connect to mock data
2. Locate statistics panel
3. Verify all required statistics visible
4. Wait 60 seconds
5. Verify connection time shows approximately 60 seconds
6. Send mix of valid/invalid data
7. Verify counters update correctly
8. Verify updates occur approximately every 1 second

**Pass/Fail Criteria:**

* PASS: All statistics present, accurate, and updating
* FAIL: Any statistic missing or not updating

---

#### TC-004.6: Status Log

|Field|Value|
|-|-|
|**Test ID**|TC-004.6|
|**Requirement**|REQ-004.6|
|**Priority**|SHOULD|

**Required Features:**

* \[ ] Status log area visible
* \[ ] Shows timestamped events
* \[ ] Errors displayed in red
* \[ ] Scrollable for long logs
* \[ ] "Clear Log" button available

**Test Events:**

|Event Type|Expected Log Entry|Color|
|-|-|-|
|Connection|"\[HH:MM:SS] Connected to COM3 at 9600 baud"|Black|
|Data received|"\[HH:MM:SS] Data reception started"|Black|
|Parse error|"\[HH:MM:SS] Parse error: Invalid field count"|Red|
|Disconnection|"\[HH:MM:SS] Disconnected"|Black|

**Test Procedure:**

1. Locate status log area
2. Connect to mock data
3. Verify connection event logged with timestamp
4. Send invalid data
5. Verify parse error logged in red
6. Disconnect
7. Verify disconnection event logged
8. Verify log is scrollable if many entries
9. Click "Clear Log" button
10. Verify log cleared

**Pass/Fail Criteria:**

* PASS: All features present and functional
* FAIL: Any feature missing or non-functional

---

### 4.5 Data Processing Tests

#### TC-005: Data Parsing and Validation

|Field|Value|
|-|-|
|**Test ID**|TC-005|
|**Requirement**|REQ-005|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] All valid data parsed successfully
* \[ ] Invalid data detected and rejected
* \[ ] Parse errors logged and counted
* \[ ] System continues operating after parse errors

**Test Data:**

|Data|Status|Reason|
|-|-|-|
|`DTA;100;182;263;0;793;2238;0;611;0;!`|Valid|Correct format|
|`DTA;100;182;263;0;793;2238;0;611;!`|Invalid|Missing field|
|`DTA;100;182;263;0;793;2238;0;611;0;0;!`|Invalid|Extra field|
|`XYZ;100;182;263;0;793;2238;0;611;0;!`|Invalid|Invalid status|
|`DTA;abc;182;263;0;793;2238;0;611;0;!`|Invalid|Non-numeric field|

**Test Procedure:**

1. Send valid data line
2. Verify parsed successfully
3. Send each invalid data line above
4. Verify rejected with appropriate error message
5. Verify system continues operating
6. Verify parse error counter increments

**Pass/Fail Criteria:**

* PASS: Valid data accepted, invalid rejected, system stable
* FAIL: Valid data rejected or invalid data accepted

---

#### TC-005.1: Data Format Parsing

|Field|Value|
|-|-|
|**Test ID**|TC-005.1|
|**Requirement**|REQ-005.1|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Correctly interprets 11-field semicolon-separated format
* \[ ] Applies proper decimal conversion
* \[ ] Extracts all fields correctly
* \[ ] Handles end marker (!)

**Decimal Conversion Tests:**

|Raw Value|Field|Expected Result|
|-|-|-|
|182|Position 1|1.82 mm|
|263|Force Lower|26.3 N|
|0|Travel 1|0.00 mm|
|793|Position 2|7.93 mm|
|2238|Force Upper|223.8 N|
|611|Travel at Upper|6.11 mm|

**Test Procedure:**

1. Send data: `DTA;100;182;263;0;793;2238;0;611;0;!`
2. Verify Cycles = 100
3. Verify Position 1 = 1.82 mm
4. Verify Force Lower = 26.3 N
5. Verify Travel 1 = 0.00 mm
6. Verify Position 2 = 7.93 mm
7. Verify Force Upper = 223.8 N
8. Verify Travel 2 = 0.00 mm
9. Verify Travel at Upper = 6.11 mm
10. Verify Error Code = 0

**Pass/Fail Criteria:**

* PASS: All fields parsed with correct decimal conversions
* FAIL: Any field incorrectly parsed or converted

---

#### TC-005.2: Data Validation

|Field|Value|
|-|-|
|**Test ID**|TC-005.2|
|**Requirement**|REQ-005.2|
|**Priority**|MUST|

**Validation Rules:**

|Rule|Test Data|Should Be|
|-|-|-|
|Field count = 10|`DTA;100;182;263;0;793;2238;0;611;!`|Rejected|
|Status = DTA or END|`XYZ;100;182;263;0;793;2238;0;611;0;!`|Rejected|
|Cycles non-negative|`DTA;-100;182;263;0;793;2238;0;611;0;!`|Rejected|
|Negative force allowed|`DTA;100;182;-263;0;793;2238;0;611;0;!`|Accepted|
|Negative position allowed|`DTA;100;-182;263;0;793;2238;0;611;0;!`|Accepted|

**Test Procedure:**

1. Send each test data line above
2. Verify correct acceptance/rejection
3. Check console for validation error messages
4. Verify error messages are descriptive

**Pass/Fail Criteria:**

* PASS: All validation rules enforced correctly
* FAIL: Any rule not enforced or incorrectly enforced

---

#### TC-005.3: Parse Error Handling

|Field|Value|
|-|-|
|**Test ID**|TC-005.3|
|**Requirement**|REQ-005.3|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Parse errors logged to console with data shown
* \[ ] Parse error counter incremented
* \[ ] Invalid data discarded (not logged or plotted)
* \[ ] System continues processing subsequent data
* \[ ] Error rate displayed to user

**Test Sequence:**

|Line #|Data|Expected|
|-|-|-|
|1|Valid data|Processed|
|2|Invalid data|Error logged, counter = 1|
|3|Valid data|Processed|
|4|Invalid data|Error logged, counter = 2|
|5|Valid data|Processed|

**Test Procedure:**

1. Send sequence above
2. Verify parse error counter = 2
3. Verify points logged = 3 (only valid data)
4. Verify console shows error messages for lines 2 and 4
5. Verify error messages include the invalid data
6. Verify system continues without crash
7. Check CSV file contains only 3 valid data rows

**Pass/Fail Criteria:**

* PASS: Errors handled gracefully, system stable, counters accurate
* FAIL: System crashes or valid data affected by errors

---

#### TC-005.4: Loss of Stiffness Calculation

|Field|Value|
|-|-|
|**Test ID**|TC-005.4|
|**Requirement**|REQ-005.4|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Formula: (Additional Travel 2 / Travel at Upper) × 100
* \[ ] Result in percentage (%)
* \[ ] Handle division by zero (return 0%)
* \[ ] Calculation included in CSV output
* \[ ] Value plotted in Plot 3

**Test Cases:**

|Travel 2|Travel at Upper|Expected Loss of Stiffness|
|-|-|-|
|0.00 mm|6.11 mm|0.00%|
|0.10 mm|6.11 mm|1.64%|
|0.50 mm|5.00 mm|10.00%|
|1.00 mm|4.00 mm|25.00%|
|0.50 mm|0.00 mm|0.00% (div by zero)|

**Test Procedure:**

1. Send data with each test case above
2. Check CSV Loss\_of\_Stiffness\_Percent column
3. Verify calculations match expected ± 0.01%
4. Verify division by zero case returns 0.00%
5. Verify no error or crash on division by zero
6. Check Plot 3 displays calculated values
7. Verify values in plot match CSV values

**Pass/Fail Criteria:**

* PASS: All calculations correct, div by zero handled
* FAIL: Any calculation incorrect or div by zero crashes

---

#### TC-005.5: Error Code Interpretation

|Field|Value|
|-|-|
|**Test ID**|TC-005.5|
|**Requirement**|REQ-005.5|
|**Priority**|SHOULD|

**Test Cases:**

|Error Code|Expected Description|
|-|-|
|0|No Error: Everything is OK|
|10|Test failed: The test was completed with an error|
|11|Additional Path 1 Violation|
|101|Motor Error: Voice Coil drive could not be initialized|
|201|Travel Determination: Resulting actuation travel is too small|
|999|Unknown Error (or similar)|

**Test Procedure:**

1. Send data with Error Code = 0
2. Verify CSV shows "No Error: Everything is OK"
3. Send data with Error Code = 11
4. Verify CSV shows correct description
5. Send data with Error Code = 101
6. Verify CSV shows motor error description
7. Send data with Error Code = 999 (unknown)
8. Verify CSV shows "Unknown Error" or similar
9. Verify critical errors (101-107, 201-205) highlighted in status log

**Pass/Fail Criteria:**

* PASS: All known codes correctly interpreted, unknown codes handled
* FAIL: Any known code has wrong description or unknown code crashes

---

## 5\. Non-Functional Requirements Tests

### 5.1 Performance Tests

#### TC-NFR-001: Data Throughput

|Field|Value|
|-|-|
|**Test ID**|TC-NFR-001|
|**Requirement**|REQ-NFR-001|
|**Priority**|MUST|
|**Test Type**|Performance|

**Acceptance Criteria:**

* \[ ] No data loss at 10 Hz continuous operation
* \[ ] Parse success rate > 95% (excluding equipment errors)
* \[ ] CPU usage < 25% on modern hardware
* \[ ] Memory usage < 500 MB for 24-hour test

**Test Procedure:**

|Duration|Data Rate|Expected Lines|Max CPU %|Max Memory|
|-|-|-|-|-|
|1 hour|10 Hz|36,000|25%|100 MB|
|4 hours|10 Hz|144,000|25%|200 MB|
|24 hours|10 Hz|864,000|25%|500 MB|

**Test Steps:**

1. Launch application with resource monitoring
2. Connect to mock data at 10 Hz
3. Run for 1 hour
4. Check Lines Received = 36,000 ± 5
5. Check Points Logged ≈ Lines Received (> 95%)
6. Monitor CPU usage (should average < 25%)
7. Monitor memory usage (should be < 100 MB)
8. Repeat for longer durations

**Pass/Fail Criteria:**

* PASS: All acceptance criteria met
* FAIL: Any criterion not met

---

#### TC-NFR-002: Plot Rendering Performance

|Field|Value|
|-|-|
|**Test ID**|TC-NFR-002|
|**Requirement**|REQ-NFR-002|
|**Priority**|MUST|
|**Test Type**|Performance|

**Acceptance Criteria:**

* \[ ] Plot updates complete within 100 ms
* \[ ] No GUI freezing during updates
* \[ ] Smooth operation with 10,000+ data points
* \[ ] Interactive controls remain responsive

**Test Method:**

|Data Points|Expected Update Time|GUI Responsive?|
|-|-|-|
|1,000|< 50 ms|Yes|
|10,000|< 100 ms|Yes|
|50,000|< 200 ms|Yes|

**Test Procedure:**

1. Connect and collect 1,000 data points
2. Measure plot update time (use profiler)
3. Verify update completes < 50 ms
4. Try to interact with GUI during update
5. Verify controls responsive
6. Continue to 10,000 points
7. Verify update time < 100 ms
8. Verify GUI never freezes

**Pass/Fail Criteria:**

* PASS: Update times within limits, GUI always responsive
* FAIL: Updates too slow or GUI freezes

---

#### TC-NFR-003: Startup Time

|Field|Value|
|-|-|
|**Test ID**|TC-NFR-003|
|**Requirement**|REQ-NFR-003|
|**Priority**|SHOULD|
|**Test Type**|Performance|

**Acceptance Criteria:**

* \[ ] Application launches within 5 seconds
* \[ ] GUI fully responsive within 10 seconds
* \[ ] No excessive delay before connection possible

**Test Procedure:**

1. Close application completely
2. Start timer
3. Launch application
4. Stop timer when main window appears
5. Verify time < 5 seconds
6. Try to interact with controls
7. Verify GUI responsive within 10 seconds
8. Try to connect immediately
9. Verify connection possible

**Pass/Fail Criteria:**

* PASS: Startup < 5s, responsive < 10s
* FAIL: Startup > 5s or not responsive within 10s

---

### 5.2 Safety and Reliability Tests

#### TC-NFR-004: Data Integrity

|Field|Value|
|-|-|
|**Test ID**|TC-NFR-004|
|**Requirement**|REQ-NFR-004|
|**Priority**|MUST|
|**Test Type**|Safety|

**Acceptance Criteria:**

* \[ ] No data overwriting
* \[ ] All valid data preserved
* \[ ] File system errors detected and reported
* \[ ] Graceful handling of disk full condition

**Test Scenarios:**

|Scenario|Expected Behavior|
|-|-|
|Normal operation|All data saved correctly|
|Disk full|Error message, graceful stop|
|Power loss simulation|Data up to crash point preserved|
|File permission denied|Error message, user notified|

**Test Procedure:**

1. Run normal test, verify data complete
2. Fill disk to capacity
3. Try to connect and log data
4. Verify error message displayed
5. Verify application doesn't crash
6. Simulate power loss (force quit)
7. Restart and check CSV file
8. Verify data up to crash point is intact
9. Remove write permissions from logs/
10. Try to connect
11. Verify error message about permissions

**Pass/Fail Criteria:**

* PASS: All scenarios handled gracefully, data never corrupted
* FAIL: Data lost or corrupted in any scenario

---

#### TC-NFR-007: Reliability

|Field|Value|
|-|-|
|**Test ID**|TC-NFR-007|
|**Requirement**|REQ-NFR-007|
|**Priority**|MUST|
|**Test Type**|Reliability|

**Acceptance Criteria:**

* \[ ] Mean Time Between Failures (MTBF) > 100 hours
* \[ ] Graceful error recovery
* \[ ] No memory leaks
* \[ ] Stable operation over extended periods

**Test Procedure:**

|Test|Duration|Monitoring|
|-|-|-|
|Continuous operation|24 hours|Check for crashes|
|Memory leak test|12 hours|Monitor memory growth|
|Error injection|2 hours|Verify recovery from errors|

**Long-Duration Test:**

1. Start application
2. Connect to mock data at 5 Hz
3. Run for 24 hours
4. Monitor for any crashes or hangs
5. Check memory usage every hour
6. Verify memory remains stable (< 500 MB)
7. At end, verify system still responsive

**Error Recovery Test:**

1. During operation, introduce errors:

   * Disconnect serial port
   * Send corrupt data
   * Fill disk temporarily

2. Verify system recovers from each error
3. Verify data collection continues after recovery

**Pass/Fail Criteria:**

* PASS: No crashes in 24 hours, memory stable, error recovery works
* FAIL: Any crash, memory leak, or failed error recovery

---

#### TC-NFR-008: Usability

|Field|Value|
|-|-|
|**Test ID**|TC-NFR-008|
|**Requirement**|REQ-NFR-008|
|**Priority**|MUST|
|**Test Type**|Usability|

**Acceptance Criteria:**

* \[ ] New users can start basic operation within 5 minutes
* \[ ] Help documentation readily accessible
* \[ ] Clear error messages
* \[ ] Intuitive controls

**Test Procedure:**

1. Recruit 3 test engineers unfamiliar with system
2. Provide only application (no training)
3. Ask them to:

   * Start the application
   * Connect to mock data
   * Start logging data
   * Save the log file

4. Time how long each takes
5. Ask for feedback on:

   * Interface clarity
   * Control intuitiveness
   * Error message clarity

6. Verify average time < 5 minutes

**Feedback Questions:**

* Was it clear how to connect? (1-5 scale)
* Were controls easy to find? (1-5 scale)
* Were error messages helpful? (1-5 scale)
* Overall ease of use? (1-5 scale)

**Pass/Fail Criteria:**

* PASS: Average time < 5 min, average rating > 3.5/5
* FAIL: Time > 5 min or rating < 3.5/5

---

#### TC-NFR-011: Mock Data Mode

|Field|Value|
|-|-|
|**Test ID**|TC-NFR-011|
|**Requirement**|REQ-NFR-011|
|**Priority**|MUST|

**Acceptance Criteria:**

* \[ ] Checkbox to enable mock mode
* \[ ] Generates realistic test data
* \[ ] Same data flow as real hardware
* \[ ] Useful for training and testing

**Test Procedure:**

1. Locate "Mock Data Mode" checkbox
2. Check the checkbox
3. Select any COM port (doesn't matter)
4. Click Connect
5. Verify connection succeeds
6. Verify data generation starts
7. Check data format matches specification
8. Verify data logged to CSV
9. Verify data plotted in real-time
10. Verify all features work same as with real hardware

**Mock Data Validation:**

* \[ ] Cycles increment logically
* \[ ] Force values realistic (0-500 N range)
* \[ ] Position values realistic (0-10 mm range)
* \[ ] Error codes occasionally non-zero
* \[ ] Data rate approximately as configured

**Pass/Fail Criteria:**

* PASS: Mock mode works identically to real hardware mode
* FAIL: Mock mode has different behavior or doesn't work

---

## 6\. Test Traceability Matrix

|Test ID|Requirement|Priority|Status|Last Run|Result|
|-|-|-|-|-|-|
|TC-001|REQ-001|MUST|Pending|-|-|
|TC-001.1|REQ-001.1|MUST|Pending|-|-|
|TC-001.2|REQ-001.2|MUST|Pending|-|-|
|TC-001.3|REQ-001.3|MUST|Pending|-|-|
|TC-001.4|REQ-001.4|MUST|Pending|-|-|
|TC-002|REQ-002|MUST|Pending|-|-|
|TC-002.1|REQ-002.1|MUST|Pending|-|-|
|TC-002.2|REQ-002.2|MUST|Pending|-|-|
|TC-002.3|REQ-002.3|MUST|Pending|-|-|
|TC-002.4|REQ-002.4|MUST|Pending|-|-|
|TC-002.5|REQ-002.5|SHOULD|Pending|-|-|
|TC-003|REQ-003|MUST|Pending|-|-|
|TC-003.1|REQ-003.1|MUST|Pending|-|-|
|TC-003.2|REQ-003.2|MUST|Pending|-|-|
|TC-003.3|REQ-003.3|MUST|Pending|-|-|
|TC-003.4|REQ-003.4|MUST|Pending|-|-|
|TC-003.5|REQ-003.5|MUST|Pending|-|-|
|TC-003.6|REQ-003.6|MUST|Pending|-|-|
|TC-003.7|REQ-003.7|MUST|Pending|-|-|
|TC-003.8|REQ-003.8|SHOULD|Pending|-|-|
|TC-004|REQ-004|MUST|Pending|-|-|
|TC-004.1|REQ-004.1|MUST|Pending|-|-|
|TC-004.2|REQ-004.2|MUST|Pending|-|-|
|TC-004.3|REQ-004.3|MUST|Pending|-|-|
|TC-004.4|REQ-004.4|MUST|Pending|-|-|
|TC-004.5|REQ-004.5|MUST|Pending|-|-|
|TC-004.6|REQ-004.6|SHOULD|Pending|-|-|
|TC-005|REQ-005|MUST|Pending|-|-|
|TC-005.1|REQ-005.1|MUST|Pending|-|-|
|TC-005.2|REQ-005.2|MUST|Pending|-|-|
|TC-005.3|REQ-005.3|MUST|Pending|-|-|
|TC-005.4|REQ-005.4|MUST|Pending|-|-|
|TC-005.5|REQ-005.5|SHOULD|Pending|-|-|
|TC-NFR-001|REQ-NFR-001|MUST|Pending|-|-|
|TC-NFR-002|REQ-NFR-002|MUST|Pending|-|-|
|TC-NFR-003|REQ-NFR-003|SHOULD|Pending|-|-|
|TC-NFR-004|REQ-NFR-004|MUST|Pending|-|-|
|TC-NFR-007|REQ-NFR-007|MUST|Pending|-|-|
|TC-NFR-008|REQ-NFR-008|MUST|Pending|-|-|
|TC-NFR-011|REQ-NFR-011|MUST|Pending|-|-|

**Summary:**

* Total Tests: 38
* MUST Priority: 33
* SHOULD Priority: 5
* Status: All Pending

---

## 7\. Test Execution Schedule

### 7.1 Test Phases

|Phase|Duration|Tests Included|Dependencies|
|-|-|-|-|
|**Phase 1: Unit Testing**|Week 1|TC-005.x (parsing/validation)|Code complete|
|**Phase 2: Integration**|Week 2|TC-001.x, TC-002.x|Phase 1 complete|
|**Phase 3: System Testing**|Week 3|TC-003.x, TC-004.x|Phase 2 complete|
|**Phase 4: Performance**|Week 4|TC-NFR-001, TC-NFR-002, TC-NFR-003|Phase 3 complete|
|**Phase 5: Reliability**|Week 5-6|TC-NFR-004, TC-NFR-007|Phase 4 complete|
|**Phase 6: User Acceptance**|Week 7|TC-NFR-008|All phases complete|

### 7.2 Daily Test Execution Template

|Time|Activity|Tester|Notes|
|-|-|-|-|
|09:00-10:00|Test environment setup|QA Team|Verify all tools ready|
|10:00-12:00|Execute planned tests|QA Team|Follow test procedures|
|12:00-13:00|Lunch|-|-|
|13:00-15:00|Continue test execution|QA Team|Document results|
|15:00-16:00|Bug reporting|QA Team|File defects in tracker|
|16:00-17:00|Test report update|QA Lead|Update status|

---

## 8\. Test Results Summary

### 8.1 Test Results Template

|Test ID|Date|Tester|Result|Duration|Notes|
|-|-|-|-|-|-|
|TC-001|YYYY-MM-DD|\[Name]|PASS/FAIL|HH:MM|Comments|

### 8.2 Defect Summary Template

|Defect ID|Test ID|Severity|Description|Status|Assigned To|
|-|-|-|-|-|-|
|DEF-001|TC-XXX|Critical/Major/Minor|Brief description|Open/Fixed/Closed|Developer name|

**Severity Definitions:**

* **Critical:** System crash, data loss, or complete feature failure
* **Major:** Significant feature impairment, workaround available
* **Minor:** Cosmetic issue or minor inconvenience

### 8.3 Test Coverage Summary

|Category|Total Tests|Passed|Failed|Pending|Coverage %|
|-|-|-|-|-|-|
|Serial Data Acquisition|5|0|0|5|0%|
|Data Logging|6|0|0|6|0%|
|Live Plotting|9|0|0|9|0%|
|User Interface|7|0|0|7|0%|
|Data Processing|6|0|0|6|0%|
|Performance|3|0|0|3|0%|
|Reliability|2|0|0|2|0%|
|**TOTAL**|**38**|**0**|**0**|**38**|**0%**|

### 8.4 Requirements Coverage

|Requirement Type|Total|Tested|Coverage %|
|-|-|-|-|
|MUST|33|0|0%|
|SHOULD|5|0|0%|
|**TOTAL**|**38**|**0**|**0%**|

---

## Appendices

### Appendix A: Test Data Files

Location: `./test\_data/`

|File|Description|
|-|-|
|`valid\_data\_sample.txt`|1000 lines of valid serial data|
|`invalid\_data\_sample.txt`|Various malformed data for error testing|
|`boundary\_data.txt`|Edge cases (zeros, negatives, large values)|
|`long\_duration\_data.txt`|100,000+ lines for performance testing|

### Appendix B: Test Automation Scripts

Location: `./tests/`

|Script|Purpose|
|-|-|
|`test\_parser.py`|Unit tests for data parsing|
|`test\_logger.py`|Unit tests for CSV logging|
|`test\_integration.py`|Integration tests|
|`mock\_serial\_generator.py`|Mock data generator|
|`performance\_monitor.py`|CPU/memory monitoring utility|

### Appendix C: Bug Report Template

```
BUG REPORT: DEF-XXX

Title: \[Brief description]
Severity: Critical/Major/Minor
Priority: High/Medium/Low

Test Case: TC-XXX
Tester: \[Name]
Date Found: YYYY-MM-DD
Environment: \[OS, Python version, etc.]

Steps to Reproduce:
1. 
2. 
3. 

Expected Result:
\[What should happen]

Actual Result:
\[What actually happened]

Screenshots/Logs:
\[Attach relevant files]

Additional Notes:
\[Any other relevant information]
```

---

**END OF TEST AND VERIFICATION PLAN**

