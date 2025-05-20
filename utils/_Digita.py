import math
import numpy as np

import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self, staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.8, minTrackCon=0.8):

        self.staticMode = staticMode
        self.maxHands = maxHands
        self.modelComplexity = modelComplexity
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.staticMode,
            max_num_hands=self.maxHands,
            model_complexity=1,  # Use more complex model
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.minTrackCon)

        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.fingers = []
        self.lmList = []

        # Add smoothing parameters
        self.smoothening = 0.1
        self.prev_landmarks = None

    def findHands(self, img, draw=True, flipType=True):
        """
        Enhanced hand detection with smoothing
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        allHands = []
        h, w, c = img.shape
        if self.results.multi_hand_landmarks:
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {}
                mylmList = []
                xList = []
                yList = []

                # Apply smoothing to landmarks
                if self.prev_landmarks is not None:
                    for i, lm in enumerate(handLms.landmark):
                        prev_lm = self.prev_landmarks[i]
                        lm.x = prev_lm[0] * self.smoothening + lm.x * (1 - self.smoothening)
                        lm.y = prev_lm[1] * self.smoothening + lm.y * (1 - self.smoothening)
                        lm.z = prev_lm[2] * self.smoothening + lm.z * (1 - self.smoothening)

                # Store current landmarks for next frame
                self.prev_landmarks = [(lm.x, lm.y, lm.z) for lm in handLms.landmark]

                # Process landmarks with improved precision
                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = float(lm.x * w), float(lm.y * h), float(lm.z * w)
                    mylmList.append([int(px), int(py), pz])
                    xList.append(px)
                    yList.append(py)

                # Calculate bounding box with padding
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin - 20, ymin - 20, boxW + 40, boxH + 40
                cx, cy = bbox[0] + (bbox[2] // 2), bbox[1] + (bbox[3] // 2)

                myHand["lmList"] = mylmList
                myHand["bbox"] = bbox
                myHand["center"] = (int(cx), int(cy))
                myHand["confidence"] = handType.classification[0].score

                # Only include hands with high confidence
                if myHand["confidence"] > 0.8:
                    if flipType:
                        if handType.classification[0].label == "Right":
                            myHand["type"] = "Left"
                        else:
                            myHand["type"] = "Right"
                    else:
                        myHand["type"] = handType.classification[0].label
                    allHands.append(myHand)

                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS,
                                               self.mpDraw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                               self.mpDraw.DrawingSpec(color=(0, 0, 255), thickness=2))

                    cv2.rectangle(img, (int(bbox[0]), int(bbox[1])),
                                  (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])),
                                  (0, 255, 0), 2)

                    cv2.putText(img, f"{myHand['type']} ({myHand['confidence']:.2f})",
                                (int(bbox[0]), int(bbox[1] - 30)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        return allHands, img

    def fingersUp(self, myHand):
        """
        Enhanced finger detection with improved angle calculation
        """
        fingers = []
        myHandType = myHand["type"]
        myLmList = myHand["lmList"]

        def calculate_angle(a, b, c):
            a = np.array([myLmList[a][0], myLmList[a][1]])
            b = np.array([myLmList[b][0], myLmList[b][1]])
            c = np.array([myLmList[c][0], myLmList[c][1]])

            ba = a - b
            bc = c - b

            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(cosine_angle)

            return np.degrees(angle)

        # Improved thumb detection using angle
        if myHandType == "Right":
            angle = calculate_angle(4, 3, 2)
            fingers.append(1 if angle > 150 else 0)
        else:
            angle = calculate_angle(4, 3, 2)
            fingers.append(1 if angle > 150 else 0)

        # Improved finger detection using angles
        for id in range(1, 5):
            angle = calculate_angle(self.tipIds[id], self.tipIds[id] - 2, self.tipIds[id] - 3)
            fingers.append(1 if angle > 160 else 0)

        return fingers

    def findDistance(self, p1, p2, img=None, color=(255, 0, 255), scale=5):
        """
        Find the distance between two landmarks input should be (x1,y1) (x2,y2)
        :param p1: Point1 (x1,y1)
        :param p2: Point2 (x2,y2)
        :param img: Image to draw output on. If no image input output img is None
        :return: Distance between the points
                 Image with output drawn
                 Line information
        """

        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), scale, color, cv2.FILLED)
            cv2.circle(img, (x2, y2), scale, color, cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), color, max(1, scale // 3))
            cv2.circle(img, (cx, cy), scale, color, cv2.FILLED)

        return length, info, img


def main():
    # Initialize the webcam to capture video
    # The '2' indicates the third camera connected to your computer; '0' would usually refer to the built-in camera
    cap = cv2.VideoCapture(0)

    # Initialize the HandDetector class with the given parameters
    detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

    # Continuously get frames from the webcam
    while True:
        # Capture each frame from the webcam
        # 'success' will be True if the frame is successfully captured, 'img' will contain the frame
        success, img = cap.read()

        # Find hands in the current frame
        # The 'draw' parameter draws landmarks and hand outlines on the image if set to True
        # The 'flipType' parameter flips the image, making it easier for some detections
        hands, img = detector.findHands(img, draw=True, flipType=True)

        # Check if any hands are detected
        if hands:
            # Information for the first hand detected
            hand1 = hands[0]  # Get the first hand detected
            lmList1 = hand1["lmList"]  # List of 21 landmarks for the first hand
            bbox1 = hand1["bbox"]  # Bounding box around the first hand (x,y,w,h coordinates)
            center1 = hand1['center']  # Center coordinates of the first hand
            handType1 = hand1["type"]  # Type of the first hand ("Left" or "Right")

            # Count the number of fingers up for the first hand
            fingers1 = detector.fingersUp(hand1)
            print(f'H1 = {fingers1.count(1)}', end=" ")  # Print the count of fingers that are up

            # Calculate distance between specific landmarks on the first hand and draw it on the image
            length, info, img = detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], img, color=(255, 0, 255),
                                                      scale=10)

            # Check if a second hand is detected
            if len(hands) == 2:
                # Information for the second hand
                hand2 = hands[1]
                lmList2 = hand2["lmList"]
                bbox2 = hand2["bbox"]
                center2 = hand2['center']
                handType2 = hand2["type"]

                # Count the number of fingers up for the second hand
                fingers2 = detector.fingersUp(hand2)
                print(f'H2 = {fingers2.count(1)}', end=" ")

                # Calculate distance between the index fingers of both hands and draw it on the image
                length, info, img = detector.findDistance(lmList1[8][0:2], lmList2[8][0:2], img, color=(255, 0, 0),
                                                          scale=10)

            print(" ")  # New line for better readability of the printed output

        # Display the image in a window if it's not None
        if img is not None:
            cv2.imshow("Image", img)

        # Keep the window open and update it for each frame; wait for 1 millisecond between frames
        cv2.waitKey(1)


if __name__ == "__main__":
    main()