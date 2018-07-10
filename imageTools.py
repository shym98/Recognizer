from PIL import Image
import numpy as np

def getProcessedData(image, imageSize):
    image = image.resize((imageSize, imageSize), resample=Image.ANTIALIAS)
    imageData = np.asarray(image, dtype=np.uint8).reshape(imageSize, imageSize, 1)
    imageData = imageData/255.
    return imageData

def getImageData(filename,imageSize):
    image = Image.open(filename)
    imageData = getProcessedData(image, imageSize)
    return imageData