import os
import logging
from datetime import datetime

def setup_environment():
    """Setup environment variables to suppress warnings and errors"""
    # Suppress TensorFlow logging and warnings
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
    
    # Suppress OpenCV warnings more aggressively
    os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
    os.environ["OPENCV_VIDEOIO_DEBUG"] = "0"
    os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
    
    # Disable MediaPipe logging completely
    os.environ["GLOG_minloglevel"] = "2"
    os.environ["MEDIAPIPE_DISABLE_GPU"] = "1"
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    
    # Disable MediaPipe feedback manager warnings
    try:
        import absl.logging
        absl.logging.set_verbosity(absl.logging.ERROR)
    except ImportError:
        pass

def setup_logging(log_file=None):
    """Setup logging for the application"""
    if log_file is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"app_log_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger('gesture_app')
    return logger

def log_system_info():
    """Log system information that might be useful for debugging"""
    logger = logging.getLogger('gesture_app')
    
    try:
        import cv2
        logger.info(f"OpenCV Version: {cv2.__version__}")
    except:
        logger.warning("OpenCV not found or version could not be determined")
    
    try:
        import numpy
        logger.info(f"NumPy Version: {numpy.__version__}")
    except:
        logger.warning("NumPy not found or version could not be determined")
    
    try:
        from PyQt5.Qt import PYQT_VERSION_STR
        logger.info(f"PyQt5 Version: {PYQT_VERSION_STR}")
    except:
        logger.warning("PyQt5 not found or version could not be determined")
    
    # Log system info
    import platform
    logger.info(f"Python Version: {platform.python_version()}")
    logger.info(f"Platform: {platform.platform()}")
