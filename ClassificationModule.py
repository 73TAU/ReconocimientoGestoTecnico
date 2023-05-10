import tensorflow.keras
import numpy as np
import cv2

class Classifier:

    def __init__(self, modelPath, labelsPath=None):
        """
        The function takes in the path to the model and the path to the labels file. It then loads the model and creates an
        array of the right shape to feed into the model

        :param modelPath: The path to the model file
        :param labelsPath: The path to the labels file
        """
        self.model_path = modelPath
        # Disable scientific notation for clarity
        np.set_printoptions(suppress=True)
        # Load the model
        self.model = tensorflow.keras.models.load_model(self.model_path)

        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1.
        self.data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        self.labels_path = labelsPath


    def getPrediction(self, img):
        """
        We take an image, resize it to 224x224, normalize it, and then run it through the model

        :param img: the image to be classified
        :return: The prediction is being returned.
        """
        # resize the image to a 224x224 with the same strategy as in TM2:
        imgS = cv2.resize(img, (224, 224))
        # turn the image into a numpy array
        image_array = np.asarray(imgS)
        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        self.data[0] = normalized_image_array

        # run the inference
        prediction = self.model.predict(self.data)
        indexVal = np.argmax(prediction)

        return list(prediction[0]), indexVal
