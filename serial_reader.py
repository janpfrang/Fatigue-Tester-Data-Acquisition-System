"""
Serial Reader module - Hardware Abstraction Layer (Producer)
Handles serial communication in a separate thread
"""

import serial
import threading
import queue
import time
from typing import Optional, Callable
from config import SerialConfig


class SerialReader(threading.Thread):
    """
    Producer thread that reads data from serial port
    Implements hardware abstraction for testability
    """
    
    def __init__(self, config: SerialConfig, data_queue: queue.Queue, 
                 status_callback: Optional[Callable] = None):
        """
        Initialize serial reader
        
        Args:
            config: Serial configuration
            data_queue: Queue to put received data
            status_callback: Optional callback for status updates
        """
        super().__init__(daemon=True)
        self.config = config
        self.data_queue = data_queue
        self.status_callback = status_callback
        self.serial_port: Optional[serial.Serial] = None
        self.running = False
        self._stop_event = threading.Event()
        self.bytes_received = 0
        self.lines_received = 0
        
    def connect(self) -> bool:
        """
        Connect to serial port
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.serial_port = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                bytesize=self.config.bytesize,
                parity=self.config.parity,
                stopbits=self.config.stopbits,
                timeout=self.config.timeout
            )
            self._update_status(f"Connected to {self.config.port}")
            return True
        except serial.SerialException as e:
            self._update_status(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port"""
        self.stop()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            self._update_status("Disconnected")
    
    def run(self):
        """Main thread loop - reads data from serial port"""
        self.running = True
        self._update_status("Reader thread started")
        
        while not self._stop_event.is_set() and self.running:
            try:
                if self.serial_port and self.serial_port.is_open:
                    if self.serial_port.in_waiting > 0:
                        # Read line from serial port
                        raw_data = self.serial_port.readline()
                        self.bytes_received += len(raw_data)
                        
                        # Decode and strip whitespace
                        decoded_data = raw_data.decode('utf-8', errors='ignore').strip()
                        
                        if decoded_data:
                            self.lines_received += 1
                            # Put data in queue for processing
                            self.data_queue.put(decoded_data)
                    else:
                        # Small sleep to prevent CPU spinning
                        time.sleep(0.01)
                else:
                    # Not connected, wait before checking again
                    time.sleep(0.1)
                    
            except serial.SerialException as e:
                self._update_status(f"Serial error: {e}")
                self.running = False
                break
            except Exception as e:
                self._update_status(f"Unexpected error: {e}")
                time.sleep(0.1)
        
        self._update_status("Reader thread stopped")
    
    def stop(self):
        """Stop the reader thread"""
        self.running = False
        self._stop_event.set()
    
    def _update_status(self, message: str):
        """Send status update via callback"""
        if self.status_callback:
            self.status_callback(message)
        print(f"[SerialReader] {message}")
    
    def get_statistics(self) -> dict:
        """Get reader statistics"""
        return {
            'bytes_received': self.bytes_received,
            'lines_received': self.lines_received,
            'is_running': self.running,
            'is_connected': self.serial_port.is_open if self.serial_port else False
        }


class MockSerialReader(threading.Thread):
    """
    Mock serial reader for testing UI without hardware
    Generates simulated data
    """
    
    def __init__(self, data_queue: queue.Queue, interval: float = 0.5,
                 status_callback: Optional[Callable] = None):
        """
        Initialize mock reader
        
        Args:
            data_queue: Queue to put simulated data
            interval: Time between data points (seconds)
            status_callback: Optional callback for status updates
        """
        super().__init__(daemon=True)
        self.data_queue = data_queue
        self.interval = interval
        self.status_callback = status_callback
        self.running = False
        self._stop_event = threading.Event()
        self.cycle_count = 0
        
    def run(self):
        """Generate simulated data"""
        self.running = True
        self._update_status("Mock reader started")
        
        while not self._stop_event.is_set() and self.running:
            self.cycle_count += 1
            
            # Generate realistic test data
            import random
            position_0 = 180 + random.randint(-5, 5)
            force_lower = 250 + random.randint(-20, 20)
            travel_lower = random.randint(-2, 2)
            position_upper = 790 + random.randint(-10, 10)
            force_upper = 2200 + random.randint(-50, 50)
            travel_upper = random.randint(-3, 3)
            travel_at_upper = 610 + random.randint(-5, 5)
            error_code = 0 if random.random() > 0.05 else random.choice([0, 11, 12])
            
            # Format data string
            mock_data = (f"DTA;{self.cycle_count};{position_0};{force_lower};"
                        f"{travel_lower};{position_upper};{force_upper};"
                        f"{travel_upper};{travel_at_upper};{error_code};!")
            
            self.data_queue.put(mock_data)
            
            # Wait for interval or stop event
            self._stop_event.wait(self.interval)
        
        self._update_status("Mock reader stopped")
    
    def stop(self):
        """Stop the mock reader"""
        self.running = False
        self._stop_event.set()
    
    def _update_status(self, message: str):
        """Send status update via callback"""
        if self.status_callback:
            self.status_callback(message)
        print(f"[MockSerialReader] {message}")
