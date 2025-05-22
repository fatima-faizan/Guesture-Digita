# Gesture Digita - Hardware Implementation Guide

This document provides detailed instructions for assembling the hardware components of the Gesture Digita system, including wiring diagrams, connection details, and system workflow.

## Hardware Components

| Component | Specification | Quantity |
|-----------|---------------|----------|
| Arduino Nano | ATmega328P, 16MHz | 1 |
| Flex Sensors | 4.5", 10kΩ-110kΩ range | 3 |
| Bluetooth Module | HC-05 (or HC-06) | 1 |
| Resistors | 10kΩ | 3 |
| Jumper Wires | Male-to-male, male-to-female | Assorted |
| Battery (optional) | 9V with adapter | 1 |
| Breadboard | Mini breadboard | 1 |
| Glove or finger straps | Fabric, elastic | As needed |

## System Architecture

```
┌─────────────────┐     ┌───────────────┐     ┌────────────────┐     ┌───────────────┐
│                 │     │               │     │                │     │               │
│  Flex Sensors   ├────►│  Arduino Nano ├────►│ Bluetooth      ├────►│  Computer     │
│  (3x)           │     │               │     │ Module (HC-05) │     │  Software     │
│                 │     │               │     │                │     │               │
└─────────────────┘     └───────────────┘     └────────────────┘     └───────────────┘
```

## Wiring Diagram

### Flex Sensors to Arduino

Each flex sensor is connected in a voltage divider configuration:

```
5V (Arduino) ──────┬─────── Flex Sensor ───────┬────── Analog Pin (A0/A1/A2)
                   │                           │
                   │                           │
                  GND                         10kΩ Resistor
                                               │
                                               │
                                              GND
```

Detailed connections:
- **Flex Sensor 1**:
  - One end to 5V
  - Other end to junction of 10kΩ resistor and A0
  - 10kΩ resistor to GND

- **Flex Sensor 2**:
  - One end to 5V
  - Other end to junction of 10kΩ resistor and A1
  - 10kΩ resistor to GND

- **Flex Sensor 3**:
  - One end to 5V
  - Other end to junction of 10kΩ resistor and A2
  - 10kΩ resistor to GND

### Bluetooth Module to Arduino

```
                  ┌───────────────┐                     ┌────────────┐
                  │ Arduino Nano  │                     │   HC-05    │
                  │               │                     │            │
  USB/Power ─────►│ Vin           │                     │            │
                  │ GND ──────────┼─────────────────────► GND        │
                  │ 5V ───────────┼─────────────────────► VCC        │
                  │ TX (D1) ──────┼─────────────────────► RX         │
                  │ RX (D0) ──────┼─────────────────────► TX         │
                  │               │                     │            │
                  └───────────────┘                     └────────────┘
```

Detailed connections:
- **Bluetooth Module HC-05**:
  - VCC to Arduino 5V
  - GND to Arduino GND
  - RX to Arduino TX (pin D1)
  - TX to Arduino RX (pin D0)
  - STATE pin not connected (optional)
  - EN pin not connected (optional)

## Physical Assembly

### Flex Sensor Placement

![Flex Sensor Placement Diagram]

The flex sensors should be attached to the fingers (typically index, middle, and ring fingers) using one of these methods:

1. **Glove Method**:
   - Sew small fabric channels on a lightweight glove
   - Insert flex sensors into these channels
   - Route wires through the wrist area
   - Secure wires with fabric tape or stitching

2. **Finger Strap Method**:
   - Create elastic finger loops for each sensor
   - Attach flex sensors to the dorsal (top) side of fingers
   - Secure with medical/athletic tape
   - Group wires with cable ties for strain relief

### Arduino and Bluetooth Placement

1. **Wrist Mount Option**:
   - Create a fabric wristband or use a sports wristband
   - Attach mini breadboard to the wristband
   - Secure Arduino and Bluetooth module to the breadboard
   - Route sensor wires neatly to the breadboard
   - Power with small LiPo battery for portable use

2. **Stationary Option**:
   - Place Arduino and breadboard on desk
   - Connect sensors with longer wires
   - Power via USB from computer

## Power Options

1. **USB Power**:
   - Connect Arduino Nano to computer via USB cable
   - Provides power and optional serial communication backup

2. **Battery Power (Portable)**:
   - 9V battery with appropriate connector to Vin and GND
   - 7.4V LiPo battery (with JST connector)
   - Battery pack with 5V USB output

## Assembly Instructions

1. **Prepare the Flex Sensors**:
   - Cut heat shrink tubing to protect solder joints
   - Solder extension wires to flex sensor terminals if needed
   - Test each sensor with a multimeter to verify changing resistance when bent

2. **Setup Breadboard**:
   - Create voltage divider circuits for each flex sensor
   - Connect power rails (5V and GND)
   - Place 10kΩ resistors for each sensor circuit

3. **Connect Arduino**:
   - Place Arduino Nano on breadboard
   - Connect analog pins A0, A1, A2 to respective flex sensor circuits
   - Connect 5V and GND to power rails

4. **Connect Bluetooth Module**:
   - Place HC-05 on breadboard
   - Connect TX, RX, VCC, and GND to corresponding Arduino pins
   - Ensure baud rate is set correctly (usually 9600 by default)

5. **Secure Components**:
   - Use double-sided tape or mounting putty to secure components
   - Apply hot glue to stress points for strain relief
   - Consider a small enclosure for the electronics

6. **Test Connectivity**:
   - Upload test sketch to Arduino (available in firmware folder)
   - Use serial monitor or Bluetooth terminal app to verify sensor readings
   - Adjust sensor placement if readings are inconsistent

## Arduino Firmware

The Arduino firmware performs these essential functions:

1. **Sensor Reading**: Reads analog values from the three flex sensors
2. **Data Processing**: Normalizes and filters the raw sensor values
3. **Data Formatting**: Packages the data into a structured format
4. **Bluetooth Transmission**: Sends the data to the computer via Bluetooth

The firmware is designed to transmit data at 50Hz (20ms intervals) to provide a balance between responsiveness and power consumption.

```arduino
// Basic structure of the Arduino code
void setup() {
  Serial.begin(9600);  // Bluetooth module baud rate
}

void loop() {
  // Read sensors
  int sensor1 = analogRead(A0);
  int sensor2 = analogRead(A1);
  int sensor3 = analogRead(A2);
  
  // Format data
  String dataPacket = String(sensor1) + "," + String(sensor2) + "," + String(sensor3);
  
  // Send via Bluetooth (Serial)
  Serial.println(dataPacket);
  
  // 20ms delay for ~50Hz sampling rate
  delay(20);
}
```

## System Workflow

1. **Data Acquisition**:
   - Flex sensors change resistance when bent
   - Voltage divider circuits convert resistance to voltage
   - Arduino reads voltage as analog values (0-1023)

2. **Data Transmission**:
   - Arduino formats sensor values into comma-separated string
   - Data transmitted via Bluetooth at 50Hz
   - Format: "sensor1,sensor2,sensor3\n"

3. **Computer Processing**:
   - Gesture Digita software connects to Bluetooth device
   - Serial data is parsed and converted to finger position values
   - ML model interprets finger positions as gestures
   - Corresponding actions are performed in the presentation

## Calibration

For optimal performance, the system should be calibrated for each user:

1. Run the calibration routine in the Gesture Digita software
2. Follow prompts to bend each finger to minimum and maximum positions
3. System stores calibration data for gesture recognition
4. Recalibrate when changing users or if gesture recognition degrades

## Troubleshooting Hardware Issues

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| No sensor readings | Loose connections | Check all wiring connections |
| | Incorrect pin assignments | Verify Arduino pin connections |
| | Damaged sensor | Test sensor with multimeter, replace if needed |
| Erratic readings | Interference | Move away from electronic devices |
| | Poor connections | Resolder connections, secure wires |
| | Power fluctuations | Use stable power source |
| Bluetooth not connecting | Pairing issues | Re-pair device, check COM port |
| | Incorrect baud rate | Ensure matching baud rates (9600) |
| | Power issues | Check Bluetooth module power connections |
| Limited sensor range | Improper voltage divider | Adjust resistor values |
| | Sensor placement | Reposition sensors on fingers |

## Power Consumption

The system's power requirements are relatively modest:
- Arduino Nano: ~20mA
- Bluetooth module: ~30-40mA
- Total system: ~50-70mA

With a typical 9V battery (500mAh), the system will operate for approximately 7-8 hours. Using a 2000mAh power bank would extend operation to 25+ hours.

## Future Hardware Expansions

The current 3-sensor design can be expanded for enhanced functionality:
- Add gyroscope/accelerometer (MPU-6050) for spatial tracking
- Integrate additional flex sensors (up to 5 total, one per finger)
- Add vibration motor for haptic feedback
- Incorporate RGB LED for status indication
- Upgrade to Arduino Nano 33 BLE for integrated Bluetooth and improved processing

## Maintenance

- Clean contacts periodically with isopropyl alcohol
- Check for wire fatigue, especially at flex points
- Replace sensors if resistance range diminishes over time
- Update firmware as new versions become available
- Recharge or replace batteries as needed

This hardware implementation guide should provide all the necessary information to build and maintain the Gesture Digita hardware system.
