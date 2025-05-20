import os
import win32com.client
import logging
import tempfile
from pathlib import Path
import cv2
import pythoncom
import time

class PPTConverter:
    def __init__(self):
        self.logger = logging.getLogger('gesture_app')
        self.presentation_folder = None
        self.slide_images = []

    def convert_ppt_to_images(self, ppt_path):
        """Convert PowerPoint slides to images using COM automation"""
        try:
            # Initialize COM in this thread
            pythoncom.CoInitialize()
            
            # Create presentation folder
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.presentation_folder = os.path.join(base_dir, "Presentation")
            os.makedirs(self.presentation_folder, exist_ok=True)
            
            # Clear existing files
            for file in os.listdir(self.presentation_folder):
                if file.endswith('.png'):
                    os.remove(os.path.join(self.presentation_folder, file))
            
            # Initialize PowerPoint
            powerpoint = win32com.client.Dispatch("PowerPoint.Application")
            powerpoint.DisplayAlerts = False
            
            # Open presentation without trying to set visibility
            abs_path = str(Path(ppt_path).resolve())
            presentation = powerpoint.Presentations.Open(abs_path, ReadOnly=True, Untitled=False, WithWindow=False)
            
            # Export slides one by one
            total_slides = presentation.Slides.Count
            for i in range(1, total_slides + 1):
                image_path = os.path.join(self.presentation_folder, f"slide_{i:03d}.png")
                try:
                    slide = presentation.Slides(i)
                    slide.Export(image_path, "PNG", 1280, 720)
                    if os.path.exists(image_path):
                        self.slide_images.append(image_path)
                    # Add small delay to prevent automation issues
                    time.sleep(0.1)
                except Exception as e:
                    self.logger.warning(f"Failed to export slide {i}: {str(e)}")
            
            # Cleanup
            try:
                presentation.Close()
                powerpoint.Quit()
            except:
                pass
            
            # Sort images by name
            self.slide_images.sort()
            
            # Uninitialize COM
            pythoncom.CoUninitialize()
            
            if not self.slide_images:
                raise Exception("No slides were exported successfully")
                
            return self.slide_images
            
        except Exception as e:
            self.logger.error(f"Error converting PPT to images: {str(e)}")
            # Ensure COM is uninitialized
            try:
                pythoncom.CoUninitialize()
            except:
                pass
            raise e
        
    def cleanup(self):
        """Clean up presentation folder"""
        if self.presentation_folder and os.path.exists(self.presentation_folder):
            for image in self.slide_images:
                try:
                    if os.path.exists(image):
                        os.remove(image)
                except Exception as e:
                    self.logger.warning(f"Error removing file {image}: {str(e)}")
            
            try:
                if not os.listdir(self.presentation_folder):
                    os.rmdir(self.presentation_folder)
            except Exception as e:
                self.logger.warning(f"Error removing presentation directory: {str(e)}")
            
        self.slide_images = []
        self.presentation_folder = None
