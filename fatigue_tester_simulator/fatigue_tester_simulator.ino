/*
 * Fatigue Tester Simulator for ESP32 NodeMCU-32S
 * 
 * Simulates a fatigue testing machine by sending serial data
 * in the format: DTA;cycles;pos1;lowerForce;addTravel1;pos2;upperForce;addTravel2;travel;code;!
 * 
 * Board: ESP32 NodeMCU-32S
 * Connection: USB/Serial at 115200 baud
 * Update rate: 1000 ms (1 Hz)
 */

// Pin definitions
const int LED_PIN = 2; // Built-in LED on NodeMCU-32S

// Simulation parameters
const unsigned long UPDATE_INTERVAL = 1000; // ms (1 Hz)
const unsigned long LED_INTERVAL = 500;     // ms (1 Hz blinking = 500ms on/off)

// Fixed and initial values
const int POS1_FIXED = 182;              // Field 3: constant position 1 in [mm*100]
const int TRAVEL_INITIAL = 550;          // Field 9: initial travel [mm*100]
const int TRAVEL_MAX = 700;              // Field 9: max travel [mm*100]
const int TRAVEL_MIN = 550;              // Field 9: min travel [mm*100]

// Lower Force (Field 4) - random between 182 and 243 (*10)
const int LOWER_FORCE_MIN = 182;         // 18.2 N
const int LOWER_FORCE_MAX = 243;         // 24.3 N

// Upper Force (Field 7) - random between 2100 and 2300 (*10)
const int UPPER_FORCE_MIN = 2100;        // 210.0 N
const int UPPER_FORCE_MAX = 2300;        // 230.0 N

// Additional Travel 1 (Field 5) - triangular wave with 10% noise
const int ADD_TRAVEL1_MAX = 80;          // Max value
const int ADD_TRAVEL1_CYCLES_PER_INC = 10; // Increment every 10 cycles
const float ADD_TRAVEL1_NOISE = 0.10;    // 10% noise

// Travel (Field 9) - triangular wave with 5% noise
const int TRAVEL_CYCLES_PER_INC = 20;    // Increment every 20 cycles
const float TRAVEL_NOISE = 0.05;         // 5% noise

// Error codes that can occur (Field 10)
const int ERROR_CODES[] = {10, 11, 12, 13, 14, 101, 102, 103, 104, 106, 107, 201, 202, 203, 204, 205};
const int ERROR_CODE_COUNT = 16;
const int ERROR_PROBABILITY_CYCLES = 100; // Every 100 cycles, chance for error

// State variables
unsigned long lastUpdate = 0;
unsigned long lastLedToggle = 0;
unsigned long cycleCount = 0;
bool ledState = false;
bool headerSent = false;

// Simulation state
int currentAddTravel1 = 0;
bool addTravel1Increasing = true;
int addTravel1BaseValue = 0;

int currentTravel = TRAVEL_INITIAL;
bool travelIncreasing = true;
int travelBaseValue = TRAVEL_INITIAL;

// Initial values for calculations
const int initialPos1 = POS1_FIXED;
const int initialTravel = TRAVEL_INITIAL;

void setup() {
  // Initialize LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Initialize serial communication at 115200 baud
  Serial.begin(115200);
  
  // Wait for serial port to connect
  while (!Serial) {
    delay(10);
  }
  
  Serial.println("Fatigue Tester Simulator");
  Serial.println("Waiting 5 seconds before starting transmission...");
  
  // Wait 5 seconds after power-on before starting data transmission
  for (int i = 5; i > 0; i--) {
    Serial.print("Starting in ");
    Serial.print(i);
    Serial.println(" seconds...");
    delay(1000);
  }
  
  Serial.println("Starting data transmission now!");
  Serial.println("Baud rate: 115200");
  Serial.println("Update interval: 1000 ms");
  Serial.println("----------------------------------------");
  
  // Seed random number generator
  randomSeed(analogRead(0));
}

void loop() {
  unsigned long currentTime = millis();
  
  // Handle LED blinking (1 Hz = 500ms on, 500ms off)
  if (currentTime - lastLedToggle >= LED_INTERVAL) {
    lastLedToggle = currentTime;
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState ? HIGH : LOW);
  }
  
  // Check if it's time to send data
  if (currentTime - lastUpdate >= UPDATE_INTERVAL) {
    lastUpdate = currentTime;
    
    // Send header only once at the start
    if (!headerSent) {
      sendHeader();
      headerSent = true;
      return; // Wait for next cycle to start sending data
    }
    
    // Increment cycle count
    cycleCount++;
    
    // Update simulation values
    updateSimulation();
    
    // Generate and send data
    sendData();
  }
}

void sendHeader() {
  /**
   * Send the system header once at startup
   */
  Serial.println("### VoiceCoilTestStand V1.5 ID=2BC4D630 ###");
  Serial.println("For display ceSID-48339C75");
  Serial.println("Loading... Adr: '1' (0x31). Ok!");
  Serial.println("CNF;49;0;0;0;0;220;0;152;8;152;8;44;1;44;1;184;11;20;0;32;78;10;0;10;1;0;0;0;63;66;15;0;0;0;0;0;16;39;0;0;255;3;0;0;0;0;0;0;0;0;0;0;0;0;0;0;255;3;0;0;16;39;0;0;0;0;0;0;15;39;0;0;83;7;0;0;166;14;0;0;0;0;0;0;0;0;0;0;0;0;0;0;96;234;0;0;48;117;0;0;0;0;0;0;48;117;0;0;1;0;0;0;2;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;32;78;0;0;16;39;0;0;0;0;0;0;16;39;0;0;255;3;0;0;16;39;0;0;0;0;0;0;0;0;0;0;0;0;0;0;16;39;0;0;255;3;0;0;0;0;0;0;255;3;0;0;2;0;0;0;1;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;48;117;0;0;96;234;0;0;0;0;0;0;96;234;0;0;2;0;0;0;1;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;16;39;0;0;32;78;0;0;0;0;0;0;32;78;0;0;!");
}

void updateSimulation() {
  /**
   * Update all simulation values based on cycle count
   */
  
  // Update Additional Travel 1 (Field 5) - triangular wave
  // Increment every 10 cycles
  if (cycleCount % ADD_TRAVEL1_CYCLES_PER_INC == 0) {
    if (addTravel1Increasing) {
      addTravel1BaseValue++;
      if (addTravel1BaseValue >= ADD_TRAVEL1_MAX) {
        addTravel1BaseValue = ADD_TRAVEL1_MAX;
        addTravel1Increasing = false;
      }
    } else {
      addTravel1BaseValue--;
      if (addTravel1BaseValue <= 0) {
        addTravel1BaseValue = 0;
        addTravel1Increasing = true;
      }
    }
  }
  
  // Apply 10% noise to Additional Travel 1
  float noise1 = (random(-100, 101) / 1000.0) * ADD_TRAVEL1_NOISE;
  currentAddTravel1 = addTravel1BaseValue * (1.0 + noise1);
  if (currentAddTravel1 < 0) currentAddTravel1 = 0;
  
  // Update Travel (Field 9) - triangular wave
  // Increment every 20 cycles
  if (cycleCount % TRAVEL_CYCLES_PER_INC == 0) {
    if (travelIncreasing) {
      travelBaseValue++;
      if (travelBaseValue >= TRAVEL_MAX) {
        travelBaseValue = TRAVEL_MAX;
        travelIncreasing = false;
      }
    } else {
      travelBaseValue--;
      if (travelBaseValue <= TRAVEL_MIN) {
        travelBaseValue = TRAVEL_MIN;
        travelIncreasing = true;
      }
    }
  }
  
  // Apply 5% noise to Travel
  float noise2 = (random(-100, 101) / 1000.0) * TRAVEL_NOISE;
  currentTravel = travelBaseValue * (1.0 + noise2);
  if (currentTravel < TRAVEL_MIN) currentTravel = TRAVEL_MIN;
  if (currentTravel > TRAVEL_MAX) currentTravel = TRAVEL_MAX;
}

void sendData() {
  /**
   * Generate and send data packet in the format:
   * DTA;cycles;pos1;lowerForce;addTravel1;pos2;upperForce;addTravel2;travel;code;!
   */
  
  // Field 1: Status (always DTA for running)
  String status = "DTA";
  
  // Field 2: Cycle count
  unsigned long cycles = cycleCount;
  
  // Field 3: Position 1 - constant 182 (1.82 mm)
  int pos1 = POS1_FIXED;
  
  // Field 4: Lower Force - random between 182 and 243 (18.2 to 24.3 N)
  int lowerForce = random(LOWER_FORCE_MIN, LOWER_FORCE_MAX + 1);
  
  // Field 5: Additional Travel 1 - calculated with triangular wave + noise
  int addTravel1 = currentAddTravel1;
  
  // Field 6: Position 2 - calculated from pos1 + initial travel
  // pos2 = 3. + (9. at the start of the program)
  int pos2 = initialPos1 + initialTravel;
  
  // Field 7: Upper Force - random between 2100 and 2300 (210.0 to 230.0 N)
  int upperForce = random(UPPER_FORCE_MIN, UPPER_FORCE_MAX + 1);
  
  // Field 8: Additional Travel 2 - calculated from position changes
  // addTravel2 = (3. + 9.) - (3. + 9. at the start of the program)
  int addTravel2 = (pos1 + currentTravel) - (initialPos1 + initialTravel);
  
  // Field 9: Travel - calculated with triangular wave + noise
  int travel = currentTravel;
  
  // Field 10: Error code - 0 normally, random error every ~100 cycles
  int errorCode = 0;
  if (cycleCount % ERROR_PROBABILITY_CYCLES == 0 && random(0, 2) == 1) {
    // Randomly select an error code
    errorCode = ERROR_CODES[random(0, ERROR_CODE_COUNT)];
  }
  
  // Build and send the data string
  Serial.print(status);
  Serial.print(";");
  Serial.print(cycles);
  Serial.print(";");
  Serial.print(pos1);
  Serial.print(";");
  Serial.print(lowerForce);
  Serial.print(";");
  Serial.print(addTravel1);
  Serial.print(";");
  Serial.print(pos2);
  Serial.print(";");
  Serial.print(upperForce);
  Serial.print(";");
  Serial.print(addTravel2);
  Serial.print(";");
  Serial.print(travel);
  Serial.print(";");
  Serial.print(errorCode);
  Serial.println(";!");
}
