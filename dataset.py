from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from random import shuffle
import pickle

from imageTools import *
from config import *

# Creates name of dataset from parameters
def getDatasetName(numberPerGenre, sliceSize):
    name = "{}".format(numberPerGenre)
    name += "_{}".format(sliceSize)
    return name

# Creates or loads dataset if it exists
# Mode = "train" or "test"
def getDataset(numberPerGenre, genres, sliceSize, validationRatio, testRatio, mode):
    print("[+] Dataset name: {}".format(getDatasetName(numberPerGenre, sliceSize)))
    if not os.path.isfile(path + "train_X_" + getDatasetName(numberPerGenre, sliceSize) + ".p"):
        print("[+] Creating dataset with {} slices of size {} per genre... ".format(numberPerGenre, sliceSize))
        createDatasetFromSlices(numberPerGenre, genres, sliceSize, validationRatio, testRatio)
    else:
        print("[+] Using existing dataset")

    return loadDataset(numberPerGenre, genres, sliceSize, mode)

# Loads dataset
# Mode = "train" or "test"
def loadDataset(nbPerGenre, genres, sliceSize, mode):
    # Load existing
    datasetName = getDatasetName(nbPerGenre, sliceSize)
    if mode == "train":
        print("[+] Loading training and validation datasets... ")
        train_X = pickle.load(open("{}train_X_{}.p".format(path, datasetName), "rb"))
        train_y = pickle.load(open("{}train_y_{}.p".format(path, datasetName), "rb"))
        validation_X = pickle.load(open("{}validation_X_{}.p".format(path, datasetName), "rb"))
        validation_y = pickle.load(open("{}validation_y_{}.p".format(path, datasetName), "rb"))
        print("    Training and validation datasets loaded!")
        return train_X, train_y, validation_X, validation_y

    else:
        print("[+] Loading testing dataset... ")
        test_X = pickle.load(open("{}test_X_{}.p".format(path, datasetName), "rb"))
        test_y = pickle.load(open("{}test_y_{}.p".format(path, datasetName), "rb"))
        print("    Testing dataset loaded!")
        return test_X, test_y

# Saves dataset
def saveDataset(train_X, train_y, validation_X, validation_y, test_X, test_y, nbPerGenre, genres, sliceSize):
    # Create path for dataset if not existing
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:  # Guard against race condition
            print("erroe")

    # SaveDataset
    print("[+] Saving dataset... ")
    datasetName = getDatasetName(nbPerGenre, sliceSize)
    pickle.dump(train_X, open("{}train_X_{}.p".format(path, datasetName), "wb"))
    pickle.dump(train_y, open("{}train_y_{}.p".format(path, datasetName), "wb"))
    pickle.dump(validation_X, open("{}validation_X_{}.p".format(path, datasetName), "wb"))
    pickle.dump(validation_y, open("{}validation_y_{}.p".format(path, datasetName), "wb"))
    pickle.dump(test_X, open("{}test_X_{}.p".format(path, datasetName), "wb"))
    pickle.dump(test_y, open("{}test_y_{}.p".format(path, datasetName), "wb"))
    print("    Dataset saved!")

# Creates and save dataset from slices
def createDatasetFromSlices(nbPerGenre, genres, sliceSize, validationRatio, testRatio):
    data = []
    for genre in genres:
        print("-> Adding {}...".format(genre))
        # Get slices in genre subfolder
        filenames = os.listdir(slicePath + genre)
        filenames = [filename for filename in filenames if filename.endswith('.png')]
        filenames = filenames[:nbPerGenre]
        # Randomize file selection for this genre
        shuffle(filenames)

        # Add data (X,y)
        for filename in filenames:
            imgData = getImageData(slicePath + genre + "/" + filename, sliceSize)
            label = [1. if genre == g else 0. for g in genres]
            data.append((imgData, label))

    # Shuffle data
    shuffle(data)

    # Extract X and y
    X, y = zip(*data)

    # Split data
    validationNb = int(len(X) * validationRatio)
    testNb = int(len(X) * testRatio)
    trainNb = len(X) - (validationNb + testNb)

    # Prepare for Tflearn at the same time
    train_X = np.array(X[:trainNb]).reshape([-1, sliceSize, sliceSize, 1])
    train_y = np.array(y[:trainNb])
    validation_X = np.array(X[trainNb:trainNb + validationNb]).reshape([-1, sliceSize, sliceSize, 1])
    validation_y = np.array(y[trainNb:trainNb + validationNb])
    test_X = np.array(X[-testNb:]).reshape([-1, sliceSize, sliceSize, 1])
    test_y = np.array(y[-testNb:])
    print("    Dataset created! ")

    # Save
    saveDataset(train_X, train_y, validation_X, validation_y, test_X, test_y, nbPerGenre, genres, sliceSize)

    return train_X, train_y, validation_X, validation_y, test_X, test_y