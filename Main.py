import time
import cv2
import cvzone
import math
from pyfirmata import Arduino, SERVO, PWM, OUTPUT


#Size 640 x 480

from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 20)

cap.set(3, 640)
cap.set(4, 480)

detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

pTime = 0

lenght_r = 0
angle_pitch = 0
angle_yaw = 90

board = Arduino("COM4")

ena = board.digital[5]

in1 = board.digital[6]
in2 = board.digital[7]

pin_9 = board.digital[9]
pin_10 = board.digital[10]

ena.mode = PWM

in1.mode = OUTPUT
in2.mode = OUTPUT

pin_9.mode = SERVO
pin_10.mode = SERVO

def writeAngle(pin, angle):
    pin.write(angle)

while True:
    success, img = cap.read()

    height, width, _ = img.shape
    img_center_x = width // 2
    img_center_y = height // 2
    img_center = [img_center_x, img_center_y]

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    hands, img = detector.findHands(img, draw=False, flipType=True)

    if hands:

        hand = hands[0] 
        lmList = hand["lmList"] 
        bbox = hand["bbox"]
        center = hand['center']
        handType = hand["type"]

        length, info, img = detector.findDistance(lmList[4][0:2], lmList[8][0:2], img, color=(0, 255, 0),
                                                  scale=8)

        hand_size = max(bbox[2], bbox[3])

        lenght_r = round(length / hand_size, 1)

        cv2.circle(img, center, 5, (255, 0, 0), cv2.FILLED)

        cv2.line(img, center, (img_center_x, img_center_y), (255 ,0, 255), 2)

        if lenght_r < 0.2:
            lenght_r = 1
        else:
            lenght_r = 0

        offset_x = center[0] - img_center_x
        offset_y = img_center_y  - center[1]

        angle_yaw = int(((offset_x - (-320)) / (320 - (-320))) * (180- 0) + 0)
        angle_pitch = int(((offset_y - (-240)) / (240 - (-240))) * (120 - 60) + 60)

        #pin_9.write(angle_yaw)
        writeAngle(pin_9, angle_yaw)
        writeAngle(pin_10, angle_pitch)

        if lenght_r == 1:
            print("eys")
            in1.write(1)
            in2.write(0)
            ena.write(1)
        else:
            print("no")
            in1.write(0)
            in2.write(0)
            ena.write(0)
    else:
        writeAngle(pin_9, angle_yaw)
        writeAngle(pin_10, angle_pitch)

        board.digital[6].write(0)
        board.digital[7].write(0)
        
    cv2.circle(img, (img_center_x, img_center_y), 5, (255, 0, 0), cv2.FILLED)

    cv2.putText(img, f'FPS : {int(fps)}', (20, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
    cv2.putText(img, "Fire: " + str(lenght_r), (20, 60), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
    cv2.putText(img, "Angle Yaw : " + str(angle_yaw), (20, 80), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)
    cv2.putText(img, "Angle Pitch : " + str(angle_pitch), (20, 100), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)


    cv2.line(img, (0, img_center_y), (width, img_center_y), (0, 255, 0), 1)  # Horizontal line
    cv2.line(img, (img_center_x, 0), (img_center_x, height), (0, 255, 0), 1) # Vertical line

    resized_img = cv2.resize(img, (960, 720))

    cv2.imshow("Tracked", resized_img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break


writeAngle(pin_9, 90)
writeAngle(pin_10, 90)

cap.release()
board.exit()
cv2.destroyAllWindows()