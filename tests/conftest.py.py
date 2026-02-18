"""
pytest configuration and fixtures for Fatigue Tester tests
"""

import sys
import os
from pathlib import Path

# Add project root to Python path so tests can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from PyQt5.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """
    Fixture that creates a QApplication instance for all GUI tests
    This is needed for any test that creates Qt widgets
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Cleanup happens automatically when session ends

@pytest.fixture
def mock_serial_config():
    """Fixture providing a mock serial configuration"""
    from config import SerialConfig
    return SerialConfig(
        port='COM_TEST',
        baudrate=115200,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=1
    )
