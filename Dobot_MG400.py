import socket
import cv2
import numpy as np
from threading import Thread

IP_ROBOT = "192.168.1.6"
PORT = 6601
INDEX_CAMERA = 1
MIN_AREA = 6500

lower_red = np.array([0,88,210])
upper_red = np.array([15,242,255])

lower_blue = np.array([83,36,155])
upper_blue = np.array([134,255,255])

lower_green = np.array([34,70,103])
upper_green = np.array([96,255,255])

lower_yellow = np.array([10,86,200])
upper_yellow = np.array([84,170,255])

List_Colors = [(lower_red, upper_red),
               (lower_blue, upper_blue),
               (lower_green, upper_green),
               (lower_yellow, upper_yellow)]
str_color = ["Red", "Blue", "Green", "Yellow"]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (IP_ROBOT, PORT)
print('connecting to %s port %s' % server_address)
sock.connect(server_address)

cap = cv2.VideoCapture(INDEX_CAMERA)

class Mg400(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()
        sock.send(Robot_Active.encode())

    def run(self):
        global X_robot, Y_robot, R_robot, color , Robot_Active, red_count, green_count, blue_count, yellow_count
        red_count = 0
        green_count = 0
        blue_count = 0
        yellow_count = 0
        Robot_Active = "0"
        first_send = 0

        while True:
            if cap.isOpened():
                if Robot_Active == "1" and first_send == 0:
                    sock.send(Robot_Active.encode())
                    first_send = 1
                    print(Robot_Active)
                if first_send == 1:
                    data = sock.recv(50)
                    print("receive: " + str(data))

                    if data == b'pose_color':
                        print("Color NO: ",color,": ", str_color[idx_color])
                        point = f"{X_robot},{Y_robot},{R_robot},{color},{red_count},{green_count},{blue_count},{yellow_count}"
                        sock.send(point.encode())
                        print("R: " , R_robot)
                        print("Y: " , Y_robot)

                        if color == 0:
                            red_count = red_count + 1
                        elif color == 1:
                            green_count = green_count + 1
                        elif color == 2:
                            blue_count = blue_count + 1
                        else:
                            yellow_count = yellow_count + 1

                    elif data == b'finish':
                        Robot_Active = "0"
                        first_send = 0

Mg400()



while True:

    ret, frame = cap.read()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if ret:
        roi = frame[0:430, 190:800]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        for idx_color, (low, high) in enumerate(List_Colors):
            mask = cv2.inRange(hsv, low, high)
            contours , _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:
                for i, c in enumerate(contours):
                    area = cv2.contourArea(c)
                    if area < MIN_AREA:
                        continue

                    rect = cv2.minAreaRect(c)
                    box = cv2.boxPoints(rect)
                    box = np.intp(box)

                    cv2.drawContours(roi, [box], 0, (221, 160, 221), 3)
                    
                    M = cv2.moments(c)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        cv2.circle(roi, (cX, cY), 3, (50, 50, 50), -1)
                        cv2.putText(roi, str_color[idx_color], (cX - 25, cY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

                    if str_color[idx_color] == "Red":
                        color = 0
                    elif str_color[idx_color] == "Green":
                        color = 1
                    elif str_color[idx_color] == "Blue":
                        color = 2
                    elif str_color[idx_color] == "Yellow":
                        color = 3

                    R_robot = round(-rect[2] , 2 )
                    X_robot = round(( -0.2149 * cY ) + 319.67  ,  2)
                    Y_robot = 131.70

                    if R_robot <= -17.00 and R_robot >= -73.00:

                        Y_robot = 130.10
                    
                    Robot_Active = "1"
            else:
                Robot_Active = "0"  
                      
        cv2.imshow("Frame", frame)
        cv2.imshow("Roi", roi)

sock.close()       
cap.release()
cv2.destroyAllWindows()