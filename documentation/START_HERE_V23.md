# 🚀 START HERE - Fatigue Tester Data Acquisition System V2.3

**Quick Start Guide** | February 12, 2026

---

## 🎉 Welcome to Version 2.3!

**New in V2.3:**
- 📄 **PDF Export** - Generate professional reports with all plots
- 🏗️ **Modular Architecture** - Improved code quality (56% reduction)
- 📊 **Enhanced Metadata** - Complete test traceability in PDFs

---

## ⚡ 5-Minute Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- pyserial >= 3.5
- PyQt5 >= 5.15.0
- pyqtgraph >= 0.13.0
- pandas >= 1.5.0
- numpy >= 1.23.0
- **matplotlib >= 3.5.0** ← NEW for PDF export

### 2. Launch Application

```bash
python main_application.py
```

### 3. Connect to Equipment

**Option A: With Real Hardware**
1. Connect USB-Serial cable
2. Click "🔋 Detect Ports"
3. Select your port from dialog
4. Click "Connect"

**Option B: Test Mode (No Hardware)**
1. Check "Use Mock Data (Testing)"
2. Click "Connect"
3. System generates realistic test data

### 4. Watch Your Data

✅ Three plots update in real-time  
✅ Data automatically logged to `logs/` directory  
✅ Statistics displayed in left panel

### 5. Export PDF Report (NEW!)

1. Menu: **Advanced Options** → **Advanced Settings**
2. Click "📄 Export Plots to PDF"
3. Choose filename → Done!
4. Get professional 2-page report with all data

---

## 📂 Project Structure

```
Fatigue-Tester/
│
├── main_application.py           ← Start here (683 lines)
│
├── Business Logic (NEW in V2.3)
│   ├── threshold_monitor.py      ← Threshold management
│   ├── statistics_tracker.py     ← Statistics tracking
│   └── plot_exporter.py          ← PDF export (NEW!)
│
├── ui_components/                ← UI panels (Phase 1)
│   ├── connection_panel.py
│   ├── logging_panel.py
│   ├── plot_settings_panel.py
│   ├── statistics_panel.py
│   └── status_log_panel.py
│
├── Core Modules
│   ├── config.py
│   ├── data_parser.py
│   ├── data_logger.py
│   ├── live_plotter.py
│   ├── serial_reader.py
│   └── serial_port_detector.py
│
├── logs/                         ← Your CSV data files
│   └── fatigue_test_*.csv
│
└── Documentation
    ├── USER_MANUAL_V23.html
    ├── SOFTWARE_REQUIREMENTS_SPECIFICATION_V23.md
    ├── MAIN_APPLICATION_V23_CHANGELOG.md
    └── THIS FILE

```

---

## 📖 Documentation Guide

| I Want To... | Read This Document |
|--------------|-------------------|
| **Get started quickly** | This file (START_HERE_V23.md) |
| **Learn all features** | USER_MANUAL_V23.html |
| **Understand requirements** | SOFTWARE_REQUIREMENTS_SPECIFICATION_V23.md |
| **See what's new** | MAIN_APPLICATION_V23_CHANGELOG.md |
| **Troubleshoot issues** | USER_MANUAL_V23.html (Section 9) |

---

## 🎯 Key Features at a Glance

### Data Acquisition
- ✅ Real-time serial communication (0.1-1.0s intervals)
- ✅ Automatic CSV logging with timestamps
- ✅ Complete header/configuration preservation
- ✅ Mock mode for testing without hardware

### Visualization
- ✅ Three synchronized plots (Forces, Travel, Loss of Stiffness)
- ✅ Unlimited data points (no artificial limits)
- ✅ Configurable update rate (100-5000 ms)
- ✅ Auto-range and manual control

### Monitoring
- ✅ Upper Force threshold monitoring
- ✅ Loss of Stiffness threshold monitoring
- ✅ Real-time violation detection
- ✅ Visual markers on plots
- ✅ Statistics tracking

### Reporting (NEW!)
- ✅ **PDF Export** - All plots + metadata
- ✅ Professional 2-page reports
- ✅ Includes log filename
- ✅ Threshold violations in report
- ✅ Complete test statistics

---

## 🔧 Common Tasks

### Task 1: Start a Test

```bash
1. python main_application.py
2. Click "🔋 Detect Ports"
3. Select port → Click "Connect"
4. Data starts flowing automatically
```

### Task 2: Enable Thresholds

```bash
1. In Plot Settings Panel (left side)
2. Check "Enable Upper Force Thresholds"
3. Set upper/lower limits
4. Watch for red violation markers
```

### Task 3: Generate PDF Report

```bash
1. Menu → Advanced Options → Advanced Settings
2. Click "📄 Export Plots to PDF"
3. Choose location → Save
4. PDF created in < 5 seconds!
```

### Task 4: Save Log with Custom Name

```bash
1. Click "Save Log As" in Logging Panel
2. Enter custom filename
3. Original log continues running
```

---

## 🐛 Troubleshooting Quick Guide

| Problem | Quick Fix |
|---------|-----------|
| **No ports detected** | Check USB cable, reinstall drivers |
| **Connection failed** | Try different port, check baudrate (115200) |
| **No plots** | Check "Update Interval", reconnect |
| **PDF export failed** | Install matplotlib: `pip install matplotlib` |
| **Watchdog timeout** | Check cable, verify equipment running |

**More help:** See USER_MANUAL_V23.html Section 9

---

## 📊 What's New in V2.3?

### 1. PDF Export Feature
**Before V2.3:** Data only in CSV, manual plotting needed  
**After V2.3:** One-click PDF reports with all plots and metadata

### 2. Modular Architecture
**Before V2.3:** 1273-line monolithic main file  
**After V2.3:** 683-line coordinator + 11 modular files

### 3. Enhanced Metadata
**Before V2.3:** Basic CSV logs  
**After V2.3:** Complete traceability with log filename in PDF

---

## 🎓 Learning Path

### For New Users:
1. **Read:** This file (5 min)
2. **Try:** Mock mode test (5 min)
3. **Read:** USER_MANUAL_V23.html Sections 1-3 (15 min)
4. **Try:** Real connection (10 min)
5. **Explore:** PDF export, thresholds (10 min)

### For Developers:
1. **Read:** SOFTWARE_REQUIREMENTS_SPECIFICATION_V23.md
2. **Review:** Source code architecture
3. **Study:** Business logic modules (threshold_monitor.py, etc.)
4. **Extend:** Add features using modular design

---

## 💡 Pro Tips

### For Testing:
- Use **Mock Mode** to explore features without hardware
- Perfect for training new users
- All features work identically (including PDF export!)

### For Production:
- Enable **thresholds** to catch anomalies early
- Export **PDFs** at key milestones (start, middle, end of test)
- Keep **log filename** visible in PDF for traceability

### For Analysis:
- CSV files compatible with Excel, MATLAB, Python pandas
- PDF reports ideal for presentations
- Threshold violations highlighted automatically

---

## 📞 Need Help?

### Documentation:
- **Full Manual:** USER_MANUAL_V23.html (open in browser)
- **Technical:** SOFTWARE_REQUIREMENTS_SPECIFICATION_V23.md
- **Changes:** MAIN_APPLICATION_V23_CHANGELOG.md

### Contact:
- **Authors:** Uwe Hasenstab and Alexander Waal
- **Email:** [Contact info]
- **GitHub:** [Repository link]

---

## ⏭️ Next Steps

### Beginner → Intermediate:
1. ✅ Complete Quick Start (above)
2. ✅ Run first real test
3. ✅ Generate first PDF report
4. ✅ Read User Manual Sections 4-7
5. ✅ Experiment with thresholds

### Intermediate → Advanced:
1. ✅ Read full User Manual
2. ✅ Understand architecture (SRS Section 3)
3. ✅ Study business logic modules
4. ✅ Write analysis scripts (Python pandas)
5. ✅ Contribute improvements

---

## 🎯 Success Checklist

**After 30 Minutes, You Should Be Able To:**
- [ ] Launch the application
- [ ] Connect to equipment (or use mock mode)
- [ ] See real-time plots updating
- [ ] Understand what each plot shows
- [ ] Find your CSV log files
- [ ] Generate a PDF report
- [ ] Enable and monitor thresholds

**If any checkbox is unchecked, review the relevant section above or in USER_MANUAL_V23.html**

---

## 🚀 You're Ready!

**Everything you need to get started is now installed and documented.**

**Start the application and begin testing:**

```bash
python main_application.py
```

**Welcome to Fatigue Tester V2.3! 🎉**

---

*Quick Start Guide - Version 2.3*  
*Last Updated: February 12, 2026*  
*Authors: Uwe Hasenstab and Alexander Waal*
