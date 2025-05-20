import sys
import cv2
import os
import numpy as np
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QComboBox, QGroupBox, QGridLayout, QSlider, QAction,
                            QMenuBar, QMenu, QStatusBar, QDockWidget, QDialog,
                            QTabWidget, QLineEdit, QMessageBox)
# Set environment variable to suppress TensorFlow warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppress TensorFlow logging

from utils._Digita import HandDetector
from utils.ppt_converter import PPTConverter
from utils.drawing_helper import DrawingHelper
import win32com.client

class GestureControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize properties
        self.width, self.height = 1280, 720
        self.gestureThreshold = 600
        self.cap = None
        self.ppt_converter = PPTConverter()
        self.slide_images = []
        self.current_slide_idx = 0
        self.detectorHand = HandDetector(detectionCon=0.8, maxHands=1)
        self.delay = 30
        self.buttonPressed = False
        self.counter = 0
        self.drawMode = False
        self.annotations = [[]]
        self.annotationNumber = -1
        self.annotationStart = False
        
        # Gesture mappings (customizable)
        self.gestures = {
            "next_slide": [0, 0, 0, 0, 1],  # Pinky finger
            "prev_slide": [1, 0, 0, 0, 0],  # Thumb
            "pointer": [0, 1, 1, 0, 0],     # Index + Middle
            "draw": [0, 1, 0, 0, 0],        # Index finger
            "erase": [0, 1, 1, 1, 0]        # Index + Middle + Ring
        }
        
        # Initialize UI
        self.initUI()
        
        # Drawing helper
        self.drawing_helper = DrawingHelper()
        # Add drawing properties
        self.current_frame = None
        self.current_slide_image = None
        self.show_camera_overlay = True
        self.camera_overlay_size = (120, 213)  # Small webcam size
        
        # Add new properties for direct image handling
        self.hs, self.ws = int(120 * 1), int(213 * 1)  # Webcam overlay size
        self.imgNumber = 0
        self.delayCounter = 0
        
        # Add flags for separate windows
        self.camera_window = None
        self.slide_window = None
        self.setup_separate_windows()
    
    def setup_separate_windows(self):
        """Create separate windows for camera feed and presentation"""
        # Create camera window
        self.camera_window = cv2.namedWindow("Camera Feed", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Camera Feed", 640, 480)
        
        # Create presentation window
        self.slide_window = cv2.namedWindow("Presentation", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Presentation", 1280, 720)
    
    def initUI(self):
        # Main window setup
        self.setWindowTitle("PowerPoint Gesture Control")
        self.setGeometry(100, 100, 1280, 720)
        try:
            self.setWindowIcon(QIcon("icon.png"))
        except:
            pass  # Ignore if icon not found
        
        # Central widget and layouts
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QVBoxLayout(self.centralWidget)
        
        # Create menu bar
        self.createMenuBar()
        
        # Video display widget
        self.videoWidget = QLabel()
        self.videoWidget.setAlignment(Qt.AlignCenter)
        self.videoWidget.setMinimumSize(800, 600)
        self.videoWidget.setStyleSheet("background-color: #1e1e1e; border-radius: 10px;")
        self.mainLayout.addWidget(self.videoWidget)
        
        # Controls layout
        self.controlsLayout = QHBoxLayout()
        
        # File controls
        self.fileGroup = QGroupBox("Presentation")
        self.fileLayout = QVBoxLayout()
        self.selectFileBtn = QPushButton("Select PPT File")
        self.selectFileBtn.clicked.connect(self.selectPPTFile)
        self.fileLayout.addWidget(self.selectFileBtn)
        self.fileGroup.setLayout(self.fileLayout)
        self.controlsLayout.addWidget(self.fileGroup)
        
        # Camera controls with dropdown for selecting camera
        self.cameraGroup = QGroupBox("Camera")
        self.cameraLayout = QVBoxLayout()
        
        # Add camera selection dropdown
        self.cameraLabel = QLabel("Select Camera:")
        self.cameraSelector = QComboBox()
        self.populateCameraSources()
        
        self.startCamBtn = QPushButton("Start Camera")
        self.startCamBtn.clicked.connect(self.startCamera)
        self.stopCamBtn = QPushButton("Stop Camera")
        self.stopCamBtn.clicked.connect(self.stopCamera)
        self.stopCamBtn.setEnabled(False)
        
        self.cameraLayout.addWidget(self.cameraLabel)
        self.cameraLayout.addWidget(self.cameraSelector)
        self.cameraLayout.addWidget(self.startCamBtn)
        self.cameraLayout.addWidget(self.stopCamBtn)
        self.cameraGroup.setLayout(self.cameraLayout)
        self.controlsLayout.addWidget(self.cameraGroup)
        
        # Status group with more detailed information
        self.statusGroup = QGroupBox("Status")
        self.statusLayout = QVBoxLayout()
        self.gestureLabel = QLabel("Current Gesture: None")
        self.slideLabel = QLabel("Current Slide: N/A")
        self.handStatusLabel = QLabel("Hand Detection: Not Active")
        self.thresholdDisplayLabel = QLabel(f"Gesture Threshold: {self.gestureThreshold}")
        
        self.statusLayout.addWidget(self.gestureLabel)
        self.statusLayout.addWidget(self.slideLabel)
        self.statusLayout.addWidget(self.handStatusLabel)
        self.statusLayout.addWidget(self.thresholdDisplayLabel)
        self.statusGroup.setLayout(self.statusLayout)
        self.controlsLayout.addWidget(self.statusGroup)
        
        # Add controls to main layout
        self.mainLayout.addLayout(self.controlsLayout)
        
        # Status bar with more detailed information
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready - Please select a PPT file and start the camera")
        
        # Initialize timer for video updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {background-color: #2d2d2d;}
            QGroupBox {font-weight: bold; color: #ffffff; background-color: #3d3d3d; border-radius: 5px; margin-top: 10px;}
            QGroupBox::title {subcontrol-origin: margin; left: 10px; padding: 0 5px;}
            QPushButton {background-color: #0078d7; color: white; border-radius: 4px; padding: 6px; font-weight: bold;}
            QPushButton:hover {background-color: #0069c0;}
            QPushButton:disabled {background-color: #666666;}
            QLabel {color: #ffffff;}
        """)
        
    def createMenuBar(self):
        menuBar = self.menuBar()
        
        # File menu
        fileMenu = menuBar.addMenu("File")
        openAction = QAction("Open Presentation", self)
        openAction.triggered.connect(self.selectPPTFile)
        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        
        # Settings menu
        settingsMenu = menuBar.addMenu("Settings")
        customizeAction = QAction("Customize Gestures", self)
        customizeAction.triggered.connect(self.openGestureSettings)
        thresholdAction = QAction("Adjust Threshold", self)
        thresholdAction.triggered.connect(self.openThresholdSettings)
        settingsMenu.addAction(customizeAction)
        settingsMenu.addAction(thresholdAction)
        
        # Help menu
        helpMenu = menuBar.addMenu("Help")
        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.showAboutDialog)
        helpMenu.addAction(aboutAction)
        
    def selectPPTFile(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Select PowerPoint File", "", 
            "PowerPoint Files (*.ppt *.pptx);;All Files (*)", 
            options=options
        )
        
        if filePath:
            self.statusBar.showMessage(f"Selected file: {filePath}")
            self.openPowerPointFile(filePath)
            
    def openPowerPointFile(self, filePath):
        try:
            # Convert PPT to images
            self.slide_images = self.ppt_converter.convert_ppt_to_images(filePath)
            self.current_slide_idx = 0
            
            # Display first slide
            self.displayCurrentSlide()
            
            self.updateSlideLabel()
            QMessageBox.information(self, "Success", "PowerPoint file loaded successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open PowerPoint file: {str(e)}")

    def displayCurrentSlide(self):
        if self.slide_images and 0 <= self.current_slide_idx < len(self.slide_images):
            try:
                # Load the current slide image
                self.current_slide_image = cv2.imread(self.slide_images[self.current_slide_idx])
                if self.current_slide_image is not None:
                    self.current_slide_image = cv2.resize(self.current_slide_image, (1280, 720))
                    self.updatePresentationWindow()
            except Exception as e:
                self.statusBar.showMessage(f"Error displaying slide: {str(e)}")

    def updateSlideLabel(self):
        if self.slide_images:
            self.slideLabel.setText(f"Current Slide: {self.current_slide_idx + 1}/{len(self.slide_images)}")

    def populateCameraSources(self):
        """Populate the camera sources dropdown with available cameras"""
        self.cameraSelector.clear()
        
        # Check for available cameras (usually up to 10 is a reasonable search space)
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        
        # Add available cameras to the dropdown
        if available_cameras:
            for cam_id in available_cameras:
                self.cameraSelector.addItem(f"Camera {cam_id}", cam_id)
        else:
            self.cameraSelector.addItem("No cameras found", -1)
    
    def startCamera(self):
        camera_id = self.cameraSelector.currentData()
        if camera_id == -1:
            QMessageBox.warning(self, "Warning", "No camera selected or available")
            return
            
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)
        
        if self.cap.isOpened():
            self.startCamBtn.setEnabled(False)
            self.stopCamBtn.setEnabled(True)
            self.cameraSelector.setEnabled(False)
            self.timer.start(30)  # Update every 30ms
            self.statusBar.showMessage(f"Camera {camera_id} started")
            self.handStatusLabel.setText("Hand Detection: Active")
        else:
            QMessageBox.critical(self, "Error", f"Could not open camera {camera_id}")
    
    def stopCamera(self):
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.videoWidget.clear()
            self.startCamBtn.setEnabled(True)
            self.stopCamBtn.setEnabled(False)
            self.cameraSelector.setEnabled(True)
            self.handStatusLabel.setText("Hand Detection: Not Active")
            self.statusBar.showMessage("Camera stopped")
    
    def updateFrame(self):
        success, img = self.cap.read()
        if success:
            img = cv2.flip(img, 1)
            
            # Process hand detection
            try:
                hands, img = self.detectorHand.findHands(img)
                
                if hands:
                    self.handStatusLabel.setText(f"Hand Detection: Detected {len(hands)} hand(s)")
                else:
                    self.handStatusLabel.setText("Hand Detection: No hands detected")
                    
            except Exception as e:
                hands = []
                self.handStatusLabel.setText(f"Hand Detection Error: {str(e)}")
                self.statusBar.showMessage(f"Error in hand detection: {str(e)}")
            
            # Draw gesture threshold line
            cv2.line(img, (0, self.gestureThreshold), (self.width, self.gestureThreshold), 
                     (0, 255, 0), 5)
            cv2.putText(img, "Gesture Threshold", (10, self.gestureThreshold - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Handle gestures
            if hands and self.buttonPressed is False and self.slide_images:
                self.processHandGestures(hands, img)
            else:
                self.drawing_helper.stop_annotation()

            if self.buttonPressed:
                self.counter += 1
                if self.counter > self.delay:
                    self.counter = 0
                    self.buttonPressed = False
            
            # Show camera feed
            cv2.imshow("Camera Feed", img)
            
            # Update the presentation window if we have a slide
            if self.current_slide_image is not None:
                self.updatePresentationWindow()

    def updatePresentationWindow(self):
        """Update the presentation window with current slide and annotations"""
        if self.current_slide_image is None:
            return
            
        # Create a copy to draw on
        display_image = self.current_slide_image.copy()
        
        # Draw annotations
        display_image = self.drawing_helper.draw_annotations(display_image)
        
        # Show presentation
        cv2.imshow("Presentation", display_image)
    
    def closeEvent(self, event):
        """Handle application closing"""
        # Close OpenCV windows
        cv2.destroyAllWindows()
        
        # Stop camera if running
        if self.cap and self.cap.isOpened():
            self.cap.release()
        
        # Cleanup
        self.ppt_converter.cleanup()
        event.accept()

    def openThresholdSettings(self):
        dialog = ThresholdSettingsDialog(self.gestureThreshold, self)
        if dialog.exec_():
            self.gestureThreshold = dialog.getThreshold()
            self.thresholdDisplayLabel.setText(f"Gesture Threshold: {self.gestureThreshold}")
            self.statusBar.showMessage(f"Threshold updated to {self.gestureThreshold}")

    def openGestureSettings(self):
        """Opens the gesture settings dialog"""
        dialog = GestureSettingsDialog(self.gestures, parent=self)
        if dialog.exec_():
            self.gestures = dialog.getGestures()
            self.statusBar.showMessage("Gesture settings updated")
    
    def processHandGestures(self, hands, img):
        try:
            hand = hands[0]
            cx, cy = hand["center"]
            lmList = hand["lmList"]
            fingers = self.detectorHand.fingersUp(hand)
            
            # Calculate drawing coordinates (similar to reference code)
            xVal = int(np.interp(lmList[8][0], [self.width // 2, self.width], [0, self.width]))
            yVal = int(np.interp(lmList[8][1], [150, self.height-150], [0, self.height]))
            indexFinger = (xVal, yVal)
            
            if cy <= self.gestureThreshold:
                # Previous slide gesture
                if fingers == [1, 0, 0, 0, 0]:
                    self.statusBar.showMessage("Left")
                    self.buttonPressed = True
                    if self.current_slide_idx > 0:
                        self.current_slide_idx -= 1
                        self.drawing_helper.clear_annotations()
                        self.displayCurrentSlide()
                        self.updateSlideLabel()
                
                # Next slide gesture
                if fingers == [0, 0, 0, 0, 1]:
                    self.statusBar.showMessage("Right")
                    self.buttonPressed = True
                    if self.current_slide_idx < len(self.slide_images) - 1:
                        self.current_slide_idx += 1
                        self.drawing_helper.clear_annotations()
                        self.displayCurrentSlide()
                        self.updateSlideLabel()
            
            # Pointer mode
            if fingers == [0, 1, 1, 0, 0]:
                cv2.circle(self.current_slide_image, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                self.updatePresentationWindow()
            
            # Drawing mode
            if fingers == [0, 1, 0, 0, 0]:
                self.drawing_helper.start_annotation(indexFinger)
                cv2.circle(self.current_slide_image, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                self.updatePresentationWindow()
            else:
                self.drawing_helper.stop_annotation()
            
            # Erase last annotation
            if fingers == [0, 1, 1, 1, 0]:
                self.drawing_helper.undo_last_annotation()
                self.updatePresentationWindow()
                self.buttonPressed = True
                
        except Exception as e:
            self.statusBar.showMessage(f"Error processing gesture: {str(e)}")
    
    def compareGestures(self, detected, reference):
        """Compare detected gesture with reference gesture with some tolerance"""
        return detected == reference
    
    def drawHandGestureInfo(self, img, hand, fingers):
        """Draw additional information about the detected hand gesture"""
        # Draw hand center
        cx, cy = hand["center"]
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        
        # Draw text indicating which fingers are up
        finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
        text = "Fingers: "
        text += ", ".join([finger_names[i] for i, is_up in enumerate(fingers) if is_up == 1])
        if not any(fingers):
            text += "None"
            
        cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Indicate if hand is above threshold
        if cy <= self.gestureThreshold:
            cv2.putText(img, "Above Threshold - Gesture Active", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def showAboutDialog(self):
        """Shows the About dialog with application information"""
        QMessageBox.about(
            self,
            "About PowerPoint Gesture Control",
            """<h3>PowerPoint Gesture Control</h3>
            <p>Version 1.0</p>
            <p>A gesture-based presentation control system that allows you to control 
            PowerPoint presentations using hand gestures.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Touchless presentation control</li>
                <li>Customizable gestures</li>
                <li>Real-time hand tracking</li>
                <li>PowerPoint integration</li>
            </ul>
            <p>&copy; 2024 All rights reserved.</p>"""
        )

class GestureSettingsDialog(QDialog):
    def __init__(self, gestures, parent=None):
        super().__init__(parent)
        self.gestures = gestures.copy()
        self.setWindowTitle("Customize Gestures")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Create form for each gesture
        formLayout = QGridLayout()
        
        row = 0
        self.gestureInputs = {}
        for action, gesture in self.gestures.items():
            label = QLabel(f"{action.replace('_', ' ').title()}:")
            inputField = QLineEdit(', '.join(map(str, gesture)))
            formLayout.addWidget(label, row, 0)
            formLayout.addWidget(inputField, row, 1)
            self.gestureInputs[action] = inputField
            row += 1
        
        # Help text
        helpLabel = QLabel("Enter 5 values (0 or 1) separated by commas.\nEach value represents a finger state:\nThumb, Index, Middle, Ring, Pinky")
        helpLabel.setWordWrap(True)
        
        # Buttons
        buttonLayout = QHBoxLayout()
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        resetButton = QPushButton("Reset to Default")
        resetButton.clicked.connect(self.resetToDefault)
        
        buttonLayout.addWidget(resetButton)
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(saveButton)
        
        layout.addLayout(formLayout)
        layout.addWidget(helpLabel)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
    
    def getGestures(self):
        """Validates and returns the updated gesture settings"""
        result = {}
        for action, inputField in self.gestureInputs.items():
            try:
                gesture = [int(x.strip()) for x in inputField.text().split(',')]
                if len(gesture) == 5 and all(x in [0, 1] for x in gesture):
                    result[action] = gesture
                else:
                    result[action] = self.gestures[action]  # Keep original if invalid
            except:
                result[action] = self.gestures[action]  # Keep original if parsing fails
        return result
    
    def resetToDefault(self):
        """Reset gesture settings to default values"""
        default_gestures = {
            "next_slide": [0, 0, 0, 0, 1],
            "prev_slide": [1, 0, 0, 0, 0],
            "pointer": [0, 1, 1, 0, 0],
            "draw": [0, 1, 0, 0, 0],
            "erase": [0, 1, 1, 1, 0]
        }
        
        for action, gesture in default_gestures.items():
            if action in self.gestureInputs:
                self.gestureInputs[action].setText(', '.join(map(str, gesture)))

class ThresholdSettingsDialog(QDialog):
    def __init__(self, threshold, parent=None):
        super().__init__(parent)
        self.threshold = threshold
        self.setWindowTitle("Adjust Gesture Threshold")
        
        layout = QVBoxLayout()
        
        # Slider for threshold
        self.thresholdSlider = QSlider(Qt.Horizontal)
        self.thresholdSlider.setMinimum(100)
        self.thresholdSlider.setMaximum(1000)
        self.thresholdSlider.setValue(threshold)
        self.thresholdSlider.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider.setTickInterval(100)
        
        self.valueLabel = QLabel(f"Threshold: {threshold}")
        self.thresholdSlider.valueChanged.connect(self.updateLabel)
        
        # Description
        descLabel = QLabel("Adjust the gesture threshold line. Gestures are recognized only when your hand is above this line.")
        descLabel.setWordWrap(True)
        
        # Buttons
        buttonLayout = QHBoxLayout()
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        
        buttonLayout.addWidget(cancelButton)
        buttonLayout.addWidget(saveButton)
        
        layout.addWidget(descLabel)
        layout.addWidget(self.thresholdSlider)
        layout.addWidget(self.valueLabel)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
    
    def updateLabel(self, value):
        self.valueLabel.setText(f"Threshold: {value}")
    
    def getThreshold(self):
        return self.thresholdSlider.value()

if __name__ == "__main__":
    # Set application attributes before creating the app instance
    # This helps avoid some deprecation warnings
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    app = QApplication(sys.argv)
    window = GestureControlApp()
    window.show()
    sys.exit(app.exec_())