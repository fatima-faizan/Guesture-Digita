# Flex Sensor Gesture Recognition System

## Project Overview

This project implements a gesture recognition system using flex sensors connected to an Arduino Nano. The system captures hand movements through flex sensors, processes this data, and transmits it via Bluetooth to a computer for gesture recognition and interpretation. The system can be used for applications such as sign language recognition, gesture-based control systems, or interactive interfaces.

## Hardware Components

### Required Hardware
1. **3× Flex Sensors**
   - Resistance range: Typically 10kΩ-110kΩ
   - Recommended model: SEN-10264 or equivalent
   - Purpose: Captures finger bending movements

2. **Arduino Nano**
   - Microcontroller: ATmega328P
   - Operating voltage: 5V
   - Input voltage: 7-12V
   - Digital I/O pins: 14 (of which 6 provide PWM output)
   - Analog input pins: 8
   - Purpose: Processes sensor data and controls Bluetooth communication

3. **Bluetooth Module**
   - Recommended model: HC-05 or HC-06
   - Operating voltage: 3.3V-5V
   - Communication: Serial communication (UART)
   - Purpose: Transmits sensor data wirelessly to the computer

4. **Additional Components**
   - Resistors (10kΩ) for voltage divider circuits
   - Breadboard and jumper wires
   - Power supply (battery or USB connection)
   - Glove or strap for mounting sensors

### Hardware Specifications
For optimal performance, the following specifications are recommended:
- Arduino Nano with 16MHz clock speed
- Bluetooth module with at least 9600 baud rate
- Flex sensors with good sensitivity range
- Low-latency connection (<50ms)

## Hardware Setup

### Wiring Diagram
1. **Flex Sensors**:
   - Connect one end of each flex sensor to 5V
   - Connect the other end to a 10kΩ resistor that goes to ground
   - Connect the junction between the flex sensor and resistor to analog pins A0, A1, and A2 on the Arduino

2. **Bluetooth Module**:
   - VCC to 5V on Arduino
   - GND to GND on Arduino
   - TXD to RXD (pin 0) on Arduino
   - RXD to TXD (pin 1) on Arduino

### Sensor Placement
- Place flex sensors along fingers (typically index, middle, and ring fingers)
- Secure with tape or integrate into a glove design
- Ensure consistent placement for reliable readings

## Software Architecture

### Overview
The system software consists of three main components:
1. Arduino firmware for sensor reading and Bluetooth transmission
2. Computer-side Bluetooth receiver script
3. Gesture recognition processing using OpenCV and custom drawing helpers

### Arduino Firmware
The Arduino firmware performs the following functions:
- Reads analog values from the flex sensors
- Calibrates sensor readings
- Formats data for transmission
- Sends data packets via Bluetooth

### Computer-Side Processing
The computer-side software:
- Establishes Bluetooth connection
- Processes incoming sensor data
- Uses drawing helper utilities for visualization
- Applies gesture recognition algorithms
- Executes corresponding actions based on recognized gestures

### Drawing Helper Class
The `DrawingHelper` class (from `drawing_helper.py`) enables:
- Real-time visualization of sensor data
- Creation and management of annotation points
- Visual feedback of recognized gestures
- Utility functions for drawing and managing annotations

```python
class DrawingHelper:
    # Initializes annotation trackers
    def __init__(self):
        # ...existing code...
    
    # Records points when annotation is active
    def start_annotation(self, point):
        # ...existing code...
    
    # Ends the current annotation sequence
    def stop_annotation(self):
        # ...existing code...
    
    # Removes the last annotation drawn
    def undo_last_annotation(self):
        # ...existing code...
    
    # Resets all annotations
    def clear_annotations(self):
        # ...existing code...
    
    # Renders all annotations on an image
    def draw_annotations(self, img, color=(0, 0, 200), thickness=12):
        # ...existing code...
```

## Implementation Details

### Gesture Recognition Process
1. **Data Acquisition**:
   - Flex sensors generate resistance changes based on bending
   - Arduino converts these to digital values via analog inputs
   - Values are normalized and transmitted via Bluetooth

2. **Data Processing**:
   - Computer receives serialized sensor data
   - Data is parsed and structured for the recognition model
   - Drawing helper visualizes the incoming data points

3. **Gesture Recognition**:
   - Pattern matching algorithms compare input with known gesture patterns
   - Machine learning model (if implemented) classifies gestures
   - Confidence scores determine the recognized gesture

4. **Action Execution**:
   - Recognized gestures trigger predefined actions
   - Feedback is provided through the visualization system

### Data Flow
```
Flex Sensors → Arduino Nano → Bluetooth Module → Computer
→ Data Processing → Gesture Recognition → Action Execution
```

## Performance Considerations

### Hardware Recommendations
For optimal performance:
- Arduino Nano or Arduino Nano 33 IoT for better processing capabilities
- High-quality flex sensors with consistent resistance curves
- Class 1 Bluetooth module for extended range if needed
- Consider using a LiPo battery for portable applications

### Performance Optimizations
- Sampling rate: 50-100Hz is typically sufficient for gesture recognition
- Bluetooth baud rate: 9600-115200 depending on data requirements
- Buffer size: Adjust based on gesture complexity and sampling rate
- Filtering: Apply simple moving average or Kalman filter for noise reduction

## Future Improvements

### Hardware Enhancements
- Add additional flex sensors for more complex gesture recognition
- Integrate IMU (accelerometer/gyroscope) for spatial tracking
- Implement wireless charging for convenience
- Explore custom PCB design for size reduction

### Software Enhancements
- Implement machine learning-based gesture recognition
- Add user-defined gesture training capability
- Improve visualization with 3D hand model
- Develop mobile app companion for configuration

## Troubleshooting

### Common Issues
1. **Inconsistent Readings**
   - Check sensor connections and resistance values
   - Verify power supply stability
   - Calibrate sensors regularly

2. **Bluetooth Connection Problems**
   - Check pairing settings
   - Verify baud rate matches on both ends
   - Reduce interference from other devices

3. **Gesture Recognition Failures**
   - Retrain or recalibrate the system
   - Ensure consistent sensor placement
   - Adjust recognition thresholds

## Conclusion
This flex sensor gesture recognition system provides a versatile platform for interpreting hand gestures through flex sensor data. With the Arduino Nano handling sensor input and Bluetooth communication, and the computer processing the data using OpenCV and custom utilities, the system offers a complete pipeline from physical movement to digital interpretation and action.