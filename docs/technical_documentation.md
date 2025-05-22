# Gesture Digita - Technical Documentation

## System Architecture

### Hardware Components
1. **Input Sensors**
   - 3x Flex Sensors (4.5" bend sensors)
   - Operating voltage: 3.3V-5V
   - Resistance range: ~10KΩ to ~250KΩ
   - Bend angle: 0° to 90°

2. **Microcontroller**
   - Arduino Nano
   - ATmega328P processor
   - Operating voltage: 5V
   - Clock speed: 16 MHz
   - Digital I/O pins: 14
   - Analog input pins: 8

3. **Bluetooth Module**
   - HC-05 Bluetooth Module
   - Operating voltage: 3.3V-6V
   - Baud rate: 9600 bps default
   - Range: ~10 meters
   - Bluetooth version: 2.0+EDR

### Software Components
1. **Gesture Recognition System**
   - MediaPipe Hands library (v0.9.0+)
   - OpenCV (v4.5.5+)
   - Custom ML model using RandomForestClassifier

2. **Presentation Control**
   - PowerPoint COM automation
   - Win32com client interface
   - Custom slide conversion utilities

3. **User Interface**
   - PyQt5 framework (v5.15.6+)
   - Real-time video processing
   - Gesture visualization

## Hardware Implementation

### Flex Sensor Circuit
```
[Flex Sensor] -- [10kΩ Resistor] -- [GND]
      |
   [Arduino Analog Pin]
```

### Arduino Nano Connections
1. Flex Sensor 1: A0
2. Flex Sensor 2: A1
3. Flex Sensor 3: A2
4. HC-05 TX: D10
5. HC-05 RX: D11
6. HC-05 VCC: 5V
7. HC-05 GND: GND

### Bluetooth Communication Protocol
```
Data Format: "F1:value,F2:value,F3:value"
Baud Rate: 9600
Update Frequency: 50Hz
```

## Software Implementation

### Gesture Detection Pipeline
1. Hardware sensor data acquisition
2. Bluetooth data parsing
3. Gesture classification using ML model
4. Action mapping and execution

### ML Model Architecture
- Algorithm: Random Forest Classifier
- Features: 63 normalized coordinates (21 landmarks × 3 coordinates)
- Classes: 6 gesture types
- Training samples: 700 for traning per gesture
- Model accuracy: ~95% on test set

## Core System Workflow

### Presentation Processing Pipeline
1. **File Input Handler**
   ```python
   # Supported formats
   SUPPORTED_FORMATS = {
       'PowerPoint': ['.ppt', '.pptx'],
       'PDF': ['.pdf']
   }
   ```

2. **Conversion Process**
   - PowerPoint:
     - Uses win32com.client for COM automation
     - Exports slides as 1280x720 PNG images
     - Preserves text for ML analysis
     - Handles embedded media
   
   - PDF:
     - Uses pdf2image for conversion
     - DPI: 200 for optimal quality
     - Anti-aliasing enabled
     - Color preservation

3. **Slide Analysis**
   - Complexity scoring:
     - Text density (0.0-0.5)
     - Edge density (0.0-0.5)
     - Combined score determines gesture sensitivity
   - Caching system:
     - In-memory cache for recent slides
     - Disk cache for large presentations
     - LRU eviction policy

### Gesture Recognition System

1. **Hand Detection**
   ```python
   # Landmark structure
   HAND_LANDMARKS = {
       'WRIST': 0,
       'THUMB_CMC': 1,
       'THUMB_TIP': 4,
       'INDEX_TIP': 8,
       'MIDDLE_TIP': 12,
       'RING_TIP': 16,
       'PINKY_TIP': 20
   }
   ```

2. **Gesture Classification**
   - Preprocessing:
     - Normalize coordinates (0.0-1.0)
     - Calculate finger angles
     - Apply temporal smoothing (0.1 factor)
   
   - Recognition thresholds:
     ```python
     THRESHOLDS = {
         'confidence': 0.3,  # Base confidence
         'temporal': 0.4,    # Historical weight
         'angle': 160        # Finger extension
     }
     ```

3. **Drawing System**
   - Vector format:
     ```python
     Annotation = {
         'points': [(x, y), ...],
         'color': (R, G, B),
         'thickness': int,
         'timestamp': float
     }
     ```
   
   - Performance:
     - Point smoothing
     - Path optimization
     - Render batching

### Memory Management

1. **Slide Storage**
   - Maximum cached slides: 10
   - Image format: PNG (compressed)
   - Resolution: 1280x720
   - Color depth: 24-bit

2. **Resource Cleanup**
   - Automatic temp file deletion
   - COM object release
   - Memory threshold monitoring
   - Background cleanup thread

### Performance Metrics

1. **Real-world Performance**
   - Slide load time: <100ms
   - Gesture latency: <50ms
   - Drawing latency: <16ms
   - Memory usage: ~200MB base

2. **Optimization Techniques**
   - Frame skipping under load
   - Adaptive quality scaling
   - Background processing
   - Resource pooling

### System Requirements

#### Minimum Hardware to run the driver
- Processor: Intel Core i3 +
- RAM: 4GB
- Camera: 720p webcam
- Bluetooth: Version 2.0+
- Storage: 1GB free space


### Performance Metrics
1. Gesture Recognition
   - Latency: <100ms
   - Accuracy: >90%
   - False positive rate: <5%

2. Bluetooth Communication
   - Latency: <50ms
   - Range: Up to 10m
   - Data rate: 9600 bps

## Integration Guide

### Arduino Code Structure
```cpp
void setup() {
    Serial.begin(9600);  // Bluetooth communication
    pinMode(A0, INPUT);  // Flex sensor 1
    pinMode(A1, INPUT);  // Flex sensor 2
    pinMode(A2, INPUT);  // Flex sensor 3
}

void loop() {
    // Read sensor values
    int flex1 = analogRead(A0);
    int flex2 = analogRead(A1);
    int flex3 = analogRead(A2);

    // Format and send data
    String data = "F1:" + String(flex1) + 
                 ",F2:" + String(flex2) + 
                 ",F3:" + String(flex3);
    Serial.println(data);
    delay(20);  // 50Hz update rate
}
```

### Python Integration
```python
import serial

def init_bluetooth():
    return serial.Serial(
        port='COM4',  # Update based on system
        baudrate=9600,
        timeout=1
    )

def parse_sensor_data(data):
    # Parse "F1:value,F2:value,F3:value"
    values = {}
    pairs = data.split(',')
    for pair in pairs:
        sensor, value = pair.split(':')
        values[sensor] = int(value)
    return values
```

## Troubleshooting Guide

### Hardware Issues
1. Flex Sensor Calibration
   - Check voltage divider circuit
   - Verify analog readings
   - Adjust sensor positioning

2. Bluetooth Connectivity
   - Verify COM port settings
   - Check power supply
   - Reset module if needed

### Software Issues
1. Gesture Recognition
   - Adjust confidence threshold
   - Recalibrate sensor ranges
   - Update ML model if needed

2. Performance
   - Monitor CPU usage
   - Check camera frame rate
   - Optimize Bluetooth polling rate

## Future Improvements
1. Hardware
   - Add more flex sensors
   - Implement wireless charging
   - Design custom PCB

2. Software
   - Implement gesture recording
   - Add custom gesture training
   - Improve ML model accuracy

## Maintenance
1. Regular calibration of flex sensors
2. Bluetooth module firmware updates
3. ML model retraining with new data
4. Software updates and patches
