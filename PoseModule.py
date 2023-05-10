import cv2
import mediapipe as mp
import math
import pandas as pd

def get_color(angulo, ang, ErrorSup, ErrorInf):
    # Verificamos si el ángulo está en el rango correcto
    if angulo == ang:
        return (255, 255, 255)  # Verde
    elif angulo > ang and angulo <= ErrorSup:
        # Calculamos la intensidad del color rojo y verde en base a la distancia al ángulo correcto
        rojo = int((angulo - ang) / 30 * 255)
        verde = int((ErrorSup - angulo) / 30 * 255)
        return (rojo, verde, 0)  # Mezcla de rojo y verde
    elif angulo < ang and angulo >= ErrorInf:
        # Calculamos la intensidad del color rojo y verde en base a la distancia al ángulo correcto
        rojo = int((ang - angulo) / 30 * 255)
        verde = int((angulo - ErrorInf) / 30 * 255)
        return (rojo, verde, 0)  # Mezcla de rojo y verde
    else:
        return (255, 0, 0)  # Rojo puro


class PoseDetector:
    """
    Estimates Pose points of a human body using the mediapipe library.
    """

    def __init__(self, mode=False, smooth=True,
                 detectionCon=0.5, trackCon=0.5):
        """
        :param mode: In static mode, detection is done on each image: slower
        :param smooth: Smoothness Flag
        :param detectionCon: Minimum Detection Confidence Threshold
        :param trackCon: Minimum Tracking Confidence Threshold
        """

        self.mode = mode
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(static_image_mode=self.mode,
                                     smooth_landmarks=self.smooth,
                                     min_detection_confidence=self.detectionCon,
                                     min_tracking_confidence=self.trackCon)

    def findPose(self, img, draw=True):
        """
        Find the pose landmarks in an Image of BGR color space.
        :param img: Image to find the pose in.
        :param draw: Flag to draw the output on the image.
        :return: Image with or without drawings
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                           self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=False, bboxWithHands=False, flipType=False):
        """
        It takes an image, and returns a list of landmarks and a bounding box

        :param img: The image to be processed
        :param draw: If True, the bounding box and center point will be drawn on the image, defaults to False (optional)
        :param bboxWithHands: If True, the bounding box will include the hands. If False, the bounding box will not include
        the hands, defaults to False (optional)
        :param flipType: If you want to flip the image, you can use the following values:, defaults to False (optional)
        """

        self.lmList = []
        self.bboxInfo = {}

        myPose = {}

        mylmList = []
        xList = []
        yList = []

        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy, cz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                self.lmList.append([id, cx, cy, cz])
                mylmList.append([cx, cy, cz])
                xList.append(cx)
                yList.append(cy)

            # Bounding Box
            ad = abs(self.lmList[12][1] - self.lmList[11][1]) // 2
            if bboxWithHands:
                x1 = self.lmList[16][1] - ad
                x2 = self.lmList[15][1] + ad
            else:
                x1 = self.lmList[12][1] - ad
                x2 = self.lmList[11][1] + ad

            # box
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            boxW, boxH = xmax - xmin, ymax - ymin
            bbox = xmin, ymin, boxW, boxH

            myPose["lmList"] = mylmList
            myPose["bbox"] = bbox
            myPose["boxW"] = boxW

            y2 = self.lmList[29][2] + ad
            y1 = self.lmList[1][2] - ad
            # bbox = (x1, y1, x2 - x1, y2 - y1)
            cx, cy = bbox[0] + (bbox[2] // 2), \
                     bbox[1] + bbox[3] // 2

            myPose["center"] = (cx, cy)

            self.bboxInfo = {"bbox": bbox, "center": (cx, cy)}

            if draw:
                cv2.rectangle(img, bbox, (255, 0, 255), 3)
                cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

        return self.lmList, self.bboxInfo

    # debe recibir por parametros los 3 puntos que uno quiere que evalue y calcule el angulo
    def findAngle(self, lmList, img, a1, b2, c3, ang, draw=True):
        """
        It takes in a list of landmarks, an image, and three landmark numbers, and returns the angle between the lines
        formed by the three landmarks

        :param lmList: The list of landmarks
        :param img: The image to draw on
        :param a1: The first landmark to use for the angle calculation
        :param b2: The point where the two lines meet
        :param c3: The landmark number of the point that is the furthest away from the line
        :param ang: The angle
        :param draw: If True, the function will draw the angle on the image, defaults to True (optional)
        :return: The angle between the three points.
        """

        l = pd.DataFrame(lmList,
                         columns=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                                  "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
                                  "30", "31", "32"])
        p1 = pd.Series(l[a1])
        p2 = pd.Series(l[b2])
        p3 = pd.Series(l[c3])

        # # print(l)

        # print("11", dat1[0])
        # print("13", dat2[0])
        # print("15", dat3[0])

        # Get the landmarks
        x1, y1 = p1[0][1], p1[0][2]
        x2, y2 = p2[0][1], p2[0][2]
        x3, y3 = p3[0][1], p3[0][2]

        # Calculate the Angle
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                             math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360

        # Draw
        RGB = get_color(angle, ang, ang+30, ang-30)

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), RGB[::-1] , 4)
            cv2.line(img, (x3, y3), (x2, y2), RGB[::-1] , 4)
            cv2.circle(img, (x1, y1), 2, RGB[::-1] , cv2.FILLED)
            cv2.circle(img, (x2, y2), 2, RGB[::-1] , cv2.FILLED)
            cv2.circle(img, (x3, y3), 2, RGB[::-1] , cv2.FILLED)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50), cv2.FONT_HERSHEY_PLAIN, 2, RGB[::-1], 2)
        return angle

    # recibe los colores de las lineas
    def drawBody(self, img, lmList, c1=255, c2=255, c3=255, c4=0, c5=0, c6=255, draw=True):
        """
        It draws a body on the image using the landmarks

        :param img: The image to draw on
        :param lmList: the list of landmarks
        :param c1: Red, defaults to 255 (optional)
        :param c2: The color of the line, defaults to 255 (optional)
        :param c3: The color of the lines that connect the joints, defaults to 255 (optional)
        :param c4: red, defaults to 0 (optional)
        :param c5: The color of the body parts, defaults to 0 (optional)
        :param c6: color of the circles, defaults to 255 (optional)
        :param draw: If True, the body will be drawn on the image, defaults to True (optional)
        """

        # l = pd.DataFrame(lmList,
        #                  columns=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
        #                           "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
        #                           "30", "31", "32"])

        # # brazo izquierdo
        # p1 = pd.Series(l["11"])
        # p2 = pd.Series(l["13"])
        # p3 = pd.Series(l["15"])
        # # Get the landmarks
        # x1, y1 = p1[0][1], p1[0][2]
        # x2, y2 = p2[0][1], p2[0][2]
        # x3, y3 = p3[0][1], p3[0][2]

        # # brazo derecho
        # p4 = pd.Series(l["12"])
        # p5 = pd.Series(l["14"])
        # p6 = pd.Series(l["16"])
        # x4, y4 = p4[0][1], p4[0][2]
        # x5, y5 = p5[0][1], p5[0][2]
        # x6, y6 = p6[0][1], p6[0][2]

        # # pierna izquierda
        # p7 = pd.Series(l["23"])
        # p8 = pd.Series(l["25"])
        # p9 = pd.Series(l["27"])
        # x7, y7 = p7[0][1], p7[0][2]
        # x8, y8 = p8[0][1], p8[0][2]
        # x9, y9 = p9[0][1], p9[0][2]

        # # pierdna derecha
        # p10 = pd.Series(l["24"])
        # p11 = pd.Series(l["26"])
        # p12 = pd.Series(l["28"])
        # x10, y10 = p10[0][1], p10[0][2]
        # x11, y11 = p11[0][1], p11[0][2]
        # x12, y12 = p12[0][1], p12[0][2]


        # The above code is extracting the x and y coordinates of specific body keypoints from a
        # dataframe of pose estimation data. It then assigns these coordinates to variables for
        # further processing. Specifically, it extracts the coordinates for the left and right arms,
        # and left and right legs.
        l = pd.DataFrame(lmList, columns=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
                                  "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
                                  "30", "31", "32"])

        keypoints = [
            ["11", "13", "15"],  # brazo izquierdo
            ["12", "14", "16"],  # brazo derecho
            ["23", "25", "27"],  # pierna izquierda
            ["24", "26", "28"]   # pierna derecha
        ]

        coordinates = []
        for group in keypoints:
            coords = []
            for point in group:
                x, y = l.loc[0, point][1:3]
                coords.append((x, y))
            coordinates.append(coords)

        x1, y1 = coordinates[0][0]
        x2, y2 = coordinates[0][1]
        x3, y3 = coordinates[0][2]

        x4, y4 = coordinates[1][0]
        x5, y5 = coordinates[1][1]
        x6, y6 = coordinates[1][2]

        x7, y7 = coordinates[2][0]
        x8, y8 = coordinates[2][1]
        x9, y9 = coordinates[2][2]

        x10, y10 = coordinates[3][0]
        x11, y11 = coordinates[3][1]
        x12, y12 = coordinates[3][2]


        # if draw:
        #     # lineas del torso
        #     cv2.line(img, (x1, y1), (x4, y4), (c1, c2, c3), 3)
        #     cv2.line(img, (x4, y4), (x10, y10), (c1, c2, c3), 3)
        #     cv2.line(img, (x10, y10), (x7, y7), (c1, c2, c3), 3)
        #     cv2.line(img, (x7, y7), (x1, y1), (c1, c2, c3), 3)

        #     cv2.line(img, (x1, y1), (x2, y2), (c1, c2, c3), 3)
        #     cv2.line(img, (x3, y3), (x2, y2), (c1, c2, c3), 3)
        #     cv2.circle(img, (x1, y1), 3, (c4, c5, c6), cv2.FILLED)
        #     cv2.circle(img, (x2, y2), 3, (c4, c5, c6), cv2.FILLED)
        #     cv2.circle(img, (x3, y3), 3, (c4, c5, c6), cv2.FILLED)

        #     cv2.line(img, (x4, y4), (x5, y5), (c1, c2, c3), 3)
        #     cv2.line(img, (x6, y6), (x5, y5), (c1, c2, c3), 3)
        #     cv2.circle(img, (x4, y4), 3, (c4, c5, c6), cv2.FILLED)
        #     cv2.circle(img, (x5, y5), 3, (c4, c5, c6), cv2.FILLED)
        #     cv2.circle(img, (x6, y6), 3, (c4, c5, c6), cv2.FILLED)

        #     cv2.line(img, (x7, y7), (x8, y8), (c1, c2, c3), 3)
        #     cv2.line(img, (x9, y9), (x8, y8), (c1, c2, c3), 3)
        #     cv2.circle(img, (x7, y7), 3, (c4, c5, c6), cv2.FILLED)
        #     cv2.circle(img, (x8, y8), 3, (c4, c5, c6), cv2.FILLED)
        #     cv2.circle(img, (x9, y9), 3, (c4, c5, c6), cv2.FILLED)

        #     cv2.line(img, (x10, y10), (x11, y11), (c1, c2, c3), 3)
        #     cv2.line(img, (x12, y12), (x11, y11), (c1, c2, c3), 3)
        #     cv2.circle(img, (x10, y10), 3, (c4, c5, c6), cv2.FILLED)
        #     cv2.circle(img, (x11, y11), 3, (c4, c5, c6), cv2.FILLED)
        #     cv2.circle(img, (x12, y12), 3, (c4, c5, c6), cv2.FILLED)


        # The above code is drawing a set of polygons and circles on an image using OpenCV library in
        # Python. The coordinates of the polygons and circles are defined in the "coordinates" list
        # and the connections between the points are defined in the "connections" list. The code then
        # iterates through each set of coordinates and connections, draws lines and circles using the
        # cv2.line() and cv2.circle() functions respectively, and finally displays the image with the
        # drawn shapes.
        if draw:
            coordinates = [
                [(x1, y1), (x4, y4), (x10, y10), (x7, y7)],
                [(x1, y1), (x2, y2), (x3, y3)],
                [(x4, y4), (x5, y5), (x6, y6)],
                [(x7, y7), (x8, y8), (x9, y9)],
                [(x10, y10), (x11, y11), (x12, y12)]
            ]

            connections = [
                [0, 1, 2, 3],
                [0, 1, 2],
                [0, 1, 2],
                [0, 1, 2],
                [0, 1, 2]
            ]

            for coords, connects in zip(coordinates, connections):
                for i in range(len(coords) - 1):
                    cv2.line(img, coords[i], coords[i+1], (c1, c2, c3), 3)
                    cv2.circle(img, coords[i], 3, (c4, c5, c6), cv2.FILLED)

                cv2.circle(img, coords[-1], 3, (c4, c5, c6), cv2.FILLED)


    def findDistance(self, p1, p2, img, draw=True, r=15, t=3):
        """
        It takes two points, draws a line between them, and returns the length of the line

        :param p1: The first point to draw the line from
        :param p2: The ndx of the landmark you want to measure the distance to
        :param img: The image to draw on
        :param draw: If True, the function will draw the line and the points on the image, defaults to True (optional)
        :param r: radius of the circle, defaults to 15 (optional)
        :param t: thickness of the line, defaults to 3 (optional)
        :return: The distance between the two points, the image, and the coordinates of the two points and the center point.
        """
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]

    def angleCheck(self, myAngle, targetAngle, addOn=20):
        """
        It checks if the angle of the player is within a certain range of the target angle

        :param myAngle: The angle of the object you want to check
        :param targetAngle: The angle you want to turn to
        :param addOn: This is the amount of degrees that the angle can be off by, defaults to 20 (optional)
        :return: a boolean value.
        """
        return targetAngle - addOn < myAngle < targetAngle + addOn

    def fist(self, list, p1, p2, p3, ang):
        """
        It takes in a list of lists

        :param list: the list of coordinates of the hand
        :param p1: the ndx of the first point in the list of points
        :param p2: the ndx of the middle finger
        :param p3: the ndx of the point that is the wrist
        :param ang: angle between the two lines
        :return: the boolean values of fista and fistb.
        """

        fista, fistb = False, False

        # gedan barai
        posY = list[0][p1][2] - list[0][p2][2]
        if ((int(ang) > 70 and int(ang) < 80)) and (posY - 20 > list[0][p3][2] or posY + 20 < list[0][p3][2]):
            fista = True

        # oi zuki
        p1 = list[0][p2][2]
        if ((int(ang) > 170 and int(ang) < 190)) and (list[0][p3][2] > p1 - 20 and list[0][p3][2] < p1 + 20):
            fistb = True

        return fista, fistb

    def comprobacionAng(self, angAmin, angAmax, angBmin, angBmax, angCmin, angCmax, angDmin, angDmax, anguloa, angulob,
                        anguloc, angulod):

        es = False
        if angAmin < int(anguloa) < angAmax:
            if angBmin < int(angulob) < angBmax:
                if angCmin < int(anguloc) < angCmax:
                    if angDmin < int(angulod) < angDmax:
                        es = True
        return es


def main():
    cap = cv2.VideoCapture(0)
    detector = PoseDetector()
    while True:
        success, img = cap.read()
        img = detector.findPose(img)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
        if bboxInfo:
            center = bboxInfo["center"]
            cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
