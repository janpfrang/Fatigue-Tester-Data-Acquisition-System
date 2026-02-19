"""
Data Parser module for Fatigue Tester
Handles parsing and validation of serial data

CNF line field assignments fully verified against hardware display screen
using 3 real test logs (100 N / 200 N / 220 N) and 2 screen photographs
(Feb 2026).  All encodings confirmed.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import config


# ─────────────────────────────────────────────────────────────────────────────
# Machine Configuration  (decoded from CNF header line)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CNFConfig:
    """
    Machine configuration decoded from a CNF header line.

    CNF field map (1-based index after the 'CNF;' prefix):
        Field  1        config_id           uint8
        Field  6        kraft2_int          uint8  = integer copy of Kraft @2 [N]
        Fields  8– 9    kraft2_N            uint16_LE ÷ 10   [N]   Kraft @2  (upper force target)
        Fields 10–11    kraftsoll2_N        uint16_LE ÷ 10   [N]   Kraftsoll @2 (= kraft2_N)
        Fields 12–13    nrw_k1_mm           uint16_LE ÷ 100  [mm]  Nachregelweg Kraft 1
        Fields 14–15    nrw_k2_mm           uint16_LE ÷ 100  [mm]  Nachregelweg Kraft 2
        Fields 16–17    kraftabschaltung_N  uint16_LE ÷ 10   [N]   Emergency force cutoff
        Field  18       toleranz_pct        uint8            [%]   Force tolerance band ±%
        Fields 22–23    messen_alle_n       uint16_LE        [#]   Log every N cycles
        Field  24       kraft1_ratio        uint8                  Kraft @1 = Kraft @2 ÷ ratio
        Fields 29–32    betaetigungen       uint32_LE        [#]   Planned total cycles
        [Derived]       kraft1_N            = kraft2_N / kraft1_ratio  [N]  Lower force target
    """
    # Core force targets
    kraft2_N: float         = 0.0   # Kraft @2  — upper force target [N]
    kraftsoll2_N: float     = 0.0   # Kraftsoll @2 — duplicate of kraft2_N [N]
    kraft1_N: float         = 0.0   # Kraft @1  — lower force target (derived) [N]
    kraft1_ratio: int       = 0     # Divisor: Kraft@1 = Kraft@2 / ratio

    # Safety & tolerances
    kraftabschaltung_N: float = 0.0 # Emergency force cutoff [N]
    toleranz_pct: int         = 0   # Force tolerance band ±% [%]

    # Position-correction budgets (Nachregelweg)
    nrw_k1_mm: float        = 0.0   # Nachregelweg Kraft 1 [mm]
    nrw_k2_mm: float        = 0.0   # Nachregelweg Kraft 2 [mm]

    # Cycle control
    betaetigungen: int      = 0     # Planned total cycles [#]
    messen_alle_n: int      = 0     # Log every N cycles [#]

    # Device identification (parsed from surrounding header lines)
    device_version: str     = ""    # e.g. "V1.5"
    device_id: str          = ""    # e.g. "2BC4D630"
    display_id: str         = ""    # e.g. "ceSID-48339C75"

    # Internal
    config_id: int          = 0     # CNF field 1
    raw_cnf: str            = ""    # full raw CNF line for audit trail
    parse_ok: bool          = False # True if successfully decoded

    # ── derived helpers ───────────────────────────────────────────────────
    def force_tolerance_window(self) -> Tuple[float, float]:
        """Return (lower_limit, upper_limit) for Kraft @2 based on Toleranz %."""
        delta = self.kraft2_N * self.toleranz_pct / 100.0
        return (self.kraft2_N - delta, self.kraft2_N + delta)

    def to_display_rows(self) -> list:
        """
        Return a list of (label, value_str, unit) tuples for the
        MachineConfigPanel table — mirrors the hardware 'Parameter' screen.
        """
        lo, hi = self.force_tolerance_window()
        return [
            # ── Force targets ──────────────────────────────────────────
            ("Kraft @2  (upper)",        f"{self.kraft2_N:.1f}",         "N"),
            ("Kraftsoll @2",             f"{self.kraftsoll2_N:.1f}",     "N"),
            ("Kraft @1  (lower)",        f"{self.kraft1_N:.1f}",         "N  (= @2 ÷ ratio)"),
            ("Force ratio",              f"1 : {self.kraft1_ratio}",     ""),
            # ── Safety ─────────────────────────────────────────────────
            ("Kraftabschaltung",         f"{self.kraftabschaltung_N:.1f}","N  (emergency cutoff)"),
            ("Kraftsoll @2 Toleranz",    f"± {self.toleranz_pct}",       "%"),
            ("  Force window",           f"{lo:.1f} – {hi:.1f}",        "N"),
            # ── Nachregelweg ────────────────────────────────────────────
            ("Nachregelweg Kraft 1",     f"{self.nrw_k1_mm:.2f}",        "mm  (pos-correction budget)"),
            ("Nachregelweg Kraft 2",     f"{self.nrw_k2_mm:.2f}",        "mm  (pos-correction budget)"),
            # ── Cycle control ───────────────────────────────────────────
            ("Betätigungen",             f"{self.betaetigungen:,}",      "#  (planned cycles)"),
            ("Messen alle N",            f"{self.messen_alle_n}",        "#  (log interval)"),
            # ── Device ──────────────────────────────────────────────────
            ("Device",                   f"{self.device_version}",       f"ID: {self.device_id}"),
            ("Display",                  f"{self.display_id}",           ""),
        ]


@dataclass
class FatigueTestData:
    """Structured data from fatigue test"""
    timestamp: datetime
    status: str
    cycles: int
    position_1_mm: float
    force_lower_n: float
    travel_1_mm: float
    position_2_mm: float
    force_upper_n: float
    travel_2_mm: float
    travel_at_upper_mm: float
    error_code: int
    raw_data: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for CSV export"""
        return {
            'Timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'Status': self.status,
            'Cycles': self.cycles,
            'Position_1_mm': self.position_1_mm,
            'Force_Lower_N': self.force_lower_n,
            'Travel_1_mm': self.travel_1_mm,
            'Position_2_mm': self.position_2_mm,
            'Force_Upper_N': self.force_upper_n,
            'Travel_2_mm': self.travel_2_mm,
            'Travel_at_Upper_mm': self.travel_at_upper_mm,
            'Loss_of_Stiffness_Percent': self.calculate_loss_of_stiffness(),
            'Error_Code': self.error_code,
            'Error_Description': config.ERROR_CODES.get(self.error_code, "Unknown Error"),
            'Raw_Data': self.raw_data
        }
    
    def calculate_loss_of_stiffness(self) -> float:
        """Calculate loss of stiffness percentage"""
        if self.travel_at_upper_mm == 0:
            return 0.0
        return (self.travel_2_mm / self.travel_at_upper_mm) * 100.0
    
    def is_test_end(self) -> bool:
        """Check if test has ended"""
        return self.status == "END"
    
    def has_error(self) -> bool:
        """Check if there's an error"""
        return self.error_code != 0


class DataParser:
    """Parser for fatigue test serial data"""
    
    def __init__(self):
        self.parse_errors = 0
        
    def parse(self, raw_data: str) -> Optional[FatigueTestData]:
        """
        Parse raw serial data string
        
        Expected format: DTA;31422;182;263;0;793;2238;0;611;0;!
        
        Args:
            raw_data: Raw string from serial port
            
        Returns:
            FatigueTestData object or None if parsing fails
        """
        try:
            # Remove trailing exclamation mark and whitespace
            raw_data = raw_data.strip()
            if raw_data.endswith('!'):
                raw_data = raw_data[:-1]
            
            # Split by semicolon
            parts = raw_data.split(';')
            
            if len(parts) != 11:
                raise ValueError(f"Expected 11 fields, got {len(parts)}")
            
            # Parse each field with proper decimal conversion
            status = parts[0].strip()
            cycles = int(parts[1])
            position_1_mm = int(parts[2]) / 100.0  # Last 2 digits are decimals
            force_lower_n = int(parts[3]) / 10.0    # Last digit is decimal
            travel_1_mm = int(parts[4]) / 100.0 # Last 2 digits are decimals
            position_2_mm = int(parts[5]) / 100.0  # Last 2 digits are decimals
            force_upper_n = int(parts[6]) / 10.0    # Last digit is decimal
            travel_2_mm = int(parts[7]) / 100.0 # Last 2 digits are decimals
            travel_at_upper_mm = int(parts[8]) / 100.0  # Last 2 digits are decimals
            error_code = int(parts[9])
            
            # Create structured data object
            return FatigueTestData(
                timestamp=datetime.now(),
                status=status,
                cycles=cycles,
                position_1_mm=position_1_mm,
                force_lower_n=force_lower_n,
                travel_1_mm=travel_1_mm,
                position_2_mm=position_2_mm,
                force_upper_n=force_upper_n,
                travel_2_mm=travel_2_mm,
                travel_at_upper_mm=travel_at_upper_mm,
                error_code=error_code,
                raw_data=raw_data + '!'
            )
            
        except (ValueError, IndexError) as e:
            self.parse_errors += 1
            print(f"Parse error #{self.parse_errors}: {e} - Data: {raw_data}")
            return None
    
    def validate_data(self, data: FatigueTestData) -> Tuple[bool, str]:
        """
        Validate parsed data for reasonableness
        
        Returns:
            (is_valid, error_message)
        """
        # Basic range checks
        if data.cycles < 0:
            return False, "Invalid cycle count (negative)"
        
        if data.status not in ["DTA", "END"]:
            return False, f"Invalid status: {data.status}"
        
        # Note: Negative values for force and position are allowed per V2 requirements
        # Upper force should typically be greater than lower force (but not enforced strictly)
        
        return True, "OK"
    
    def get_error_description(self, error_code: int) -> str:
        """Get human-readable error description"""
        return config.ERROR_CODES.get(error_code, f"Unknown Error Code: {error_code}")

    # ─────────────────────────────────────────────────────────────────────────
    # CNF header line parsing
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def parse_cnf_line(raw: str) -> CNFConfig:
        """
        Decode a CNF configuration line into a CNFConfig dataclass.

        All field assignments verified against hardware display screen
        (3 test logs × 2 screen photos, Feb 2026).

        Args:
            raw: complete CNF line string, e.g. "CNF;49;0;...;!"

        Returns:
            CNFConfig — parse_ok=True on success, False on any error
        """
        cfg = CNFConfig(raw_cnf=raw)
        try:
            values = [int(x) for x in raw.replace('!', '').split(';')[1:]
                      if x.strip().lstrip('-').isdigit()]

            if len(values) < 32:
                return cfg   # parse_ok stays False

            def u16(i: int) -> int:
                return values[i] + (values[i + 1] << 8)

            def u32(i: int) -> int:
                return (values[i]
                        + (values[i + 1] << 8)
                        + (values[i + 2] << 16)
                        + (values[i + 3] << 24))

            cfg.config_id           = values[0]           # field 1
            cfg.kraft2_N            = u16(7)  / 10.0      # fields 8-9
            cfg.kraftsoll2_N        = u16(9)  / 10.0      # fields 10-11
            cfg.nrw_k1_mm           = u16(11) / 100.0     # fields 12-13
            cfg.nrw_k2_mm           = u16(13) / 100.0     # fields 14-15
            cfg.kraftabschaltung_N  = u16(15) / 10.0      # fields 16-17
            cfg.toleranz_pct        = values[17]           # field  18
            cfg.messen_alle_n       = u16(21)              # fields 22-23
            cfg.kraft1_ratio        = values[23]           # field  24
            cfg.betaetigungen       = u32(28)              # fields 29-32

            # Derive Kraft @1 from ratio
            if cfg.kraft1_ratio > 0:
                cfg.kraft1_N = cfg.kraft2_N / cfg.kraft1_ratio

            cfg.parse_ok = True

        except Exception as e:
            print(f"CNFConfig parse error: {e}  —  raw: {raw[:80]}")

        return cfg

    @staticmethod
    def parse_header_block(lines: list) -> CNFConfig:
        """
        Parse a sequence of header lines (as received on startup) and return
        a populated CNFConfig, including device identification extracted from
        the surrounding text lines.

        Args:
            lines: list of raw strings from the header section

        Returns:
            CNFConfig (parse_ok=True only if a valid CNF line was found)
        """
        cfg = CNFConfig()

        for line in lines:
            line = line.strip()

            # ── Device ID & version ──────────────────────────────────────────
            if '### VoiceCoilTestStand' in line:
                for token in line.split():
                    if token.startswith('V') and len(token) > 1:
                        cfg.device_version = token
                    if token.startswith('ID='):
                        cfg.device_id = token.split('=', 1)[1].rstrip('#').strip()

            # ── Display controller ID ────────────────────────────────────────
            elif line.startswith('For display'):
                parts = line.split()
                if len(parts) >= 3:
                    cfg.display_id = parts[2]

            # ── CNF line ─────────────────────────────────────────────────────
            elif line.startswith('CNF;'):
                parsed = DataParser.parse_cnf_line(line)
                if parsed.parse_ok:
                    # Carry over device info gathered above
                    parsed.device_version = cfg.device_version
                    parsed.device_id      = cfg.device_id
                    parsed.display_id     = cfg.display_id
                    cfg = parsed

        return cfg
