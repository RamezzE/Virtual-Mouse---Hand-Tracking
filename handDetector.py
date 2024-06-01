import mediapipe as mp
import cv2
import math

FIST_CLOSED = 0
HAND_OPEN = 1
INDEX_MIDDLE_THUMB_EXTENDED = 2
INDEX_THUMB_EXTENDED = 3
INDEX_MIDDLE_EXTENDED = 4
INDEX_EXTENDED = 5
PINCH = 6
THUMB_EXTENDED = 7
SCISSORS = 8

class HandDetector:
    WRIST = 0
    THUMB = 4
    INDEX = 8
    MIDDLE = 12
    RING = 16
    PINKY = 20
    
    # Constructor
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.mpHandsDetector = self.mpHands.Hands(min_detection_confidence = 0.75, min_tracking_confidence = 0.1, max_num_hands = 1)
        self.mpDraw = mp.solutions.drawing_utils
                        
    def findHands(self, img, drawConnections = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        self.imgHeight, self.imgWidth, _ = img.shape
        self.results = self.mpHandsDetector.process(imgRGB)
        self.hands = self.results.multi_hand_landmarks
        
        if drawConnections:
            if not self.hands:
                return img
            
            for hand in self.hands:
                self.mpDraw.draw_landmarks(img, hand, self.mpHands.HAND_CONNECTIONS)
            
        return img
    
    
    def highlightFingers(self, img, fingers = [THUMB, INDEX, MIDDLE, RING, PINKY]):
        if not self.hands:
            return img
        
        for hand in self.hands:
            landmarks = hand.landmark
      
            for id, landmark in enumerate(landmarks):
                if id not in fingers:
                    continue
                
                x = int(landmark.x * self.imgWidth)
                y = int(landmark.y * self.imgHeight)
                cv2.circle(img = img, center = (x, y), radius = 10, color = (255, 0, 0), thickness = cv2.FILLED)
                
        return img
    
    def highlightGesture(self, img, gesture):
        if not self.hands:
            return img
        
        # switch case 
        
        if gesture == FIST_CLOSED or gesture == HAND_OPEN:
            fingers = [self.THUMB, self.INDEX, self.MIDDLE, self.RING, self.PINKY]
        elif gesture == INDEX_MIDDLE_THUMB_EXTENDED:
            fingers = [self.INDEX, self.MIDDLE, self.THUMB]
        elif gesture == INDEX_THUMB_EXTENDED:
            fingers = [self.INDEX, self.THUMB]
        elif gesture == INDEX_MIDDLE_EXTENDED:
            fingers = [self.INDEX, self.MIDDLE]
        elif gesture == INDEX_EXTENDED:
            fingers = [self.INDEX]
        elif gesture == PINCH:
            fingers = [self.INDEX, self.THUMB]
        elif gesture == THUMB_EXTENDED:
            fingers = [self.THUMB]
        else:
            fingers = [self.INDEX, self.MIDDLE]
        
        return self.highlightFingers(img, fingers)
    
    def getFingerPosition(self, fingerId, hand = 0):
        landmarks = self.getLandmarks(hand)
        if landmarks and fingerId < len(landmarks):
            finger = landmarks[fingerId]
            x = int(finger.x * self.imgWidth)
            y = int(finger.y * self.imgHeight)
            
            return x, y
        return None, None

    
    def getLandmarks(self, hand = 0):
        try:
            if self.hands and hand < len(self.hands):
                return self.hands[hand].landmark
            return None
        except:
            return None
    
    def getFingersUp(self, hand = 0):
        if not self.hands:
            return None
        
        handType = self.results.multi_handedness[hand].classification[0].label
        lmList = self.getLandmarks(hand)
        
        fingersUp = []
                
        # Thumb
        # if handType == "Right":
        if handType == "Left":
            if lmList[self.THUMB].x > lmList[self.THUMB - 1].x:
                fingersUp.append(1)
            else:
                fingersUp.append(0)
        else:
            if lmList[self.THUMB].x < lmList[self.THUMB - 1].x:
                fingersUp.append(1)
            else:
                fingersUp.append(0)

        for fingerId in [self.INDEX, self.MIDDLE, self.RING, self.PINKY]:
            if lmList[fingerId].y < lmList[fingerId - 2].y:
                fingersUp.append(1)
            else:
                fingersUp.append(0)
        
        return fingersUp
    
    def isFingerOnlyUp(self, finger, hand = 0):
        fingers = self.getFingersUp(hand)
        if not fingers:
            return False
        
        return sum (fingers) == 1 and fingers[int(finger / 4) -1] == 1
    
    def isFistClosed(self, hand = 0):
        fingers = self.getFingersUp(hand)
        if not fingers:
            return None
        
        return sum(fingers) == 0
    
    def getDistance(self, f1, f2, img = None, color = (255, 0, 255), scale = 5, draw = True):
        x1, y1 = self.getFingerPosition(f1)
        x2, y2 = self.getFingerPosition(f2)
        
        if x1 is None or x2 is None or y1 is None or y2 is None:
            return None, img
        
        distance = math.hypot(x2 - x1, y2 - y1)
        
        if img is not None:
            cv2.circle(img, (x1, y1), scale, color, cv2.FILLED)
            cv2.circle(img, (x2, y2), scale, color, cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), color, max(1, scale // 3))
            # cv2.circle(img, (cx, cy), scale, color, cv2.FILLED)

        return distance, img

    def isDistanceWithin(self, f1, f2, distance = 25):
        dist, _ = self.getDistance(f1, f2)
        return dist is not None and dist < distance
    