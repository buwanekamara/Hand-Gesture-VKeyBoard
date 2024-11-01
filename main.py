import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Controller

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set width of video capture
cap.set(4, 720)   # Set height of video capture

# Initialize hand detector with higher confidence threshold for stability
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Define keyboard layout
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["BACK", " ", "CLOSE"]]  # Added BACK and CLOSE options

finalText = ""
keyboard = Controller()

# Time delay to prevent multiple clicks
CLICK_DELAY = 0.3  # Increased delay to reduce multiple inputs
last_click_time = 0

class Button():
    def __init__(self, pos, text, size=[65, 65]):  # Slightly larger buttons for better visibility
        self.pos = pos
        self.size = size
        self.text = text

# Create button list with updated positions
buttonList = []
keyboard_x = 300  # Moved keyboard position to center
keyboard_y = 150  # Moved keyboard higher on screen

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == " ":
            buttonList.append(Button([keyboard_x + 85 * j, keyboard_y + 85 * i], key, [200, 65]))
        elif key in ["BACK", "CLOSE"]:
            buttonList.append(Button([keyboard_x + 85 * j, keyboard_y + 85 * i], key, [100, 65]))
        else:
            buttonList.append(Button([keyboard_x + 85 * j, keyboard_y + 85 * i], key))

def drawAll(img, buttonList):
    # Add keyboard background with lighting effect
    keyboard_bg = np.zeros((720, 1280, 3), np.uint8)
    cv2.rectangle(keyboard_bg, (keyboard_x-50, keyboard_y-50), 
                 (keyboard_x + 900, keyboard_y + 350), (30, 30, 50), cv2.FILLED)
    img = cv2.addWeighted(img, 1, keyboard_bg, 0.3, 0)

    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        
        # Add button lighting effect
        cv2.rectangle(img, (x-2, y-2), (x + w + 2, y + h + 2), (255, 255, 255), 1)
        cv2.rectangle(img, (x, y), (x + w, y + h), (50, 50, 50), cv2.FILLED)
        cv2.putText(img, button.text, (x + 15, y + 45), 
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
    return img

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)
    img = drawAll(img, buttonList)

    if hands:
        hand1 = hands[0]
        lmList1 = hand1["lmList"]
        fingers1 = detector.fingersUp(hand1)  # Get fingers status

        # Check for fist gesture (all fingers down)
        if sum(fingers1) == 0:  # If all fingers are down (fist)
            break  # Close the application

        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < lmList1[8][0] < x+w and y < lmList1[8][1] < y+h:
                cv2.rectangle(img, button.pos, (x+w, y+h), (175,0,175), cv2.FILLED)
                cv2.putText(img, button.text, (x+20,y+65), 
                           cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                l = detector.findDistance((lmList1[8][0], lmList1[8][1]), 
                                       (lmList1[4][0], lmList1[4][1]), img)[0]

                # Check if enough time has passed since last click
                if l < 30 and (time.time() - last_click_time) > CLICK_DELAY:
                    if button.text == "BACK":
                        finalText = finalText[:-1]  # Remove last character
                    elif button.text == "CLOSE":
                        break
                    else:
                        keyboard.press(button.text)
                        finalText += button.text
                    
                    last_click_time = time.time()  # Update last click time
                    cv2.rectangle(img, button.pos, (x+w, y+h), (0,255,0), cv2.FILLED)
                    cv2.putText(img, button.text, (x+20,y+65), 
                              cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    # Draw text display area with background
    cv2.rectangle(img, (150, 50), (1100, 150), (50, 50, 50), cv2.FILLED)
    cv2.rectangle(img, (148, 48), (1102, 152), (255, 255, 255), 1)  # Border
    cv2.putText(img, finalText, (160, 130), 
                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Virtual Keyboard", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()