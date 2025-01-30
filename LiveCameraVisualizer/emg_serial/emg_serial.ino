void setup() 
{
  Serial.begin(115200);
}

void loop() {
    int emgValue = analogRead(A0);  // Read from A0
    Serial.println(emgValue);  // Send value to Python
    delay(100);  // Increase delay (50-100ms is stable)
}
