import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import datetime
import csv
import smtplib
from email.message import EmailMessage
import queue
import zipfile
import os
import board
import busio
import collections
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Hardware Setup ---
try:
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    chan = AnalogIn(ads, ADS.P0)
    HARDWARE_CONNECTED = True
except Exception as e:
    print(f"Hardware not found. Running in simulation mode. Error: {e}")
    HARDWARE_CONNECTED = False
    import math

# ==================================================================
# Rainflow-Accumulator (Fixed Memory)
# ==================================================================
class RainflowAccumulator:
    MIN_AMPLITUDE = 0.1    # mm, ignore tiny noise cycles
    HIST_BINS = 200        # Number of histogram bins
    HIST_MAX_AMP = 80.0    # mm, max expected amplitude (covers your 75mm pot)

    def __init__(self):
        self.lock = threading.Lock()
        self.stack = []           
        self.last_val = None
        self.last_dir = 0         

        self.bin_edges = np.linspace(0, self.HIST_MAX_AMP, self.HIST_BINS + 1)
        self.bin_counts = np.zeros(self.HIST_BINS, dtype=np.float64)
        self.total_count = 0.0
        self.max_amplitude = 0.0
        self._dirty = False

    def feed(self, value: float):
        with self.lock:
            if self.last_val is None:
                self.last_val = value
                return

            diff = value - self.last_val
            if abs(diff) < 1e-9:
                return

            direction = 1 if diff > 0 else -1

            if self.last_dir == 0:
                self.last_dir = direction
                self.stack.append(self.last_val)
                self.last_val = value
                return

            if direction != self.last_dir:
                self.stack.append(self.last_val)
                self._extract_cycles()
                self.last_dir = direction

            self.last_val = value

    def _extract_cycles(self):
        while len(self.stack) >= 4:
            s0, s1, s2, s3 = self.stack[-4], self.stack[-3], self.stack[-2], self.stack[-1]

            r_inner = abs(s1 - s2)
            r_outer_left = abs(s0 - s1)
            r_outer_right = abs(s2 - s3)

            if r_inner <= r_outer_left and r_inner <= r_outer_right:
                amp = r_inner / 2.0
                del self.stack[-3]
                del self.stack[-2]

                if amp >= self.MIN_AMPLITUDE:
                    bin_idx = int(amp / self.HIST_MAX_AMP * self.HIST_BINS)
                    bin_idx = min(bin_idx, self.HIST_BINS - 1)
                    self.bin_counts[bin_idx] += 1.0
                    self.total_count += 1.0
                    if amp > self.max_amplitude:
                        self.max_amplitude = amp
                    self._dirty = True
            else:
                break

    def get_summary(self):
        with self.lock:
            return (self.total_count, self.max_amplitude)

# ==================================================================
# Main Application
# ==================================================================
class FatigueTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fatigue Tester - Potentiometer Log")
        self.root.geometry("1000x650")
        self.running = True

        # --- State Variables ---
        self.is_logging = False
        self.is_emailing = False
        self.start_time = time.time()
        self.cal_points = {0: 0.1, 30: 1.6, 75: 3.2} 
        
        # UI Buffers & Hardware Settings
        self.plot_len = 500
        self.time_data = collections.deque(maxlen=self.plot_len)
        self.mm_data = collections.deque(maxlen=self.plot_len)
        
        self.sample_rates = {"10 SPS": (16, 0.1), "50 SPS": (64, 0.02), 
                             "100 SPS": (128, 0.01), "200 SPS": (250, 0.005), 
                             "Max SPS": (860, 0.001)}
        self.current_sleep = 0.1

        # Objects & Queues
        self.rf_acc = RainflowAccumulator()
        self.data_queue = queue.Queue()       
        self.email_queue = queue.Queue()      

        self.setup_ui()
        
        # Start Threads
        threading.Thread(target=self.sensor_loop, daemon=True).start()
        threading.Thread(target=self.disk_writer_loop, daemon=True).start()
        threading.Thread(target=self.email_loop, daemon=True).start()
        
        self.update_plot()

    def setup_ui(self):
        plot_frame = tk.Frame(self.root)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 5), dpi=100)
        self.ax.set_title("Live Displacement (mm)")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Position (mm)")
        self.ax.set_ylim(-5, 80)
        self.line, = self.ax.plot([], [], 'b-')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(self.root, width=300, padx=10, pady=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 1. Calibration
        calib_lf = tk.LabelFrame(control_frame, text="Calibration", padx=5, pady=5)
        calib_lf.pack(fill=tk.X, pady=5)
        self.calib_label = tk.Label(calib_lf, text="Current Volts: 0.00 V\nCurrent Pos: 0.0 mm")
        self.calib_label.pack(pady=5)
        tk.Button(calib_lf, text="Set 0 mm", command=lambda: self.calibrate(0)).pack(fill=tk.X)
        tk.Button(calib_lf, text="Set 30 mm", command=lambda: self.calibrate(30)).pack(fill=tk.X)
        tk.Button(calib_lf, text="Set 75 mm", command=lambda: self.calibrate(75)).pack(fill=tk.X)

        # 2. Fatigue Stats (NEW)
        stats_lf = tk.LabelFrame(control_frame, text="Fatigue Stats", padx=5, pady=5)
        stats_lf.pack(fill=tk.X, pady=5)
        self.stats_label = tk.Label(stats_lf, text="Cycles: 0\nMax Amp: 0.00 mm", font=("Helvetica", 12, "bold"), fg="blue")
        self.stats_label.pack(pady=5)

        # 3. Sampling Rate
        samp_lf = tk.LabelFrame(control_frame, text="Sampling Rate", padx=5, pady=5)
        samp_lf.pack(fill=tk.X, pady=5)
        self.rate_var = tk.StringVar(value="10 SPS")
        rate_dropdown = ttk.Combobox(samp_lf, textvariable=self.rate_var, values=list(self.sample_rates.keys()), state="readonly")
        rate_dropdown.pack(fill=tk.X)
        rate_dropdown.bind("<<ComboboxSelected>>", self.change_rate)

        # 4. Data Logging
        log_lf = tk.LabelFrame(control_frame, text="Data Logging", padx=5, pady=5)
        log_lf.pack(fill=tk.X, pady=5)
        self.log_btn = tk.Button(log_lf, text="Start Logging", bg="lightgreen", command=self.toggle_logging)
        self.log_btn.pack(fill=tk.X, pady=5)

        # 5. Hourly Email Push
        email_lf = tk.LabelFrame(control_frame, text="Hourly Email Push", padx=5, pady=5)
        email_lf.pack(fill=tk.X, pady=5)
        tk.Label(email_lf, text="Receiver Email:").pack(anchor="w")
        self.email_entry = tk.Entry(email_lf)
        self.email_entry.pack(fill=tk.X)
        self.email_entry.insert(0, "user@example.com")
        self.email_btn = tk.Button(email_lf, text="Enable Auto-Email", bg="lightgray", command=self.toggle_email)
        self.email_btn.pack(fill=tk.X, pady=5)

    def change_rate(self, event):
        selection = self.rate_var.get()
        ads_rate, sleep_time = self.sample_rates[selection]
        if HARDWARE_CONNECTED:
            ads.data_rate = ads_rate
        self.current_sleep = sleep_time

    def calibrate(self, position):
        if not HARDWARE_CONNECTED: return
        self.cal_points[position] = chan.voltage

    def get_mm_from_voltage(self, v):
        v0, v30, v75 = self.cal_points[0], self.cal_points[30], self.cal_points[75]
        if v <= v30:
            if v30 == v0: return 0 
            mm = 0 + (30 - 0) * ((v - v0) / (v30 - v0))
        else:
            if v75 == v30: return 30
            mm = 30 + (75 - 30) * ((v - v30) / (v75 - v30))
        return max(-5, min(80, mm))

    # --- 1. SENSOR THREAD ---
    def sensor_loop(self):
        rf_count_local = 0.0
        rf_max_local = 0.0

        while self.running:
            loop_start = time.time()
            t = loop_start - self.start_time
            
            # Read Hardware or Mock Data
            v = chan.voltage if HARDWARE_CONNECTED else 1.6 + math.sin(t*5)*1.5 
            mm = self.get_mm_from_voltage(v)
            
            # Feed the Rainflow Accumulator
            self.rf_acc.feed(mm)
            
            self.time_data.append(t)
            self.mm_data.append(mm)
            
            if self.is_logging:
                # Lightweight check against total_count to avoid locking unnecessarily
                new_count = self.rf_acc.total_count
                if new_count != rf_count_local:
                    rf_count_local = self.rf_acc.total_count
                    rf_max_local = self.rf_acc.max_amplitude
                
                # Push data AND rainflow stats to queue
                self.data_queue.put((f"{t:.3f}", f"{v:.4f}", f"{mm:.2f}", f"{int(rf_count_local)}", f"{rf_max_local:.3f}"))
                
            elapsed = time.time() - loop_start
            sleep_duration = self.current_sleep - elapsed
            if sleep_duration > 0:
                time.sleep(sleep_duration)

    # --- 2. DISK WRITER THREAD ---
    def disk_writer_loop(self):
        current_hour = datetime.datetime.now().hour
        current_filename = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H00')}.csv"
        
        while self.running:
            buffer = []
            while not self.data_queue.empty():
                buffer.append(self.data_queue.get())
                
            if buffer:
                now_hour = datetime.datetime.now().hour
                if now_hour != current_hour:
                    self.email_queue.put(current_filename)
                    current_hour = now_hour
                    current_filename = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H00')}.csv"
                
                file_exists = os.path.isfile(current_filename)
                with open(current_filename, "a", newline='') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        # Added Rainflow headers
                        writer.writerow(["Time_s", "Voltage_V", "Position_mm", "Total_Cycles", "Max_Amp_mm"])
                    writer.writerows(buffer)
            
            time.sleep(1)

    # --- 3. EMAIL THREAD ---
    def email_loop(self):
        while self.running:
            if not self.email_queue.empty():
                file_to_send = self.email_queue.get()
                if self.is_emailing:
                    try:
                        zip_filename = file_to_send.replace('.csv', '.zip')
                        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            zipf.write(file_to_send)
                            
                        receiver = self.email_entry.get()
                        sender = "your_pi_email@gmail.com" 
                        password = "your_app_password"     
                        
                        msg = EmailMessage()
                        msg['Subject'] = f'Fatigue Tester Log: {file_to_send}'
                        msg['From'] = sender
                        msg['To'] = receiver
                        msg.set_content('Attached is the zipped log file for the previous hour.')
                        
                        with open(zip_filename, 'rb') as f:
                            msg.add_attachment(f.read(), maintype='application', subtype='zip', filename=zip_filename)
                            
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login(sender, password)
                            smtp.send_message(msg)
                    except Exception as e:
                        print(f"Failed to process/email {file_to_send}: {e}")
            time.sleep(5) 

    # --- GUI UPDATES ---
    def update_plot(self):
        if len(self.mm_data) > 0:
            current_v = chan.voltage if HARDWARE_CONNECTED else 1.5
            
            # Update Calibration Label
            self.calib_label.config(text=f"Current Volts: {current_v:.3f} V\nCurrent Pos: {self.mm_data[-1]:.1f} mm")
            
            # Update Rainflow Label
            cycles, max_amp = self.rf_acc.get_summary()
            self.stats_label.config(text=f"Cycles: {int(cycles)}\nMax Amp: {max_amp:.2f} mm")

            # Update Plot
            self.line.set_data(self.time_data, self.mm_data)
            self.ax.set_xlim(max(0, self.time_data[-1] - 10), max(10, self.time_data[-1] + 1))
            self.canvas.draw_idle()
            
        self.root.after(100, self.update_plot)

    def toggle_logging(self):
        self.is_logging = not self.is_logging
        self.log_btn.config(text="Stop Logging", bg="lightcoral") if self.is_logging else self.log_btn.config(text="Start Logging", bg="lightgreen")

    def toggle_email(self):
        self.is_emailing = not self.is_emailing
        self.email_btn.config(text="Disable Auto-Email", bg="lightcoral") if self.is_emailing else self.email_btn.config(text="Enable Auto-Email", bg="lightgray")

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FatigueTesterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
