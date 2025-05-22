# Gesture Digita - Software User Manual

This comprehensive guide provides detailed instructions for installing, configuring, and using the Gesture Digita software system.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [First-Time Setup](#first-time-setup)
4. [User Interface](#user-interface)
5. [Basic Operations](#basic-operations)
6. [Gesture Controls](#gesture-controls)
7. [Advanced Features](#advanced-features)
8. [Configuration Settings](#configuration-settings)
9. [Bluetooth Connection](#bluetooth-connection)
10. [Troubleshooting](#troubleshooting)
11. [Frequently Asked Questions](#frequently-asked-questions)

## System Requirements

### Hardware Requirements
- Computer with USB port or Bluetooth capability
- Camera (built-in webcam or external USB camera)
- Arduino-based gesture sensor system (see Hardware Diagram documentation)
- Minimum 4GB RAM (8GB recommended)
- 500MB available disk space

### Software Requirements
- Windows 10/11, macOS 10.14+, or Ubuntu 18.04+
- Python 3.8 or newer
- OpenCV 4.5.5+
- PyQt5 5.15.6+
- MediaPipe 0.9.0+
- TensorFlow 2.10.0+
- Microsoft PowerPoint or compatible presentation software

## Installation

### Standard Installation

1. **Clone or download the repository**:
   ```bash
   git clone https://github.com/xer0bit/gesture-digita.git
   cd gesture-digita
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run_app.py
   ```

### Virtual Environment Installation (Recommended)

1. **Create and activate virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies in the virtual environment**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run_app.py
   ```

### Installation Verification

After installation, verify that all components are working:

1. Launch the application
2. The main window should appear without errors
3. Camera selection dropdown should show available cameras
4. Bluetooth device selection should show available devices (if any)

## First-Time Setup

### Initial Configuration

1. **Launch Gesture Digita**:
   ```bash
   python run_app.py
   ```

2. **Connect Hardware**:
   - Connect the Arduino-based gesture sensor via USB or Bluetooth
   - Select the appropriate connection method from the dropdown menu
   - Click "Connect" to establish communication

3. **Camera Setup**:
   - Select your preferred camera from the dropdown menu
   - Adjust camera position to capture your hand gestures clearly
   - Ensure adequate lighting for optimal recognition

4. **Calibration**:
   - Click "Calibrate" button to start sensor calibration
   - Follow on-screen instructions for each sensor position
   - Complete the calibration process to improve gesture recognition accuracy

5. **Test Gestures**:
   - Use the "Test Mode" to verify that gestures are recognized correctly
   - Make adjustments to threshold settings if needed

## User Interface

### Main Window Layout

The Gesture Digita interface is divided into several key areas:

```
┌────────────────────────────────────────────────────────────────┐
│ ┌─Toolbar───────────────────────────────────────────────────┐  │
│ │ File | Settings | View | Help                             │  │
│ └───────────────────────────────────────────────────────────┘  │
│ ┌─Connection Panel─┐ ┌─Presentation Controls─────────────────┐ │
│ │ Camera: [-----v] │ │ ┌─Prev─┐   ┌─Current Slide─┐  ┌─Next┐ │ │
│ │ Connect [Button] │ │ │  <<  │   │      1/24     │  │ >>  │ │ │
│ │ Status: [-----]  │ │ └──────┘   └───────────────┘  └─────┘ │ │
│ └─────────────────┘ └────────────────────────────────────────┘ │
│ ┌─Camera Preview──────────────┐ ┌─Slide Preview─────────────┐  │
│ │                             │ │                           │  │
│ │                             │ │                           │  │
│ │                             │ │                           │  │
│ │                             │ │                           │  │
│ │                             │ │                           │  │
│ └─────────────────────────────┘ └───────────────────────────┘  │
│ ┌─Gesture Recognition Status────────────────────────────────┐  │
│ │ Current Gesture: [------------]  Confidence: [------]     │  │
│ │ Sensor Values: [----------------------------------------] │  │
│ └───────────────────────────────────────────────────────────┘  │
│ ┌─Status Bar────────────────────────────────────────────────┐  │
│ │ Ready                                                     │  │
│ └───────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Interface Elements

1. **Toolbar**:
   - File: Open presentation, save settings, exit
   - Settings: Configure camera, gesture thresholds, connection settings
   - View: Change layout, toggle components
   - Help: Access documentation, about information

2. **Connection Panel**:
   - Camera selection dropdown
   - Connection button to start/stop camera
   - Bluetooth device selection
   - Connection status indicator

3. **Presentation Controls**:
   - Previous/Next slide buttons
   - Current slide indicator
   - Presentation name

4. **Camera Preview**:
   - Live camera feed
   - Visualized hand tracking
   - Gesture recognition threshold line
   - Recognition confidence visualization

5. **Slide Preview**:
   - Current presentation slide
   - Drawing annotations
   - Pointer indicator

6. **Gesture Recognition Status**:
   - Current detected gesture
   - Confidence level
   - Raw sensor values

7. **Status Bar**:
   - System status messages
   - Error notifications
   - Connection status

## Basic Operations

### Opening a Presentation

1. Click "File" > "Open Presentation" or use the keyboard shortcut (Ctrl+O)
2. Browse to select a PowerPoint (.ppt, .pptx) or PDF file
3. Click "Open" to load the presentation
4. The first slide will appear in the slide preview pane

### Starting Camera

1. Select the desired camera from the dropdown menu
2. Click the "Start Camera" button
3. Adjust your position to ensure your hand is visible in the frame
4. Verify that hand landmarks are detected (shown as connected dots)

### Connecting to Hardware

1. Ensure Arduino hardware is powered on
2. Select the appropriate COM port from the dropdown menu
3. Click "Connect" to establish communication with the hardware
4. Verify connection status shows "Connected"
5. Test sensor readings by moving fingers

### Navigating Slides

1. **Using Buttons**:
   - Click "Next" button or right arrow key to advance to the next slide
   - Click "Previous" button or left arrow key to go back to the previous slide

2. **Using Gestures**:
   - Thumb up gesture (👍) to go to previous slide
   - Pinky up gesture (🤙) to go to next slide

## Gesture Controls

### Standard Gestures

| Gesture | Description | Action |
|---------|-------------|--------|
| 👍 Thumb up | Extend thumb, curl other fingers | Previous slide |
| 🤙 Pinky up | Extend pinky, curl other fingers | Next slide |
| ☝️ Index finger | Extend index finger only | Drawing mode |
| ✌️ Index + Middle | Extend index and middle fingers | Pointer mode |
| 🖖 Three fingers | Extend index, middle, and ring fingers | Erase last annotation |
| ✋ Open palm | All fingers extended | Clear all annotations |

### Using Drawing Mode

1. Make the Index finger gesture (☝️)
2. Position your hand above the threshold line
3. Move your finger to draw on the current slide
4. Release the gesture to stop drawing
5. Annotations persist across slide changes

### Using Pointer Mode

1. Make the Index + Middle finger gesture (✌️)
2. A pointer dot appears on the slide
3. Move your hand to position the pointer
4. The pointer disappears when you change gestures

### Erasing Annotations

1. **Erase Last Annotation**:
   - Make the Three finger gesture (🖖)
   - The most recent annotation will be removed

2. **Clear All Annotations**:
   - Make the Open palm gesture (✋)
   - All annotations on the current slide will be removed

## Advanced Features

### Customizing Gestures

1. Click "Settings" > "Gesture Configuration"
2. For each action, you can modify the associated gesture:
   - Select the action from the dropdown
   - Configure which fingers need to be extended
   - Set confidence thresholds
3. Click "Save" to apply changes
4. Test the new gesture configuration

### Camera Settings

1. Click "Settings" > "Camera Configuration"
2. Adjust settings:
   - Resolution: Select from available resolutions
   - Frame Rate: Adjust processing frame rate
   - Flip Horizontally/Vertically: Mirror camera if needed
   - Threshold Line: Adjust the height of the gesture activation line
3. Click "Apply" to save changes

### Presentation Settings

1. Click "Settings" > "Presentation Settings"
2. Configure:
   - Default Drawing Color: Select color for annotations
   - Drawing Thickness: Adjust line thickness
   - Pointer Size: Modify the size of the pointer dot
   - Slide Transition Effect: Choose between available effects
3. Click "Save" to apply settings

### Sensor Calibration

For hardware-based configuration:

1. Click "Settings" > "Sensor Calibration"
2. Follow the on-screen instructions:
   - Flex each finger to its maximum and minimum positions
   - Hold each position for the specified time
   - Complete the process for all sensors
3. The system will calculate optimal thresholds
4. Click "Save Calibration" to store these values

## Configuration Settings

### General Settings

| Setting | Description | Default Value |
|---------|-------------|---------------|
| Start Maximized | Launch application in full-screen | On |
| Auto-Connect | Automatically connect to last used device | On |
| Dark Mode | Use dark color theme | Off |
| Auto-Save Annotations | Automatically save annotations | On |
| Language | Interface language | English |

### Camera Settings

| Setting | Description | Default Value |
|---------|-------------|---------------|
| Camera Index | Selected camera device | 0 (default) |
| Resolution | Camera resolution | 640x480 |
| Frame Rate | Processing frame rate | 30 FPS |
| Horizontal Flip | Mirror horizontally | Off |
| Vertical Flip | Mirror vertically | Off |
| Threshold Line | Gesture activation line height | 60% |

### Gesture Settings

| Setting | Description | Default Value |
|---------|-------------|---------------|
| Gesture Confidence | Minimum confidence for recognition | 0.8 |
| Gesture Hold Time | Time to hold gesture for activation | 500ms |
| Hand Detection Method | Detection algorithm | MediaPipe |
| Left Hand Support | Enable left hand detection | On |
| Right Hand Support | Enable right hand detection | On |

### Presentation Settings

| Setting | Description | Default Value |
|---------|-------------|---------------|
| Drawing Color | Annotation color (RGB) | (0, 0, 200) |
| Drawing Thickness | Line thickness | 12px |
| Pointer Size | Size of pointer dot | 20px |
| Slide Change Effect | Transition animation | Fade |
| Auto-Hide Controls | Hide UI controls during presentation | Off |

## Bluetooth Connection

### Pairing a Device

Before connecting to the Arduino hardware via Bluetooth:

1. Ensure the HC-05 Bluetooth module is powered on
2. Open your computer's Bluetooth settings
3. Scan for new devices
4. Select "HC-05" (default name) or your custom device name
5. Enter pairing code (default: 1234)
6. Complete the pairing process

### Connecting in Gesture Digita

1. Launch Gesture Digita application
2. Click "Settings" > "Connection Settings"
3. Select "Bluetooth" as the connection type
4. Choose your paired HC-05 device from the dropdown
5. Click "Connect"
6. Verify status shows "Connected"
7. Test by moving fingers and observing sensor values

### Troubleshooting Bluetooth

If connection fails:
1. Ensure device is paired at the system level
2. Verify device is powered on
3. Check if COM port is correct
4. Try disconnecting and reconnecting
5. Restart the application
6. Consider using USB connection as a backup

## Troubleshooting

### Common Issues and Solutions

| Issue | Possible Causes | Solutions |
|-------|----------------|-----------|
| Camera not detected | Driver issue, USB connection | Reconnect camera, update drivers, try different USB port |
| Hand not tracked | Poor lighting, position | Improve lighting, keep hand within camera view |
| Gestures not recognized | Calibration issues, threshold | Recalibrate, adjust gesture thresholds |
| Bluetooth not connecting | Pairing issue, COM port | Re-pair device, verify COM port, check power |
| Slow performance | System resources, resolution | Lower camera resolution, close other applications |
| Drawing lag | Processing delay | Reduce frame rate, simplify gestures |
| Presentation not loading | File format, permissions | Check file format, verify file permissions |
| Application crashes | Memory issues, conflicts | Restart application, update dependencies |

### Diagnostic Tools

1. **System Information**:
   - Click "Help" > "System Information"
   - Review hardware and software details
   - Copy information for support tickets

2. **Gesture Test Mode**:
   - Click "Help" > "Gesture Test"
   - Perform gestures and see raw recognition data
   - Helps identify specific recognition issues

3. **Log Viewer**:
   - Click "Help" > "View Logs"
   - Review application logs for errors
   - Filter by severity and component

4. **Connection Diagnostics**:
   - Click "Settings" > "Connection" > "Run Diagnostics"
   - Tests hardware connectivity
   - Provides detailed error messages

## Frequently Asked Questions

### General Questions

**Q: Can I use Gesture Digita with any presentation software?**
A: The software is primarily designed for PowerPoint and PDF files, but can control any application by mapping gestures to keyboard shortcuts.

**Q: How many gestures can I configure?**
A: The system supports up to 10 distinct gestures, which can be customized in the settings.

**Q: Can I use Gesture Digita without the hardware sensors?**
A: Yes, the software can work with just the camera for hand tracking, though the hardware sensors provide additional precision.

**Q: Is my presentation data stored anywhere?**
A: Slides are temporarily stored in the "Presentation" folder while the application is running but are not permanently saved.

### Technical Questions

**Q: What cameras are supported?**
A: Any standard webcam or USB camera compatible with your operating system should work.

**Q: How accurate is the gesture recognition?**
A: The system achieves approximately 95% accuracy after proper calibration in good lighting conditions.

**Q: Can I use wireless sensors?**
A: Yes, the Arduino-based sensor system can connect via Bluetooth for wireless operation.

**Q: How do I update the software?**
A: Check the GitHub repository for updates, or use the "Check for Updates" option in the Help menu.

### Troubleshooting Questions

**Q: Why is my hand not being detected?**
A: Ensure adequate lighting, position your hand within camera view, and check that no other applications are using the camera.

**Q: Why are my gestures intermittently recognized?**
A: Try recalibrating the system, ensure consistent lighting, and check that your hand is positioned above the threshold line.

**Q: The application is running slowly. How can I improve performance?**
A: Lower the camera resolution, reduce the frame rate in settings, and close other resource-intensive applications.

## Support and Resources

### Getting Help

- **Documentation**: Full documentation is available in the "docs" folder
- **GitHub Issues**: Report bugs and request features on the GitHub repository
- **Email Support**: Contact bsem-f21-129@superior.edu.pk for assistance
- **Community Forum**: Discuss issues and share tips on the project forum

### Resources

- **Tutorial Videos**: Available on the project YouTube channel
- **Sample Presentations**: Test presentations are included in the "samples" folder
- **Development Guide**: Information for contributors in CONTRIBUTING.md
- **Release Notes**: Details about current and past versions in CHANGELOG.md

---

© 2023 Gesture Digita Team. All rights reserved.
