"""
Serial Port Detector Module - Hardware Abstraction Layer Extension
==================================================================

This module extends the hardware abstraction layer (serial_reader.py) by
providing automatic COM port detection capabilities. It follows the same
architecture as the rest of the Fatigue Tester Data Acquisition System.

Part of: Fatigue Tester Data Acquisition System v2.2
Layer: Hardware Abstraction (Producer)

Integrated with:
- config.py: Uses SerialConfig for configuration
- serial_reader.py: Complements SerialReader with port detection
- main_application.py: Provides GUI integration methods
"""

import serial
import platform
import threading
from typing import List, Optional, Callable, Dict
from dataclasses import dataclass
from pathlib import Path
import logging


# Configure logging for this module
logger = logging.getLogger(__name__)


@dataclass
class DetectedPort:
    """
    Represents a detected serial port
    
    Attributes:
        port (str): Port name (e.g., 'COM3', '/dev/ttyUSB0')
        description (str): Human-readable description
        is_available (bool): Whether port can be opened
        device_path (str): Full device path if available
    """
    port: str
    description: str = ""
    is_available: bool = True
    device_path: str = ""
    
    def __str__(self) -> str:
        """User-friendly string representation"""
        status = "✓" if self.is_available else "✗"
        if self.description:
            return f"{self.port} - {self.description} ({status})"
        return f"{self.port} ({status})"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/serialization"""
        return {
            'port': self.port,
            'description': self.description,
            'is_available': self.is_available,
            'device_path': self.device_path
        }


class SerialPortDetector:
    """
    Detects available serial ports on the system.
    
    Part of the Hardware Abstraction Layer for detecting available ports
    before attempting connection. Works cross-platform with graceful fallbacks.
    
    Architecture: Hardware Abstraction Layer (Producer)
    Singleton pattern recommended for application lifecycle.
    """
    
    def __init__(self, timeout: float = 0.5, logger_instance=None):
        """
        Initialize port detector
        
        Args:
            timeout: Port open timeout in seconds for availability testing
            logger_instance: Optional logger instance (uses module logger if None)
        """
        self.timeout = timeout
        self.logger = logger_instance or logger
        self._detected_ports: List[DetectedPort] = []
        self._last_detection_time: Optional[float] = None
        self._detection_lock = threading.Lock()
    
    def detect_ports(self, use_cache: bool = False, cache_timeout: float = 30.0) -> List[DetectedPort]:
        """
        Detect all available serial ports on the system.
        
        Thread-safe operation with optional caching for performance.
        
        Args:
            use_cache: If True, return cached results if available
            cache_timeout: Cache validity duration in seconds
            
        Returns:
            List of DetectedPort objects, empty if none found
        """
        import time
        
        with self._detection_lock:
            # Check cache validity
            if use_cache and self._detected_ports:
                if self._last_detection_time:
                    elapsed = time.time() - self._last_detection_time
                    if elapsed < cache_timeout:
                        self.logger.debug(f"Returning cached ports (age: {elapsed:.1f}s)")
                        return self._detected_ports
            
            # Detect ports
            ports = self._detect_ports_internal()
            
            # Update cache
            self._detected_ports = ports
            self._last_detection_time = time.time()
            
            return ports
    
    def _detect_ports_internal(self) -> List[DetectedPort]:
        """
        Internal port detection using platform-specific methods.
        
        Returns:
            List of DetectedPort objects
        """
        try:
            system = platform.system()
            
            if system == "Windows":
                ports = self._detect_windows_ports()
            elif system == "Darwin":
                ports = self._detect_macos_ports()
            elif system == "Linux":
                ports = self._detect_linux_ports()
            else:
                ports = self._detect_generic_ports()
            
            self.logger.info(f"Detected {len(ports)} port(s) on {system}")
            return ports
            
        except Exception as e:
            self.logger.error(f"Error detecting ports: {e}", exc_info=True)
            return []
    
    def _detect_windows_ports(self) -> List[DetectedPort]:
        """Detect COM ports on Windows"""
        ports = []
        
        try:
            from serial.tools import list_ports
            
            for port_info in list_ports.comports():
                is_available = self._test_port_availability(port_info.device)
                port = DetectedPort(
                    port=port_info.device,
                    description=port_info.description,
                    is_available=is_available,
                    device_path=port_info.device
                )
                ports.append(port)
                self.logger.debug(f"Found Windows port: {port}")
        
        except ImportError:
            self.logger.warning("pyserial.tools.list_ports not available, testing common ports")
            ports = self._test_common_windows_ports()
        
        except Exception as e:
            self.logger.error(f"Error detecting Windows ports: {e}", exc_info=True)
            ports = self._test_common_windows_ports()
        
        return ports
    
    def _detect_linux_ports(self) -> List[DetectedPort]:
        """Detect serial ports on Linux"""
        ports = []
        
        try:
            from serial.tools import list_ports
            
            for port_info in list_ports.comports():
                is_available = self._test_port_availability(port_info.device)
                port = DetectedPort(
                    port=port_info.device,
                    description=port_info.description,
                    is_available=is_available,
                    device_path=port_info.device
                )
                ports.append(port)
                self.logger.debug(f"Found Linux port: {port}")
        
        except ImportError:
            self.logger.warning("pyserial.tools.list_ports not available, scanning /dev")
            ports = self._scan_linux_dev_ports()
        
        except Exception as e:
            self.logger.error(f"Error detecting Linux ports: {e}", exc_info=True)
            ports = self._scan_linux_dev_ports()
        
        return ports
    
    def _detect_macos_ports(self) -> List[DetectedPort]:
        """Detect serial ports on macOS"""
        ports = []
        
        try:
            from serial.tools import list_ports
            
            for port_info in list_ports.comports():
                is_available = self._test_port_availability(port_info.device)
                port = DetectedPort(
                    port=port_info.device,
                    description=port_info.description,
                    is_available=is_available,
                    device_path=port_info.device
                )
                ports.append(port)
                self.logger.debug(f"Found macOS port: {port}")
        
        except ImportError:
            self.logger.warning("pyserial.tools.list_ports not available, scanning /dev")
            ports = self._scan_macos_dev_ports()
        
        except Exception as e:
            self.logger.error(f"Error detecting macOS ports: {e}", exc_info=True)
            ports = self._scan_macos_dev_ports()
        
        return ports
    
    def _detect_generic_ports(self) -> List[DetectedPort]:
        """Generic port detection fallback"""
        ports = []
        
        try:
            from serial.tools import list_ports
            
            for port_info in list_ports.comports():
                is_available = self._test_port_availability(port_info.device)
                port = DetectedPort(
                    port=port_info.device,
                    description=port_info.description,
                    is_available=is_available,
                    device_path=port_info.device
                )
                ports.append(port)
        
        except Exception as e:
            self.logger.error(f"Generic port detection failed: {e}", exc_info=True)
        
        return ports
    
    def _test_common_windows_ports(self) -> List[DetectedPort]:
        """Test common Windows COM ports (1-16)"""
        ports = []
        for i in range(1, 17):
            port_name = f"COM{i}"
            is_available = self._test_port_availability(port_name)
            if is_available:
                port = DetectedPort(
                    port=port_name,
                    description="",
                    is_available=is_available
                )
                ports.append(port)
                self.logger.debug(f"Found Windows port: {port_name}")
        
        return ports
    
    def _scan_linux_dev_ports(self) -> List[DetectedPort]:
        """Scan Linux /dev directory for serial ports"""
        import glob
        
        ports = []
        patterns = ['/dev/ttyUSB*', '/dev/ttyACM*', '/dev/ttyS*']
        
        for pattern in patterns:
            for dev_path in glob.glob(pattern):
                port_name = Path(dev_path).name
                is_available = self._test_port_availability(dev_path)
                port = DetectedPort(
                    port=dev_path,
                    description="",
                    is_available=is_available,
                    device_path=dev_path
                )
                ports.append(port)
                self.logger.debug(f"Found Linux port: {dev_path}")
        
        return ports
    
    def _scan_macos_dev_ports(self) -> List[DetectedPort]:
        """Scan macOS /dev directory for serial ports"""
        import glob
        
        ports = []
        patterns = ['/dev/tty.*', '/dev/cu.*']
        
        for pattern in patterns:
            for dev_path in glob.glob(pattern):
                if 'serial' in dev_path or 'usbserial' in dev_path or 'usb' in dev_path:
                    port_name = Path(dev_path).name
                    is_available = self._test_port_availability(dev_path)
                    port = DetectedPort(
                        port=dev_path,
                        description="",
                        is_available=is_available,
                        device_path=dev_path
                    )
                    ports.append(port)
                    self.logger.debug(f"Found macOS port: {dev_path}")
        
        return ports
    
    def _test_port_availability(self, port: str) -> bool:
        """
        Test if a port can be opened and is available.
        
        Args:
            port: Port name to test
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            ser = serial.Serial(port, timeout=self.timeout)
            ser.close()
            self.logger.debug(f"Port {port} is available")
            return True
        except (serial.SerialException, OSError, Exception) as e:
            self.logger.debug(f"Port {port} is not available: {type(e).__name__}")
            return False
    
    def get_port_names(self) -> List[str]:
        """
        Get list of available port names only.
        
        Returns:
            List of port name strings (e.g., ['COM3', 'COM5'])
        """
        ports = self.detect_ports(use_cache=True)
        return [p.port for p in ports]
    
    def get_available_ports(self) -> List[str]:
        """
        Get list of available (openable) port names.
        
        Returns:
            List of available port name strings
        """
        ports = self.detect_ports(use_cache=True)
        return [p.port for p in ports if p.is_available]
    
    def find_fatigue_tester_port(self) -> Optional[str]:
        """
        Attempt to find Fatigue Tester port by description.
        
        Looks for keywords that might identify the device.
        Falls back to first available port if not found.
        
        Returns:
            Port name if found, None otherwise
        """
        ports = self.detect_ports(use_cache=True)
        
        # Keywords that might identify Fatigue Tester
        keywords = ['fatigue', 'tester', 'ftester', 'ch340', 'ft232', 'cp2102', 'uart']
        
        for port in ports:
            desc = port.description.lower()
            if any(kw in desc for kw in keywords):
                self.logger.info(f"Found potential Fatigue Tester on {port.port}")
                return port.port
        
        # Fall back to first available port
        available = self.get_available_ports()
        if available:
            self.logger.info(f"Using first available port: {available[0]}")
            return available[0]
        
        self.logger.warning("Could not find suitable port")
        return None
    
    def clear_cache(self):
        """Clear the detection cache"""
        with self._detection_lock:
            self._detected_ports = []
            self._last_detection_time = None
            self.logger.debug("Port detection cache cleared")


# Singleton instance for application-wide use
_port_detector_instance: Optional[SerialPortDetector] = None


def get_port_detector(timeout: float = 0.5) -> SerialPortDetector:
    """
    Get or create the singleton SerialPortDetector instance.
    
    This follows the singleton pattern recommended for the hardware
    abstraction layer in this architecture.
    
    Args:
        timeout: Port availability test timeout
        
    Returns:
        SerialPortDetector instance
    """
    global _port_detector_instance
    
    if _port_detector_instance is None:
        _port_detector_instance = SerialPortDetector(timeout=timeout)
    
    return _port_detector_instance


# Example/Testing
if __name__ == "__main__":
    import sys
    
    # Setup basic logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='[%(name)s] %(levelname)s: %(message)s'
    )
    
    detector = get_port_detector()
    
    print("\n" + "="*70)
    print("Serial Port Detector - Testing")
    print("="*70)
    print(f"Operating System: {platform.system()}\n")
    
    print("Detecting ports...")
    ports = detector.detect_ports()
    
    if ports:
        print(f"Found {len(ports)} port(s):\n")
        for i, port in enumerate(ports, 1):
            print(f"  {i}. {port}")
        
        print(f"\nAvailable ports: {detector.get_available_ports()}")
        
        suggested = detector.find_fatigue_tester_port()
        if suggested:
            print(f"Suggested port: {suggested}")
    else:
        print("No ports detected")
    
    print("="*70 + "\n")
