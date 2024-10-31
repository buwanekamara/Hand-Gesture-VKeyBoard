# Importing Modules
import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Controller

# initializing the video capture
cap = cv2.VideoCapture(0)
cap.set(3, 1280) # width of the video capture 
cap.set(4, 720) # height of the video capture

detector = HandDetector(detectionCon=.8, maxHands=2)

keys = [["Q","W","E","R","T","Y","U","I","O","P"],
        ["A","S","D","F","G","H","J","K","L",";"],
        ["Z","X","C","V","B","N","M",",",".","/"],
        [" "]]
finalText = ""

keyboard = Controller()

# class Button():
#     def __init__(self, pos, text, size=[80,80]):
#         self.pos = pos
#         self.size = size
#         self.text = text

# buttonList = []

# for i in range(len(keys)):
#         for j, key in enumerate(keys[i]):
#             if key == " ":
#                 buttonList.append(Button([100*j+150, 100*i+250], key, [400,80]))
#             else:
#                 buttonList.append(Button([100*j+150, 100*i+250], key))

# def drawAll(img, buttonList):
#     for button in buttonList:
#         x, y = button.pos
#         w, h = button.size
#         cvzone.cornerRect(img, (button.pos[0], button.pos[1], button.size[0],button.size[0]), 20 ,rt=0)
#         cv2.rectangle(img, button.pos, (x+w, y+h), (0,0,0), cv2.FILLED)
#         cv2.putText(img, button.text, (x+20, y+80), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
#     return img

# Modify the Button class to use a smaller default size
class Button():
    def __init__(self, pos, text, size=[60, 60]):  # Reduced size from [80, 80] to [60, 60]
        self.pos = pos
        self.size = size
        self.text = text

buttonList = []

# Update button positions and spacing to fit the new size
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == " ":
            buttonList.append(Button([80 * j + 100, 80 * i + 200], key, [300, 60]))  # Adjusted size and positions
        else:
            buttonList.append(Button([80 * j + 100, 80 * i + 200], key))  # Smaller size and spacing

def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (x, y, w, h), 20, rt=0)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, button.text, (x + 15, y + 45), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)
    return img


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)
    img = drawAll(img, buttonList)

    if hands:
        hand1 = hands[0]
        lmList1 = hand1["lmList"] # list of 21 landmarks
        bbox1 = hand1["bbox"] # bounding box info x,y,w,h

        if len(hands) == 2:
                # Hand 2
                hand2 = hands[1]
                lmList2 = hand2["lmList"]  # List of 21 Landmark points
                bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
                centerPoint2 = hand2['center']  # center of the hand cx,cy
                handType2 = hand2["type"]  # Hand Type "Left" or "Right"

                fingers2 = detector.fingersUp(hand2)

                # Find Distance between two Landmarks. Could be same hand or different hands
                #l, _, _ = detector.findDistance(lmList1[8], lmList2[8], img)  # with draw
                # length, info = detector.findDistance(lmList1[8], lmList2[8]) 

        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < lmList1[8][0] < x+w and y < lmList1[8][1] < y+h:
                cv2.rectangle(img, button.pos, (x+w, y+h), (175,0,175), cv2.FILLED)
                cv2.putText(img, button.text, (x+20,y+65), 
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                # Pass only the (x, y) coordinates from the landmarks
                result = detector.findDistance((lmList1[8][0], lmList1[8][1]), (lmList1[4][0], lmList1[4][1]), img)
                l = result[0]  # Assuming the first element is the distance
                # print(l)

                if l<30:
                    keyboard.press(button.text)
                    cv2.rectangle(img, button.pos, (x+w, y+h), (0,255,0), cv2.FILLED)
                    cv2.putText(img, button.text, (x+10,y+45), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    finalText += button.text
                    sleep(0.13)

    cv2.rectangle(img, (150, 50), (1000, 150), (0,0,0), cv2.FILLED)
    cv2.putText(img, finalText, (160, 130), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Image", img)
    if cv2.waitKey(5) & 0xFF == 27:
      break


cap.release()
cv2.destroyAllWindows()