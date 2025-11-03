
// Pin definitions
const int BUTTON1_PIN = 2;  // Player 1 button
const int BUTTON2_PIN = 3;  // Player 2 button

// Button state variables
int button1State = 0;
int button2State = 0;
int lastButton1State = 0;
int lastButton2State = 0;

// Debounce variables
unsigned long lastDebounceTime1 = 0;
unsigned long lastDebounceTime2 = 0;
unsigned long debounceDelay = 50;  // 50ms debounce time

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Configure button pins as inputs with internal pull-up resistors
  pinMode(BUTTON1_PIN, INPUT_PULLUP);
  pinMode(BUTTON2_PIN, INPUT_PULLUP);
  
  // Wait for serial connection to establish
  delay(1000);
  Serial.println("Arduino Button Controller Ready");
  Serial.println("Button 1: Pin 2 (Player 1 - Yellow)");
  Serial.println("Button 2: Pin 3 (Player 2 - Orange)");
}

void loop() {
  // Read button states (inverted because of INPUT_PULLUP)
  // When button is pressed, pin reads LOW (0)
  // When button is released, pin reads HIGH (1)
  int reading1 = !digitalRead(BUTTON1_PIN);  // Invert so 1 = pressed
  int reading2 = !digitalRead(BUTTON2_PIN);  // Invert so 1 = pressed
  
  // Debounce Button 1
  if (reading1 != lastButton1State) {
    lastDebounceTime1 = millis();
  }
  
  if ((millis() - lastDebounceTime1) > debounceDelay) {
    if (reading1 != button1State) {
      button1State = reading1;
    }
  }
  
  // Debounce Button 2
  if (reading2 != lastButton2State) {
    lastDebounceTime2 = millis();
  }
  
  if ((millis() - lastDebounceTime2) > debounceDelay) {
    if (reading2 != button2State) {
      button2State = reading2;
    }
  }
  
  // Send button states over serial
  Serial.print("Button 1: ");
  Serial.println(button1State);
  Serial.print("Button 2: ");
  Serial.println(button2State);
  
  // Update last states
  lastButton1State = reading1;
  lastButton2State = reading2;
  
  // Small delay for stability
  delay(50);
}