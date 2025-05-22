import sys
import cv2
import os
import logging
import numpy as np
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QSize, QPropertyAnimation, QRect
from PyQt5.QtGui import QImage, QPixmap, QIcon, QColor, QPalette, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QComboBox, QGroupBox, QGridLayout, QSlider, QAction,
                            QMenuBar, QMenu, QStatusBar, QDockWidget, QDialog,
                            QTabWidget, QLineEdit, QMessageBox, QSplitter, QFrame,
                            QProgressBar, QCheckBox, QSizePolicy, QSpacerItem, QStyle)

# Set environment variable to suppress TensorFlow warnings
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppress TensorFlow logging

from utils._Digita import HandDetector
from utils.ppt_converter import PPTConverter
from utils.drawing_helper import DrawingHelper
from utils.ml_gesture_recognizer import MLGestureRecognizer
import win32com.client
import time


class GestureControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize logger
        self.logger = self.setup_logger()
        
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
        
        # Machine learning model
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "gesture_model.pkl")
        self.ml_recognizer = MLGestureRecognizer(model_path)
        
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
        self.hand_only_mode = True  # Show only hand landmarks, not the full camera feed
        
        # Initialize UI with modern professional look
        self.initUI()
        self.setup_separate_windows()
        
        # Initialize gesture mappings
        self.gestures = {
            "next_slide": [0, 0, 0, 0, 1],  # Pinky finger
            "prev_slide": [1, 0, 0, 0, 0],  # Thumb
            "pointer": [0, 1, 1, 0, 0],     # Index + Middle
            "draw": [0, 1, 0, 0, 0],        # Index finger
            "erase": [0, 1, 1, 1, 0]        # Index + Middle + Ring
        }
        
        # Gesture cooldown properties
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # seconds between gestures
        self.last_processed_gesture = None
        
    def setup_logger(self):
        """Setup logging for the application"""
        logger = logging.getLogger('gesture_app')
        
        # Create handler if not already configured
        if not logger.handlers:
            # Configure logger
            logger.setLevel(logging.INFO)
            
            # Create logs directory if it doesn't exist
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # File handler
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f"app_log_{timestamp}.log")
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Format
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
        
    def setup_separate_windows(self):
        """Remove separate OpenCV windows"""
        pass  # We'll use Qt windows instead

    def initUI(self):
        # Main window setup
        self.setWindowTitle("Gesture Digita - Advanced Presentation Control")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        try:
            app_icon = QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "app_icon.png"))
            self.setWindowIcon(app_icon)
        except:
            # Fallback to system icon
            self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Central widget
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        
        # Main layout
        mainLayout = QVBoxLayout(self.centralWidget)
        mainLayout.setContentsMargins(10, 10, 10, 10)
        mainLayout.setSpacing(10)
        
        # Create menu bar
        self.createMenuBar()
        
        # Header with title and logo
        headerFrame = QFrame()
        headerFrame.setFrameShape(QFrame.StyledPanel)
        headerFrame.setStyleSheet("background-color: #2c3e50; border-radius: 8px;")
        headerLayout = QHBoxLayout(headerFrame)
        
        titleLabel = QLabel("Gesture Control Presentation System")
        titleLabel.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        headerLayout.addWidget(titleLabel)
        
        # Add logo or app icon
        try:
            logoLabel = QLabel()
            logoPixmap = QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png"))
            logoLabel.setPixmap(logoPixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            headerLayout.addWidget(logoLabel)
        except:
            pass
        
        mainLayout.addWidget(headerFrame)
        
        # Main content area
        contentSplitter = QSplitter(Qt.Horizontal)
        contentSplitter.setHandleWidth(2)
        contentSplitter.setChildrenCollapsible(False)
        
        # Left panel - Controls
        leftPanel = QWidget()
        leftPanelLayout = QVBoxLayout(leftPanel)
        leftPanelLayout.setContentsMargins(5, 5, 5, 5)
        
        # File controls
        fileGroup = self.createControlGroup("Presentation", leftPanelLayout)
        fileLayout = QVBoxLayout()
        self.selectFileBtn = self.createStyledButton("Select Presentation File", "document-open")
        self.selectFileBtn.clicked.connect(self.selectPPTFile)
        fileLayout.addWidget(self.selectFileBtn)
        
        # Current slide info
        self.slideInfoLabel = QLabel("No presentation loaded")
        self.slideInfoLabel.setWordWrap(True)
        self.slideInfoLabel.setStyleSheet("font-size: 14px;")
        fileLayout.addWidget(self.slideInfoLabel)
        
        # Slide navigation
        navLayout = QHBoxLayout()
        self.prevSlideBtn = self.createStyledButton("", "go-previous")
        self.prevSlideBtn.setIconSize(QSize(24, 24))
        self.prevSlideBtn.clicked.connect(self.prev_slide)
        self.prevSlideBtn.setEnabled(False)
        
        self.nextSlideBtn = self.createStyledButton("", "go-next")
        self.nextSlideBtn.setIconSize(QSize(24, 24))
        self.nextSlideBtn.clicked.connect(self.next_slide)
        self.nextSlideBtn.setEnabled(False)
        
        navLayout.addWidget(self.prevSlideBtn)
        navLayout.addWidget(self.nextSlideBtn)
        fileLayout.addLayout(navLayout)
        
        # Add slide complexity indicator
        self.complexityLabel = QLabel("Slide Complexity: N/A")
        self.complexityLabel.setStyleSheet("font-size: 12px;")
        fileLayout.addWidget(self.complexityLabel)
        
        fileGroup.setLayout(fileLayout)
        
        # Camera controls
        cameraGroup = self.createControlGroup("Camera", leftPanelLayout)
        cameraLayout = QVBoxLayout()
        
        # Camera selection
        cameraSelLayout = QHBoxLayout()
        cameraSelLayout.addWidget(QLabel("Camera:"))
        self.cameraSelector = QComboBox()
        self.cameraSelector.setStyleSheet("padding: 5px;")
        self.populateCameraSources()
        cameraSelLayout.addWidget(self.cameraSelector)
        cameraLayout.addLayout(cameraSelLayout)
        
        # Camera buttons
        camButtonLayout = QHBoxLayout()
        self.startCamBtn = self.createStyledButton("Start Camera", "media-playback-start")
        self.startCamBtn.clicked.connect(self.startCamera)
        
        self.stopCamBtn = self.createStyledButton("Stop Camera", "media-playback-stop")
        self.stopCamBtn.clicked.connect(self.stopCamera)
        self.stopCamBtn.setEnabled(False)
        
        camButtonLayout.addWidget(self.startCamBtn)
        camButtonLayout.addWidget(self.stopCamBtn)
        cameraLayout.addLayout(camButtonLayout)
        
        # Show only hand landmarks option
        self.handOnlyCheckbox = QCheckBox("Show only hand landmarks")
        self.handOnlyCheckbox.setChecked(self.hand_only_mode)
        self.handOnlyCheckbox.toggled.connect(self.toggleHandOnlyMode)
        cameraLayout.addWidget(self.handOnlyCheckbox)
        
        cameraGroup.setLayout(cameraLayout)
        
        # Gesture controls
        gestureGroup = self.createControlGroup("Gesture Settings", leftPanelLayout)
        gestureLayout = QVBoxLayout()
        
        # Threshold slider
        thresholdLayout = QHBoxLayout()
        thresholdLayout.addWidget(QLabel("Gesture Threshold:"))
        self.thresholdSlider = QSlider(Qt.Horizontal)
        self.thresholdSlider.setMinimum(100)
        self.thresholdSlider.setMaximum(1000)
        self.thresholdSlider.setValue(self.gestureThreshold)
        self.thresholdSlider.setTickPosition(QSlider.TicksBelow)
        self.thresholdSlider.setTickInterval(100)
        self.thresholdSlider.valueChanged.connect(self.updateThreshold)
        thresholdLayout.addWidget(self.thresholdSlider)
        gestureLayout.addLayout(thresholdLayout)
        
        # Current threshold value
        self.thresholdValueLabel = QLabel(f"Current: {self.gestureThreshold}")
        self.thresholdValueLabel.setAlignment(Qt.AlignCenter)
        gestureLayout.addWidget(self.thresholdValueLabel)
        
        # Gesture customize button
        self.customizeGesturesBtn = self.createStyledButton("Customize Gestures", "preferences-desktop-gesture")
        self.customizeGesturesBtn.clicked.connect(self.openGestureSettings)
        gestureLayout.addWidget(self.customizeGesturesBtn)
        
        gestureGroup.setLayout(gestureLayout)
        
        # Status area
        statusGroup = self.createControlGroup("Status", leftPanelLayout)
        statusLayout = QVBoxLayout()
        
        self.handStatusLabel = QLabel("Hand Detection: Not Active")
        self.handStatusLabel.setStyleSheet("font-size: 13px;")
        statusLayout.addWidget(self.handStatusLabel)
        
        self.gestureStatusLabel = QLabel("Current Gesture: None")
        self.gestureStatusLabel.setStyleSheet("font-size: 13px;")
        statusLayout.addWidget(self.gestureStatusLabel)
        
        self.slideLabel = QLabel("Current Slide: N/A")
        self.slideLabel.setStyleSheet("font-size: 13px;")
        statusLayout.addWidget(self.slideLabel)
        
        statusGroup.setLayout(statusLayout)
        
        # Add spacer to push controls to the top
        leftPanelLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Right panel - Preview
        rightPanel = QWidget()
        rightPanelLayout = QVBoxLayout(rightPanel)
        rightPanelLayout.setContentsMargins(5, 5, 5, 5)
        
        previewLabel = QLabel("Live Preview")
        previewLabel.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        previewLabel.setAlignment(Qt.AlignCenter)
        rightPanelLayout.addWidget(previewLabel)
        
        # Preview frame
        self.previewFrame = QFrame()
        self.previewFrame.setFrameShape(QFrame.StyledPanel)
        self.previewFrame.setStyleSheet("background-color: #1e1e1e; border-radius: 8px;")
        self.previewFrame.setMinimumSize(640, 480)
        
        previewLayout = QVBoxLayout(self.previewFrame)
        self.previewWidget = QLabel()
        self.previewWidget.setAlignment(Qt.AlignCenter)
        self.previewWidget.setStyleSheet("color: white; font-size: 16px;")
        self.previewWidget.setText("Camera preview will appear here\nwhen the camera is started")
        previewLayout.addWidget(self.previewWidget)
        
        rightPanelLayout.addWidget(self.previewFrame)
        
        # Add panels to splitter
        contentSplitter.addWidget(leftPanel)
        contentSplitter.addWidget(rightPanel)
        contentSplitter.setSizes([300, 700])  # Set initial sizes
        
        mainLayout.addWidget(contentSplitter)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready - Please select a presentation file and start the camera")
        
        # Initialize timer for video updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
    
    def populateCameraSources(self):
        """Populate the camera sources dropdown with available cameras"""
        try:
            self.cameraSelector.clear()
            available_cameras = []
            
            # Check first 5 camera indices
            for i in range(5):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Use DirectShow
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        available_cameras.append(i)
                    cap.release()
                    
            if available_cameras:
                for cam_id in available_cameras:
                    self.cameraSelector.addItem(f"Camera {cam_id}", cam_id)
            else:
                self.cameraSelector.addItem("No cameras found", -1)
                self.startCamBtn.setEnabled(False)
                
        except Exception as e:
            self.statusBar.showMessage(f"Error detecting cameras: {str(e)}")
            self.cameraSelector.addItem("Error detecting cameras", -1)
            self.startCamBtn.setEnabled(False)
    
    def openGestureSettings(self):
        """Open the gesture settings dialog"""
        dialog = GestureSettingsDialog(self.gestures, parent=self)
        if dialog.exec_():
            # Get new gesture settings
            new_gestures = dialog.getGestures()
            # Update gestures
            self.gestures = new_gestures
            # Save and update UI
            self.statusBar.showMessage("Gesture settings updated")
            
            # Update ML model if available
            if hasattr(self, 'ml_recognizer'):
                self.ml_recognizer.update_gestures(new_gestures)
                
            # Show current gesture mappings in status
            gesture_str = ", ".join([f"{k}: {''.join(map(str, v))}" for k, v in self.gestures.items()])
            self.gestureStatusLabel.setText(f"Gestures Updated: {gesture_str}")
            
    def createControlGroup(self, title, parentLayout):
        """Create a styled control group"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3498db;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
        """)
        parentLayout.addWidget(group)
        return group
    
    def createStyledButton(self, text, icon_name=None):
        """Create a styled button with optional icon"""
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        if icon_name:
            try:
                # Try to use system icon first
                icon = self.style().standardIcon(getattr(QStyle, f"SP_{icon_name.replace('-', '')}Icon"))
                button.setIcon(icon)
            except:
                try:
                    # Then try from assets folder
                    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           "assets", f"{icon_name}.png")
                    if os.path.exists(icon_path):
                        button.setIcon(QIcon(icon_path))
                except:
                    pass  # No icon, just use text
                
        return button
    
    def createMenuBar(self):
        menuBar = self.menuBar()
        menuBar.setStyleSheet("""
            QMenuBar {
                background-color: #2c3e50;
                color: white;
            }
            QMenuBar::item {
                background-color: transparent;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
            }
        """)
        
        # File menu
        fileMenu = menuBar.addMenu("File")
        fileMenu.setStyleSheet("QMenu { background-color: #2c3e50; color: white; }")
        
        openAction = QAction("Open Presentation", self)
        openAction.triggered.connect(self.selectPPTFile)
        
        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.close)
        
        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)
        
        # Settings menu
        settingsMenu = menuBar.addMenu("Settings")
        settingsMenu.setStyleSheet("QMenu { background-color: #2c3e50; color: white; }")
        
        customizeAction = QAction("Customize Gestures", self)
        customizeAction.triggered.connect(self.openGestureSettings)
        
        cameraAction = QAction("Camera Settings", self)
        cameraAction.triggered.connect(self.openCameraSettings)
        
        settingsMenu.addAction(customizeAction)
        settingsMenu.addAction(cameraAction)
        
        # Help menu
        helpMenu = menuBar.addMenu("Help")
        helpMenu.setStyleSheet("QMenu { background-color: #2c3e50; color: white; }")
        
        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.showAboutDialog)
        
        helpAction = QAction("User Guide", self)
        helpAction.triggered.connect(self.showHelp)
        
        helpMenu.addAction(helpAction)
        helpMenu.addAction(aboutAction)
    
    def toggleHandOnlyMode(self, checked):
        """Toggle between showing only hand landmarks or full camera feed"""
        self.hand_only_mode = checked
    
    def updateThreshold(self, value):
        """Update gesture threshold from slider"""
        self.gestureThreshold = value
        self.thresholdValueLabel.setText(f"Current: {value}")
    
    def prev_slide(self):
        """Navigate to previous slide"""
        if self.slide_images and self.current_slide_idx > 0:
            self.current_slide_idx -= 1
            self.drawing_helper.clear_annotations()
            self.displayCurrentSlide()
            self.updateSlideLabel()
    
    def next_slide(self):
        """Navigate to next slide"""
        if self.slide_images and self.current_slide_idx < len(self.slide_images) - 1:
            self.current_slide_idx += 1
            self.drawing_helper.clear_annotations()
            self.displayCurrentSlide()
            self.updateSlideLabel()
    
    def openCameraSettings(self):
        """Open camera settings dialog"""
        # Implement camera settings dialog
        QMessageBox.information(self, "Camera Settings", 
                               "Camera configuration options will be available in a future update.")
    
    def showHelp(self):
        """Show help documentation"""
        QMessageBox.information(self, "User Guide", 
                               """<h3>Gesture Control Guide</h3>
                               <p><b>Basic Gestures:</b></p>
                               <ul>
                                 <li>Thumb up: Previous slide</li>
                                 <li>Pinky up: Next slide</li>
                                 <li>Index finger up: Drawing mode</li>
                                 <li>Index + Middle fingers up: Pointer mode</li>
                                 <li>Index + Middle + Ring fingers up: Erase last annotation</li>
                               </ul>
                               <p>Gestures are recognized when your hand is above the threshold line.</p>
                               """)
    
    def selectPPTFile(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Select PowerPoint File", "", 
            "PowerPoint Files (*.ppt *.pptx);;All Files (*)", 
            options=options
        )
        
        if filePath:
            self.statusBar.showMessage(f"Loading presentation: {filePath}")
            self.openPowerPointFile(filePath)
            
    def openPowerPointFile(self, filePath):
        try:
            # Show loading indicator
            self.slideInfoLabel.setText("Converting presentation to images...\nThis may take a moment.")
            QApplication.processEvents()
            
            # Convert PPT to images
            self.slide_images = self.ppt_converter.convert_ppt_to_images(filePath)
            self.current_slide_idx = 0
            
            # Update UI
            self.prevSlideBtn.setEnabled(False)
            self.nextSlideBtn.setEnabled(len(self.slide_images) > 1)
            
            # Display first slide
            self.displayCurrentSlide()
            
            # Update info
            filename = os.path.basename(filePath)
            self.slideInfoLabel.setText(f"Presentation: {filename}\nTotal Slides: {len(self.slide_images)}")
            self.updateSlideLabel()
            
            # Update complexity info
            self.updateSlideComplexityInfo()
            
            self.statusBar.showMessage(f"Presentation loaded successfully: {len(self.slide_images)} slides")
        except Exception as e:
            self.slideInfoLabel.setText("Error loading presentation.\nPlease try again.")
            QMessageBox.critical(self, "Error", f"Failed to open PowerPoint file: {str(e)}")
    
    def updateSlideComplexityInfo(self):
        """Update slide complexity information using ML"""
        if self.slide_images and 0 <= self.current_slide_idx < len(self.slide_images):
            complexity = self.ppt_converter.get_slide_complexity(self.current_slide_idx)
            self.complexityLabel.setText(f"Slide Complexity: {complexity}")
            
            # Set color based on complexity
            if complexity == "Simple":
                self.complexityLabel.setStyleSheet("font-size: 12px; color: #27ae60;")
            elif complexity == "Moderate":
                self.complexityLabel.setStyleSheet("font-size: 12px; color: #f39c12;")
            elif complexity == "Complex":
                self.complexityLabel.setStyleSheet("font-size: 12px; color: #c0392b;")
            else:
                self.complexityLabel.setStyleSheet("font-size: 12px; color: #7f8c8d;")

    def displayCurrentSlide(self):
        if self.slide_images and 0 <= self.current_slide_idx < len(self.slide_images):
            try:
                # Load the current slide image
                self.current_slide_image = cv2.imread(self.slide_images[self.current_slide_idx])
                if self.current_slide_image is not None:
                    self.current_slide_image = cv2.resize(self.current_slide_image, (1280, 720))
                    self.updatePresentationWindow()
                    self.updateSlideComplexityInfo()
                    
                    # Enable/disable navigation buttons based on current position
                    self.prevSlideBtn.setEnabled(self.current_slide_idx > 0)
                    self.nextSlideBtn.setEnabled(self.current_slide_idx < len(self.slide_images) - 1)
            except Exception as e:
                self.statusBar.showMessage(f"Error displaying slide: {str(e)}")

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
    
    def updateFrame(self):
        try:
            if self.cap is None or not self.cap.isOpened():
                return
            
            success, img = self.cap.read()
            if not success:
                return

            img = cv2.flip(img, 1)
            
            try:
                hands, _ = self.detectorHand.findHands(img, draw=True)
                
                # Create display image based on mode
                if self.hand_only_mode:
                    display_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
                    
                    if hands:
                        self.handStatusLabel.setText(f"Hand Detection: Detected {len(hands)} hand(s)")
                        self.drawHandSkeleton(display_img, hands)
                    else:
                        self.handStatusLabel.setText("Hand Detection: No hands detected")
                else:
                    display_img = img

                # Draw threshold line
                cv2.line(display_img, (0, self.gestureThreshold), 
                        (self.width, self.gestureThreshold), (0, 255, 0), 2)
                
                # Convert to Qt format with error handling
                try:
                    h, w, ch = display_img.shape
                    bytes_per_line = ch * w
                    qt_img = QImage(display_img.data, w, h, bytes_per_line, QImage.Format_BGR888)
                    if not qt_img.isNull():
                        pixmap = QPixmap.fromImage(qt_img)
                        scaled_pixmap = pixmap.scaled(
                            self.previewWidget.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.previewWidget.setPixmap(scaled_pixmap)
                except Exception as e:
                    self.logger.error(f"Qt image conversion error: {str(e)}")
                
                # Process gestures
                if hands and not self.buttonPressed and self.slide_images:
                    self.processHandGestures(hands, display_img)
                else:
                    self.drawing_helper.stop_annotation()
                    
            except KeyError as ke:
                self.logger.error(f"KeyError in hand detection: {str(ke)}")
                self.handStatusLabel.setText("Hand Detection: Error processing hand data")

        except Exception as e:
            self.logger.error(f"Frame update error: {str(e)}")
    
    def drawHandSkeleton(self, canvas, hands):
        """Draw hand skeleton with connections"""
        for hand in hands:
            lmList = hand["lmList"]
            
            # Draw connections
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
                (0, 5), (5, 6), (6, 7), (7, 8),  # Index
                (5, 9), (9, 10), (10, 11), (11, 12),  # Middle
                (9, 13), (13, 14), (14, 15), (15, 16),  # Ring
                (13, 17), (17, 18), (18, 19), (19, 20),  # Pinky
                (0, 17), (0, 5), (5, 9), (9, 13), (13, 17)  # Palm
            ]
            
            for connection in connections:
                start = tuple(map(int, lmList[connection[0]][:2]))
                end = tuple(map(int, lmList[connection[1]][:2]))
                cv2.line(canvas, start, end, (255, 255, 255), 2)
            
            # Draw landmarks
            for point in lmList:
                cv2.circle(canvas, (int(point[0]), int(point[1])), 4, (0, 255, 0), -1)

    def processHandGestures(self, hands, img):
        try:
            if not hands:
                return

            hand = hands[0]
            cx, cy = hand["center"]
            lmList = hand["lmList"]
            fingers = self.detectorHand.fingersUp(hand)
            
            current_time = time.time()
            
            # Get ML gesture prediction
            ml_gesture = self.ml_recognizer.predict_gesture(lmList)
            
            # Update UI
            self.gestureStatusLabel.setText(f"Current Gesture: {ml_gesture} ({fingers})")
            
            # Process gestures if hand is above threshold and cooldown has passed
            if cy <= self.gestureThreshold and (current_time - self.last_gesture_time) >= self.gesture_cooldown:
                # Previous slide
                if fingers == [1, 0, 0, 0, 0] or ml_gesture == "previous_slide":
                    if self.current_slide_idx > 0:
                        self.prev_slide()
                        self.last_gesture_time = current_time
                        self.last_processed_gesture = "previous_slide"
                        self.statusBar.showMessage("Gesture: Previous Slide")
                
                # Next slide
                elif fingers == [0, 0, 0, 0, 1] or ml_gesture == "next_slide":
                    if self.current_slide_idx < len(self.slide_images) - 1:
                        self.next_slide()
                        self.last_gesture_time = current_time
                        self.last_processed_gesture = "next_slide"
                        self.statusBar.showMessage("Gesture: Next Slide")
            
            # Continuous gestures (no cooldown)
            # Drawing mode
            if fingers == [0, 1, 0, 0, 0] or ml_gesture == "draw":
                self.drawMode = True
                indexFinger = (int(lmList[8][0]), int(lmList[8][1]))
                self.drawing_helper.start_annotation(indexFinger)
                self.statusBar.showMessage("Mode: Drawing")
            else:
                self.drawMode = False
                self.drawing_helper.stop_annotation()
            
            # Pointer mode
            if fingers == [0, 1, 1, 0, 0] or ml_gesture == "pointer":
                indexFinger = (int(lmList[8][0]), int(lmList[8][1]))
                if self.current_slide_image is not None:
                    self.current_slide_image = self.current_slide_image.copy()
                    cv2.circle(self.current_slide_image, indexFinger, 10, (0, 0, 255), -1)
                    self.updatePresentationWindow()
                self.statusBar.showMessage("Mode: Pointer")
            
            # Erase last annotation
            if (fingers == [0, 1, 1, 1, 0] or ml_gesture == "erase") and \
               self.last_processed_gesture != "erase" and \
               (current_time - self.last_gesture_time) >= self.gesture_cooldown:
                self.drawing_helper.undo_last_annotation()
                self.updatePresentationWindow()
                self.last_gesture_time = current_time
                self.last_processed_gesture = "erase"
                self.statusBar.showMessage("Action: Erased last drawing")
            
            # Debug information
            debug_text = f"Fingers: {fingers}\nGesture: {ml_gesture}\nHeight: {cy}"
            cv2.putText(img, debug_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
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
            "About Gesture Digita",
            """<h3>Gesture Digita</h3>
            <p>Version 1.0</p>
            <p>An advanced gesture-based presentation control system that allows you to control 
            PowerPoint presentations using natural hand gestures.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Intuitive gesture controls</li>
                <li>AI-powered gesture recognition</li>
                <li>Real-time hand tracking</li>
                <li>Drawing and annotation tools</li>
            </ul>
            <p>&copy; 2024 Gesture Digita. All rights reserved.</p>"""
        )

    def startCamera(self):
        """Start camera capture"""
        try:
            camera_id = self.cameraSelector.currentData()
            if camera_id == -1:
                QMessageBox.warning(self, "Warning", "No camera selected or available")
                return
                
            self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
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
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error starting camera: {str(e)}")
            self.statusBar.showMessage(f"Camera error: {str(e)}")
    
    def stopCamera(self):
        """Stop camera capture"""
        try:
            if self.cap and self.cap.isOpened():
                self.timer.stop()
                self.cap.release()
                
            self.cap = None
            self.current_frame = None
            self.previewWidget.setText("Camera preview will appear here\nwhen the camera is started")
            self.startCamBtn.setEnabled(True)
            self.stopCamBtn.setEnabled(False)
            self.cameraSelector.setEnabled(True)
            self.handStatusLabel.setText("Hand Detection: Not Active")
            self.statusBar.showMessage("Camera stopped")
            
            # Destroy camera window if it exists
            cv2.destroyWindow("Hand Tracking")
            
        except Exception as e:
            self.statusBar.showMessage(f"Error stopping camera: {str(e)}")
    
    def updateSlideLabel(self):
        """Update the slide label with current slide number and total slides"""
        if self.slide_images:
            total_slides = len(self.slide_images)
            current = self.current_slide_idx + 1
            self.slideLabel.setText(f"Current Slide: {current}/{total_slides}")
            
            # Update navigation button states
            self.prevSlideBtn.setEnabled(self.current_slide_idx > 0)
            self.nextSlideBtn.setEnabled(self.current_slide_idx < total_slides - 1)
        else:
            self.slideLabel.setText("Current Slide: N/A")
            self.prevSlideBtn.setEnabled(False)
            self.nextSlideBtn.setEnabled(False)

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