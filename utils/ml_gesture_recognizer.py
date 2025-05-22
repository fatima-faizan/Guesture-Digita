import numpy as np
import cv2
import tensorflow as tf
import os
import logging
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class MLGestureRecognizer:
    def __init__(self, model_path=None):
        self.logger = logging.getLogger('gesture_app')
        
        self.model = None
        self.gesture_names = [
            "previous_slide",  # Thumb up
            "next_slide",      # Pinky up
            "pointer",         # Index and middle up
            "draw",            # Index up
            "erase",           # Index, middle, and ring up
            "none"             # No gesture
        ]
   
        
        # Fixed number of samples
        n_landmarks = 21
        n_features = n_landmarks * 3
        samples_per_gesture = 10
        n_gestures = len(self.gesture_names) - 1  # Excluding 'none'
        total_samples = samples_per_gesture * n_gestures
        
        # Initialize training data arrays with correct sizes
        self.training_data = np.zeros((total_samples, n_features))
        self.training_labels = np.zeros(total_samples, dtype=int)
        
        # Generate base gestures
        base_gestures = {
            "previous_slide": [1] + [0]*19,  # Thumb up
            "next_slide": [0]*19 + [1],      # Pinky up
            "pointer": [0,0,1,1] + [0]*16,   # Index + Middle up
            "draw": [0,1] + [0]*18,          # Index up
            "erase": [0,1,1,1] + [0]*16,     # Index + Middle + Ring up
        }
        
        # Create training samples with consistent indexing
        for i, gesture_name in enumerate(self.gesture_names[:-1]):  # Exclude 'none'
            base = base_gestures.get(gesture_name, [0]*20)
            for j in range(samples_per_gesture):
                idx = i * samples_per_gesture + j
                sample = np.zeros(n_features)
                
                # Set coordinates for active fingers
                for k, val in enumerate(base):
                    if val:
                        # Add slight variations for robustness
                        sample[k*3:(k+1)*3] = [
                            0.5 + np.random.normal(0, 0.1),
                            0.8 + np.random.normal(0, 0.1),
                            0.0 + np.random.normal(0, 0.1)
                        ]
                
                self.training_data[idx] = sample
                self.training_labels[idx] = i
        
        # Ensure model is always initialized
        if not self.model or not hasattr(self.model, 'estimators_'):
            # Train model with the generated data
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=4,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(self.training_data, self.training_labels)
        
        # Set parameters for prediction
        self.confidence_threshold = 0.3  # Lower threshold for better detection
        self.gesture_history = []
        self.history_size = 5  # Increase history size
        self.prev_gesture = "none"
    
        # Save newly trained model
        if model_path:
            self.save_model(model_path)
    
    def update_gestures(self, new_gestures):
        """Update the gesture mappings used by the recognizer"""
        self.gestures = new_gestures
    
    def preprocess_landmarks(self, landmarks):
        """Improved landmark processing"""
        if not landmarks or len(landmarks) < 21:
            return None
            
        try:
            # Extract coordinates and normalize
            coords = []
            base_x, base_y = landmarks[0][0], landmarks[0][1]  # Use wrist as reference
            
            for lm in landmarks:
                # Normalize coordinates relative to wrist
                x = (lm[0] - base_x) / 640  # Normalize by image width
                y = (lm[1] - base_y) / 480  # Normalize by image height
                z = lm[2] if len(lm) > 2 else 0.0
                coords.extend([x, y, z])
            
            # Ensure consistent feature length
            if len(coords) > 63:  # 21 landmarks * 3 coordinates
                coords = coords[:63]
            elif len(coords) < 63:
                coords.extend([0.0] * (63 - len(coords)))
            
            return coords
            
        except Exception as e:
            self.logger.error(f"Landmark preprocessing error: {str(e)}")
            return None

    def predict_gesture(self, landmarks):
        """Improved gesture prediction"""
        try:
            features = self.preprocess_landmarks(landmarks)
            if not features:
                return "none"

            # Reshape and predict
            features = np.array(features).reshape(1, -1)
            probas = self.model.predict_proba(features)[0] # type: ignore
            prediction_idx = np.argmax(probas)
            confidence = probas[prediction_idx]
            
            # Get current prediction
            current_pred = self.gesture_names[prediction_idx]
            
            # Apply temporal smoothing
            if confidence < self.confidence_threshold:
                current_pred = "none"
            
            # Use previous gesture if confidence is close
            if confidence < 0.4 and self.prev_gesture != "none":
                current_pred = self.prev_gesture
            
            # Update previous gesture
            self.prev_gesture = current_pred
            
            return current_pred
            
        except Exception as e:
            self.logger.error(f"Prediction error: {str(e)}")
            return "none"
            
    def train_model(self, training_data, labels):
        """Train the model with labeled data"""
        try:
            # Ensure model is initialized
            if self.model is None:
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
                
            # Split data into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(
                training_data, labels, test_size=0.2, random_state=42
            )
            
            # Train the model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            predictions = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            self.logger.info(f"Model trained with accuracy: {accuracy:.4f}")
            return accuracy
        except Exception as e:
            self.logger.error(f"Training error: {str(e)}")
            return 0.0
    
    def save_model(self, path):
        """Save the trained model to a file"""
        if not self.model:
            return False
            
        try:
            with open(path, 'wb') as f:
                pickle.dump(self.model, f)
            self.logger.info(f"Model saved to {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, path):
        """Load a trained model from a file"""
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            self.logger.info(f"Model loaded from {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            return False
            
    def collect_training_example(self, landmarks, gesture_index):
        """Collect a training example for a specific gesture"""
        features = self.preprocess_landmarks(landmarks)
        if features:
            return features, gesture_index
        return None, None
