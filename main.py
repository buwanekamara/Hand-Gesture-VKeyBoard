import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep, time
import numpy as np
import cvzone
from pynput.keyboard import Controller
import os
from datetime import datetime

# Create a folder for saving files if it doesn't exist
if not os.path.exists("typed_texts"):
    os.makedirs("typed_texts")

# initializing the video capture
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # width of the video capture 
cap.set(4, 720)   # height of the video capture

detector = HandDetector(detectionCon=.8, maxHands=2)

keys = [["Q","W","E","R","T","Y","U","I","O","P"],
        ["A","S","D","F","G","H","J","K","L",";"],
        ["Z","X","C","V","B","N","M",",",".","/"],
        ["SAVE", " ", "CLEAR"]]  # Added SAVE and CLEAR buttons
finalText = ""

keyboard = Controller()

class Button():
    def __init__(self, pos, text, size=[60, 60]):
        self.pos = pos
        self.size = size
        self.text = text

buttonList = []

# Update button positions with new special buttons
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == " ":
            buttonList.append(Button([80 * j + 100, 80 * i + 200], key, [300, 60]))
        elif key in ["SAVE", "CLEAR"]:
            buttonList.append(Button([80 * j + 100, 80 * i + 200], key, [100, 60]))
        else:
            buttonList.append(Button([80 * j + 100, 80 * i + 200], key))

def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (x, y, w, h), 20, rt=0)
        
        # Different colors for special buttons
        if button.text == "SAVE":
            color = (0, 255, 0)  # Green for save
        elif button.text == "CLEAR":
            color = (0, 0, 255)  # Red for clear
        else:
            color = (0, 0, 0)    # Black for regular keys
            
        cv2.rectangle(img, (x, y), (x + w, y + h), color, cv2.FILLED)
        cv2.putText(img, button.text, (x + 15, y + 45), 
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
    return img

def save_text_to_file(text):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"typed_texts/typed_text_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(text)
    return filename

# Initialize last click time for debouncing
last_click_time = time()
CLICK_DELAY = 0.3  # Increased delay to 0.3 seconds

while True:
    try:
        success, img = cap.read()
        if not success:
            print("Failed to capture frame")
            continue
            
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img)
        img = drawAll(img, buttonList)

        if hands:
            hand1 = hands[0]
            lmList1 = hand1["lmList"]

            for button in buttonList:
                x, y = button.pos
                w, h = button.size

                if x < lmList1[8][0] < x+w and y < lmList1[8][1] < y+h:
                    cv2.rectangle(img, button.pos, (x+w, y+h), (175,0,175), cv2.FILLED)
                    cv2.putText(img, button.text, (x+20,y+65), 
                              cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                    # Check for pinch between any two fingers
                    fingers = []
                    # Check thumb with all fingers
                    for id in [8, 12, 16, 20]:  # Index, middle, ring, pinky
                        result = detector.findDistance((lmList1[4][0], lmList1[4][1]),
                                                   (lmList1[id][0], lmList1[id][1]), img)
                        if result[0] < 30:  # If distance is less than 30
                            fingers.append(True)
                        else:
                            fingers.append(False)

                    current_time = time()
                    if any(fingers) and (current_time - last_click_time) > CLICK_DELAY:
                        if button.text == "SAVE":
                            if finalText:
                                filename = save_text_to_file(finalText)
                                print(f"Saved to {filename}")
                                # Show save confirmation on screen
                                cv2.putText(img, "Saved!", (500, 50), 
                                          cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                        elif button.text == "CLEAR":
                            finalText = ""
                        else:
                            keyboard.press(button.text)
                            finalText += button.text
                            
                        last_click_time = current_time
                        sleep(0.3)  # Added delay after each action

        cv2.rectangle(img, (150, 50), (1000, 150), (0,0,0), cv2.FILLED)
        cv2.putText(img, finalText, (160, 130), 
                    cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

        cv2.imshow("Image", img)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    except Exception as e:
        print(f"Error occurred: {e}")
        continue

cap.release()
cv2.destroyAllWindows()