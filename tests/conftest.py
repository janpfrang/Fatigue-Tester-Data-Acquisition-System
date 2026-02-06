# tests/conftest.py
"""
Shared test fixtures and configuration
"""

import pytest
import tempfile
from pathlib import Path
from config import LogConfig, SerialConfig, PlotConfig, WatchdogConfig


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for log files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup after test
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def log_config():
    """Provide LogConfig for tests"""
    return LogConfig()


@pytest.fixture
def serial_config():
    """Provide SerialConfig for tests"""
    return SerialConfig()


@pytest.fixture
def plot_config():
    """Provide PlotConfig for tests"""
    return PlotConfig()


@pytest.fixture
def watchdog_config():
    """Provide WatchdogConfig for tests"""
    return WatchdogConfig()