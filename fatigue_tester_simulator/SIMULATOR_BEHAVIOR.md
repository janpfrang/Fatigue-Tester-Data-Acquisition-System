# ESP32 Fatigue Tester Simulator - Verhalten Dokumentation

## Übersicht

Der ESP32 NodeMCU-32S simuliert jetzt realistisches Verhalten eines Fatigue Testers mit komplexen Mustern und Fehlersimulation.

## Startup-Sequenz

1. **Power-On**: 5 Sekunden Countdown
2. **Header-Übertragung**: Einmalig beim Start
3. **Datenübertragung**: Kontinuierlich alle 1000 ms (1 Hz)

## Header (einmalig beim Start)

```
### VoiceCoilTestStand V1.5 ID=2BC4D630 ###
For display ceSID-48339C75
Loading... Adr: '1' (0x31). Ok!
CNF;49;0;0;0;0;220;0;152;8;152;8;44;1;44;1;184;11;20;0;32;78;10;0;10;1;0;0;0;63;66;15;0;0;0;0;0;16;39;0;0;255;3;0;0;0;0;0;0;0;0;0;0;0;0;0;0;255;3;0;0;16;39;0;0;0;0;0;0;15;39;0;0;83;7;0;0;166;14;0;0;0;0;0;0;0;0;0;0;0;0;0;0;96;234;0;0;48;117;0;0;0;0;0;0;48;117;0;0;1;0;0;0;2;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;32;78;0;0;16;39;0;0;0;0;0;0;16;39;0;0;255;3;0;0;16;39;0;0;0;0;0;0;0;0;0;0;0;0;0;0;16;39;0;0;255;3;0;0;0;0;0;0;255;3;0;0;2;0;0;0;1;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;48;117;0;0;96;234;0;0;0;0;0;0;96;234;0;0;2;0;0;0;1;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;16;39;0;0;32;78;0;0;0;0;0;0;32;78;0;0;!
```

## Datenformat

```
DTA;cycles;pos1;lowerForce;addTravel1;pos2;upperForce;addTravel2;travel;code;!
```

## Feldverhalten

### Feld 1: Status
- **Typ**: Text
- **Wert**: Immer "DTA" (Test läuft)

### Feld 2: Cycles (Zyklen)
- **Typ**: Zähler
- **Verhalten**: Inkrementiert mit jedem Datensatz ab 1
- **Bereich**: 1 bis ∞

### Feld 3: Position 1 [mm]
- **Typ**: Konstant
- **Wert**: `182` (kodiert für 1.82 mm)
- **Echtwert**: 1.82 mm

### Feld 4: Lower Force [N]
- **Typ**: Zufällig
- **Bereich**: `182` bis `243` (kodiert)
- **Echtwert**: 18.2 N bis 24.3 N
- **Verhalten**: Neuer Zufallswert bei jedem Zyklus

### Feld 5: Additional Travel 1 [mm]
- **Typ**: Dreiecks-Welle mit Rauschen
- **Verhalten**:
  - Start: `0`
  - Erhöhung: +1 alle **10 Zyklen**
  - Maximum: `80` (8.0 mm)
  - Danach: Abnahme auf `0`
  - Zyklus: 0 → 80 → 0 → 80 → ...
- **Rauschen**: ±10% zufällig
- **Periode**: ~1600 Zyklen für kompletten Zyklus (800 hoch, 800 runter)

**Beispiel-Verlauf:**
```
Zyklus   Basiswert  Mit Rauschen
     0 →    0    →   0
    10 →    1    →   0-2
    20 →    2    →   1-3
   ...
   800 →   80    →  72-88
   810 →   79    →  71-87
   ...
  1600 →    0    →   0
```

### Feld 6: Position 2 [mm]
- **Typ**: Berechnet
- **Formel**: `pos1 + travel_initial`
- **Wert**: `182 + 550 = 732` (konstant)
- **Echtwert**: 7.32 mm

### Feld 7: Upper Force [N]
- **Typ**: Zufällig
- **Bereich**: `2100` bis `2300` (kodiert)
- **Echtwert**: 210.0 N bis 230.0 N
- **Verhalten**: Neuer Zufallswert bei jedem Zyklus

### Feld 8: Additional Travel 2 [mm]
- **Typ**: Berechnet
- **Formel**: `(pos1 + travel_current) - (pos1_initial + travel_initial)`
- **Vereinfacht**: `travel_current - travel_initial`
- **Verhalten**: 
  - Start: `0` (da travel = 550)
  - Maximum: ~`150` (wenn travel = 700)
  - Folgt der Dreiecks-Welle von Travel

**Beispiel-Berechnung:**
```
Zyklus 1: (182 + 550) - (182 + 550) = 0
Zyklus 3000: (182 + 700) - (182 + 550) = 150
```

### Feld 9: Travel at Upper Force [mm]
- **Typ**: Dreiecks-Welle mit Rauschen
- **Verhalten**:
  - Start: `550` (5.50 mm)
  - Erhöhung: +1 alle **20 Zyklen**
  - Maximum: `700` (7.00 mm)
  - Danach: Abnahme auf `550`
  - Zyklus: 550 → 700 → 550 → 700 → ...
- **Rauschen**: ±5% zufällig
- **Periode**: ~6000 Zyklen für kompletten Zyklus (3000 hoch, 3000 runter)

**Beispiel-Verlauf:**
```
Zyklus   Basiswert  Mit Rauschen
     0 →   550   →  522-577
    20 →   551   →  523-578
    40 →   552   →  524-579
   ...
  3000 →   700   →  665-735
  3020 →   699   →  664-733
   ...
  6000 →   550   →  522-577
```

### Feld 10: Error Code
- **Typ**: Fehlercode
- **Verhalten**:
  - Normalerweise: `0` (kein Fehler)
  - Alle 100 Zyklen: 50% Chance auf Fehlercode
  - Zufälliger Fehler aus Liste

**Mögliche Fehlercodes:**
| Code | Bedeutung |
|------|-----------|
| 10   | Test failed |
| 11   | Additional Path 1 Violation |
| 12   | Additional Path 2 Violation |
| 13   | Force Limit 2 below limit |
| 14   | Force Limit 2 above limit |
| 101  | Motor Error: Initialization failed |
| 102  | Motor Error: Communication error |
| 103  | Reference Position not set |
| 104  | Motor Error: Not ready |
| 106  | Motor Error: Incorrect initialization |
| 107  | Motor Error: Blocked |
| 201  | Travel too small |
| 202  | Force Search: Target force 1 reached |
| 203  | Force Search: Target force 2 reached |
| 204  | Force Search: Cannot build force 1 |
| 205  | Force Search: Cannot build force 2 |

## LED-Anzeige

- **Pin**: GPIO2 (onboard LED)
- **Frequenz**: 1 Hz (blinkt einmal pro Sekunde)
- **Muster**: 500 ms AN, 500 ms AUS
- **Bedeutung**: Normaler Betrieb

## Beispiel-Ausgabe

### Beim Start:
```
Fatigue Tester Simulator
Waiting 5 seconds before starting transmission...
Starting in 5 seconds...
Starting in 4 seconds...
Starting in 3 seconds...
Starting in 2 seconds...
Starting in 1 seconds...
Starting data transmission now!
Baud rate: 115200
Update interval: 1000 ms
----------------------------------------
### VoiceCoilTestStand V1.5 ID=2BC4D630 ###
For display ceSID-48339C75
Loading... Adr: '1' (0x31). Ok!
CNF;49;0;0;0;0;220;...;!
```

### Dann kontinuierlich:
```
DTA;1;182;215;0;732;2156;0;551;0;!
DTA;2;182;198;0;732;2289;0;550;0;!
DTA;3;182;227;0;732;2134;0;552;0;!
...
DTA;10;182;203;1;732;2245;1;553;0;!
DTA;11;182;219;1;732;2178;1;551;0;!
...
DTA;100;182;241;10;732;2267;3;556;11;!
DTA;101;182;192;10;732;2198;3;557;0;!
...
DTA;800;182;234;80;732;2211;40;590;0;!
...
DTA;3000;182;221;40;732;2176;150;700;0;!
```

## Zeitliche Verläufe

### Additional Travel 1 (Feld 5)
```
   80 ┤     ╱╲     ╱╲
      │    ╱  ╲   ╱  ╲
   40 ┤   ╱    ╲ ╱    ╲
      │  ╱      ╳      ╲
    0 ┼─╯       ╲       ╲─
      0        800      1600    Zyklen
      
Periode: ~1600 Zyklen
Inkrement: Alle 10 Zyklen
Rauschen: ±10%
```

### Travel (Feld 9)
```
  700 ┤        ╱╲       ╱
      │       ╱  ╲     ╱ 
  625 ┤      ╱    ╲   ╱  
      │     ╱      ╲ ╱   
  550 ┼────╯        ╲    
      0          3000    6000   Zyklen
      
Periode: ~6000 Zyklen
Inkrement: Alle 20 Zyklen
Rauschen: ±5%
```

## Anwendungshinweise

### Für Tests:
1. **Kurzer Test** (< 100 Zyklen): Sehen Sie hauptsächlich konstante Werte
2. **Mittlerer Test** (100-1000 Zyklen): Erste Änderungen in Travel erkennbar
3. **Langer Test** (> 1000 Zyklen): Komplette Dreiecks-Wellen sichtbar

### Erwartete Werte:

**Zyklus 1:**
```
DTA;1;182;~200;0;732;~2200;0;~550;0;!
```

**Zyklus 100:**
```
DTA;100;182;~200;10;732;~2200;3;~555;möglicher Fehlercode;!
```

**Zyklus 800:**
```
DTA;800;182;~200;80;732;~2200;40;~590;0;!
```

**Zyklus 3000:**
```
DTA;3000;182;~200;40;732;~2200;150;~700;möglicher Fehlercode;!
```

## Dekodierung

### Position (Felder 3, 6, 8, 9):
```
Rohwert → Realer Wert [mm]
182 → 1.82 mm
732 → 7.32 mm
550 → 5.50 mm
```

### Kraft (Felder 4, 7):
```
Rohwert → Realer Wert [N]
215 → 21.5 N
2156 → 215.6 N
```

## Technische Details

- **Baud Rate**: 115200
- **Update Rate**: 1000 ms (1 Hz)
- **LED Blink Rate**: 1 Hz (1 Blink/Sekunde)
- **Random Seed**: Analog Pin 0

## Typische Anwendungsfälle

1. **Continuous Monitoring**: Aufzeichnung über Stunden/Tage
2. **Trend Analysis**: Beobachtung der Travel-Zunahme über Zeit
3. **Error Detection**: Simulation von Fehlerzuständen alle ~100 Zyklen
4. **Data Validation**: Prüfung der Python-Anwendung mit realistischen Daten

---

**Version**: 2.0  
**Datum**: 05.02.2026  
**Board**: ESP32 NodeMCU-32S
