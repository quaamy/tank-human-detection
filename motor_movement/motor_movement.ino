#include <Arduino.h>

#define IR D8   // IR SENSOR
// Left Motor
#define ENA D7  // PWM pin for speed control (left motor)
#define IN1 D6  // GPIO pin for direction (left motor)
#define IN2 D5  // GPIO pin for direction (left motor)

// Right Motor
#define ENB D4  // PWM pin for speed control (right motor)
#define IN3 D3  // GPIO pin for direction (right motor)
#define IN4 D2  // GPIO pin for direction (right motor)

// WIFI
#include <ESP8266WiFi.h>

// Wi-Fi credentials
const char* ssid = "PLDTHOMEFIBRLtYs4";
const char* password = "aia3562@2015";
WiFiServer server(80);

// Commands
int condition = 0;

// Setting minimum duty cycle
int dutyCycle = 60;

int irReading;

#define TRIG D1
#define ECHO D0

//define sound speed in cm/uS
#define SOUND_SPEED 0.034
#define CM_TO_INCH 0.393701

long duration;
float distanceCm;

void setup() {

  Serial.begin(115200);

  pinMode(IR, INPUT);
  // Start Wi-Fi connection
  WiFi.begin(ssid, password);
  Serial.println("Connecting to Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Start the server
  server.begin();

  // Set the pins as outputs
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);

  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);

  pinMode(TRIG, OUTPUT);  // Sets the TRIG as an Output
  pinMode(ECHO, INPUT);   // Sets the ECHO as an Input

  // Testing message
  Serial.println("Testing DC Motors...");
}

void loop() {
  // Commands Output
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");
    String request = client.readStringUntil('\r');
    Serial.println("Request: " + request);

    // Control motor based on received request
    if (request.indexOf("/FORWARD") != -1) {
      forward();
    } else if (request.indexOf("/BACKWARD") != -1) {
      backward();
    } else if (request.indexOf("/STOP") != -1) {
      stop();
    } else if (request.indexOf("/RIGHT") != -1) {
      right();
    } else if (request.indexOf("/LEFT") != -1) {
      left();
    } else if (request.indexOf("/BACKLEFT") != -1) {
      backleft();
    } else if (request.indexOf("/BACKRIGHT") != -1) {
      backright();
    }

    // Send response to the client
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/html");
    client.println("");
    client.println("<!DOCTYPE HTML>");
    client.println("<html>");
    client.println("<h1>ESP8266 Motor Control</h1>");
    client.println("<p><a href=\"/FORWARD\">Forward</a></p>");
    client.println("<p><a href=\"/BACKWARD\">Backward</a></p>");
    client.println("<p><a href=\"/RIGHT\">Right</a></p>");
    client.println("<p><a href=\"/LEFT\">Left</a></p>");
    client.println("<p><a href=\"/BACKLEFT\">Backleft</a></p>");
    client.println("<p><a href=\"/BACKRIGHT\">Backright</a></p>");
    client.println("<p><a href=\"/STOP\">Stop</a></p>");
    client.println("</html>");
    client.stop();
    Serial.println("Client disconnected");
  }

  irReading = digitalRead(IR);
    if (irReading == LOW) {
      Serial.println("READING IS HIGH!!");
      Serial.print("READING IS HIGH!!");
    } else {
      Serial.println("READING IS LOW!!");
      Serial.print("READING IS LOW!!");
    }

  // Clears the TRIG
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  // Sets the TRIG on HIGH state for 10 micro seconds
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  // Reads the ECHO, returns the sound wave travel time in microseconds
  duration = pulseIn(ECHO, HIGH);

  // Calculate the distance
  distanceCm = duration * SOUND_SPEED / 2;

  // Prints the distance in the Serial Monitor
  Serial.print("Distance (cm): ");
  Serial.println(distanceCm);

  delay(1000);
}

void forward() {
  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  // Move the motors forward at maximum speed
  Serial.println("Forward");
  digitalWrite(IN1, LOW);  // Left motor forward
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, LOW);  // Right motor forward
  digitalWrite(IN4, HIGH);
}

void backward() {
  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  Serial.println("Moving Backward");
  digitalWrite(IN1, HIGH);  // Left motor backward
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);  // Right motor backward
  digitalWrite(IN4, LOW);
}

void stop() {
  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  Serial.println("Motors Stopped");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void right() {
  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  Serial.println("Going Right");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void left() {
  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  Serial.println("Going Left");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void backleft() {
  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  Serial.println("Going Left");
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void backright() {
  analogWrite(ENA, 255);
  analogWrite(ENB, 255);

  Serial.println("Going Right");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}
