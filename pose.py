# Importing the math, cv2 and time modules.
import cv2
import math
import time
import numpy as np

from PoseModule import PoseDetector
from PostureClassifier import PostureClassifier

#posturas
def posturas():
    # Define angle ranges
    rei_angles = (160, 190, 160, 190, 160, 190, 160, 190)
    kamae_angles = (160, 190, 160, 190, 160, 190, 160, 190)
    oi_zuki_angles = (110, 130, 160, 180, 220, 240, 160, 185)
    oi_guedan_barai_angles = (160, 190, 60, 85, 175, 205, 220, 250)

    # Check for rei posture
    rei_check = detector.comprobacionAng(*rei_angles, anguloa, angulob, anguloc, angulod)
    if rei_check and list[0][27][1] - list[0][28][1] <= list[0][23][1] - list[0][24][1]:
        return 0

    # Check for kamae posture
    kamae_check = detector.comprobacionAng(*kamae_angles, anguloa, angulob, anguloc, angulod)
    if kamae_check and list[0][27][1] - list[0][28][1] >= list[0][23][1] - list[0][24][1]:
        return 1

    # Check for oi zuki posture
    if detector.comprobacionAng(*oi_zuki_angles, anguloa, angulob, anguloc, angulod):
        return 2

    # Check for oi guedan barai posture
    if detector.comprobacionAng(*oi_guedan_barai_angles, anguloa, angulob, anguloc, angulod):
        return 3

    return None

# imagen
# cap = cv2.VideoCapture("img\muestra\Screenshot_2.JPG")

# camara
# deteccion de camara primaria: 0
# deteccion de camara secundaria: 1
cap = cv2.VideoCapture(0)

# Capturing the video from the file.
# cap = cv2.VideoCapture("videos/Taikyoku Shodan _ Shotokan Karate Kata.mp4")
# cap = cv2.VideoCapture("videos/KATA HEIAN SHODAN (KARATE DO SHOTOKAN).mp4")

# Creating a new instance of the PoseDetector class.
detector = PoseDetector()
posture = PostureClassifier()

# Used to increase the size of the bounding box.
offset = 20

# The size of the image that is used to predict the class.
imgSize = 500

# Creating a folder called "img/a"
folder = "img/a"

# Used to count the number of images that are saved.
counter = 0

# A list of labels that are used to display the prediction of the classifier.
labe = 0
labels = ["REI", "KAMAE", "OI ZUKI", "GEDAN BARAI", ""]
ndx = 4

# Setting the initial value of pTime to 0.
pTime = 0

eval_oiZuki = 0
eval_gedanBarai = 0
eval_rei = 0
eval_kamae = 0

indx = 4

fista = []
fistb = []
vlocidad_puno = []
count_fist = 0
caderaA = []
caderaB = []
count_cadera = 0

bar_golpe = 7

while True:
    success, img = cap.read()
    # img = cv2.imread("1st Kata - Taigyoku Shodan.mp4")

    img = cv2.resize(img, (1280, 720))
    img = detector.findPose(img, False)
    lmlist = detector.findPosition(img, False)
    pose = detector.findPosition(img, False)
    draw = detector.drawBody(img, lmlist, 66, 202, 36, 36, 66, 202, False)

    if bool(lmlist[0]) != False:

        Pose = pose[1]
        x, y, w, h = Pose["bbox"]
        # print(x, y, w, h)

        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
        imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

        imgCropShape = imgCrop.shape

        aspectRatio = h / w

        if aspectRatio > 1:
            k = imgSize / h
            wCal = math.ceil(k * w)
            try:
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                imgResizeShape = imgResize.shape
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
            except:
                pass

        else:
            k = imgSize / w
            hCal = math.ceil(k * h)
            try:
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                imgResizeShape = imgResize.shape
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize
            except:
                pass
        list = detector.findPosition(imgWhite, False)
        print(list)
        # These lines of code are calculating the angles between specific body parts detected by the
        # PoseDetector class. The `detector.findAngle()` method takes in the list of landmarks
        # `lmlist`, the image `img`, and the indices of the body parts to calculate the angle between.
        # The resulting angles are stored in the variables `anguloa`, `angulob`, `anguloc`, and
        # `angulod`.

        anguloa = detector.findAngle(lmlist, img, "11", "13", "15", 90, True)
        angulob = detector.findAngle(lmlist, img, "12", "14", "16", 90, True)
        anguloc = detector.findAngle(lmlist, img, "24", "26", "28", 90, True)
        angulod = detector.findAngle(lmlist, img, "23", "25", "27", 90, True)


        extremidades = ['B', 'B', 'P', 'P']
        lados = [1, 2, 1, 2]
        angu= [180, 90, 145, 120]
        print("nuevo modulo: ", posture.articulaciones(lmlist, img, extremidades, lados, angu, len(extremidades)))


        # posturas
        ndx = posturas()

        predicion = "prediction " + str(ndx)
        cv2.putText(img, predicion, (100, 100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

        angulo = "angulo " + str(int(anguloa)) + " " + str(int(angulob)) + " " + str(int(anguloc)) + " " + str(int(angulod))
        cv2.putText(img, angulo, (100, 120), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

        a, b = detector.fist(list, 24, 12, 16, angulob)[0], detector.fist(list, 24, 12, 16, angulob)[1]
        print(a, b)

        if (ndx == 2):
            print("oiZuki")
            cv2.putText(img, "oizuki", (100, 160), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            eval_oiZuki += 1
            eval_gedanBarai = 0
            eval_rei = 0
            eval_kamae = 0
            print(eval_oiZuki)
            if (eval_oiZuki == bar_golpe):
                print(eval_oiZuki)
                eval_oiZuki = 0

        if (ndx == 3):
            print("gedanbarai")
            cv2.putText(img, "gedanbarai", (100, 160), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            eval_gedanBarai += 1
            eval_rei = 0
            eval_kamae = 0
            eval_oiZuki = 0
            print(eval_gedanBarai)
            if (eval_gedanBarai == bar_golpe):
                print(eval_gedanBarai)
                eval_gedanBarai = 0

        if (ndx == 0):
            print("rei")
            cv2.putText(img, "rei", (100, 160), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            eval_rei += 1
            eval_kamae = 0
            eval_oiZuki = 0
            eval_gedanBarai = 0
            print(eval_rei)
            if (eval_rei == bar_golpe):
                print(eval_rei)
                eval_rei = 0

        if (ndx == 1):
            print("kamae")
            cv2.putText(img, "kamae", (100, 160), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            eval_kamae += 1
            eval_oiZuki = 0
            eval_gedanBarai = 0
            eval_rei = 0
            print(eval_kamae)
            if (eval_kamae == bar_golpe):
                print(eval_kamae)
                eval_kamae = 0

        if eval_oiZuki == 6:
            indx = 2
        elif eval_gedanBarai == 6:
            indx = 3
        elif eval_rei == 6:
            indx = 0
        elif eval_kamae == 6:
            indx = 1

        predicion = "prediction " + str(indx)
        cv2.putText(img, predicion, (100, 140), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

        print("indx: ", indx)
        cv2.putText(img, labels[indx], (x, y - 50), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)

        print("anguloa: ", anguloa, "angulob: ", angulob, "anguloc: ", anguloc, "angulod: ", angulod)

        # cv2.imshow("ImageCrop", imgCrop)
        cv2.imshow("ImageWhite", imgWhite)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("image", img)
    cv2.waitKey(1)
    # key = cv2.waitKey(1)
    # if key == ord("s"):
    #     counter += 1
    #     cv2.imwrite(f'{folder}/Image_{time.time()}.jpg',img)
    #     print(counter)
