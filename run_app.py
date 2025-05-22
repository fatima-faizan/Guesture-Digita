import sys
import os

# Add path to utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import debug helper functions and set environment variables
from utils.debug_helper import setup_environment, setup_logging, log_system_info

if __name__ == "__main__":
    # Setup environment variables first (before other imports)
    setup_environment()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Gesture Digita application")
    
    # Log system information
    log_system_info()
  
    
    try:
        # Import and run the main application
        from main import GestureControlApp
        from PyQt5.QtWidgets import QApplication, QMessageBox
        from PyQt5.QtCore import Qt
        
        logger.info("Initializing Qt application")
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        
        app = QApplication(sys.argv)
        try:
            window = GestureControlApp()
            window.show()
        except AttributeError as ae:
            logger.error(f"Initialization error: {str(ae)}")
            QMessageBox.critical(None, "Error", f"Failed to initialize application: {str(ae)}")
            sys.exit(1)
        
        logger.info("Application window displayed")
        sys.exit(app.exec_())
    except Exception as e:
        logger.exception(f"Error running application: {str(e)}")
        print(f"Error: {str(e)}")
        input("Press Enter to exit...")
