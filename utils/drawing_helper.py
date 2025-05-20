import cv2
import numpy as np

class DrawingHelper:
    def __init__(self):
        self.annotations = [[]]
        self.annotation_number = -1
        self.annotation_start = False
        
    def start_annotation(self, point):
        if not self.annotation_start:
            self.annotation_start = True
            self.annotation_number += 1
            self.annotations.append([])
        self.annotations[self.annotation_number].append(point)
        
    def stop_annotation(self):
        self.annotation_start = False
        
    def undo_last_annotation(self):
        if self.annotations:
            self.annotations.pop(-1)
            self.annotation_number -= 1
            
    def clear_annotations(self):
        self.annotations = [[]]
        self.annotation_number = -1
        self.annotation_start = False
        
    def draw_annotations(self, img, color=(0, 0, 200), thickness=12):
        for annotation in self.annotations:
            for j in range(1, len(annotation)):
                cv2.line(img, annotation[j - 1], annotation[j], color, thickness)
        return img
