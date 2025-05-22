# Gesture Digita - Advanced Presentation Control System

Gesture Digita is a modern presentation control system that allows users to control PowerPoint presentations using natural hand gestures. Built with Python and powered by AI-based gesture recognition, it offers an intuitive and touchless way to navigate through slides and interact with presentations.

## Features

- **Intuitive Gesture Controls**
  - 👍 Thumb up: Previous slide
  - 🤙 Pinky up: Next slide
  - ☝️ Index finger: Drawing mode
  - ✌️ Index + Middle fingers: Pointer mode
  - 🖖 Index + Middle + Ring fingers: Erase last annotation

- **AI-Powered Recognition**
  - Real-time hand tracking
  - Machine learning-based gesture recognition
  - Adaptive gesture thresholding
  - Support for both left and right hands

- **Drawing & Annotation**
  - Real-time drawing on slides
  - Pointer mode for highlighting
  - Annotation undo/redo support
  - Clear annotations feature

- **Professional Interface**
  - Modern Qt-based GUI
  - Live hand tracking preview
  - Slide complexity analysis
  - Customizable gesture settings

## Installation

1. Clone the repository:
```bash
git clone https://github.com/xer0bit/gesture-digita.git
cd gesture-digita
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python run_app.py
```

## Requirements

- Python 3.8+
- OpenCV 4.5.5+
- PyQt5 5.15.6+
- MediaPipe 0.9.0+
- TensorFlow 2.10.0+
- Other dependencies listed in `requirements.txt`

## Hardware Requirements

### Components
- Arduino Nano (ATmega328P)
- 3x Flex Sensors (4.5")
- HC-05 Bluetooth Module
- 10kΩ Resistors (3x)
- Connecting wires
- USB cable for Arduino

### Additional Requirements
- Soldering iron and solder
- Breadboard for prototyping
- Multimeter for testing
- Heat shrink tubing

For detailed technical documentation, including circuit diagrams, implementation details, and troubleshooting guides, see [Technical Documentation](docs/technical_documentation.md).

## Project Structure

```
code final/
├── assets/                 # Application icons and images
├── models/                 # ML model files
├── utils/                 # Utility modules
│   ├── _Digita.py        # Hand detection implementation
│   ├── ml_gesture_recognizer.py  # Gesture recognition
│   ├── ppt_converter.py  # PowerPoint handling
│   ├── drawing_helper.py # Drawing utilities
│   └── debug_helper.py   # Debugging utilities
├── main.py               # Main application
├── run_app.py           # Application entry point
└── requirements.txt     # Project dependencies
```

## Usage

1. Launch the application using `python run_app.py`
2. Select a PowerPoint presentation using the "Select Presentation File" button
3. Start the camera using the "Start Camera" button
4. Use the following gestures above the threshold line:
   - Thumb up to go to previous slide
   - Pinky up to go to next slide
   - Index finger to draw
   - Index + Middle fingers for pointer mode
   - Index + Middle + Ring fingers to erase last annotation

## Customization

### Gesture Settings
1. Click "Customize Gestures" in the settings menu
2. Modify finger combinations for each action
3. Save your custom gesture mappings

### Camera Settings
1. Select your preferred camera from the dropdown
2. Adjust the gesture threshold using the slider
3. Toggle hand-only mode for cleaner visualization

## Troubleshooting

Common issues and solutions:

1. **Camera not detected**
   - Ensure camera is properly connected
   - Try different camera indices in the selector
   - Check camera permissions

2. **Gestures not recognized**
   - Adjust the gesture threshold
   - Ensure hand is clearly visible
   - Check lighting conditions
   - Keep hand above the threshold line

3. **Performance issues**
   - Close other applications using the camera
   - Reduce the camera resolution if needed
   - Ensure system meets minimum requirements

## Core Workflow

1. **Presentation Processing**
   - Supports both PowerPoint (.ppt, .pptx) and PDF files
   - Converts presentations into high-quality PNG images (1280x720)
   - Preserves text content for ML analysis
   - Stores slides in temporary "Presentation" folder
   - Analyzes slide complexity for gesture sensitivity

2. **Gesture Recognition**
   - Real-time hand landmark detection (21 points)
   - Normalized 3D coordinates for consistent recognition
   - Gesture smoothing with temporal filtering
   - Confidence scoring (0.0-1.0) for each gesture
   - Gesture state machine for robust transitions

3. **Drawing & Annotation System**
   - Vector-based drawing for smooth lines
   - Point-based gesture tracking (12px thickness)
   - RGB color system (default: red=0, blue=200)
   - Annotation history for undo/redo
   - Multi-layer drawing support

4. **Performance Optimizations**
   - Slide caching for instant transitions
   - Parallel image processing
   - Memory-efficient slide storage
   - Background thread for ML processing
   - Frame skip for smooth performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- OpenCV for computer vision capabilities
- MediaPipe for hand tracking
- PyQt5 for the GUI framework
- TensorFlow for machine learning support

## Contact

For questions and support, please open an issue on the GitHub repository or contact the development team at bsem-f21-129@superior.edu.pk
