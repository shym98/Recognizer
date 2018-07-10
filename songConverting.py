from subprocess import Popen, PIPE, STDOUT
import os
from PIL import Image
from config import *

currentPath = os.path.dirname(os.path.realpath(__file__))

def createSpectrogram(filename, newFilename):
    command = "sox '{}' '/tmp/{}.mp3' remix 1,2".format(path + filename + '.mp3', newFilename)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
    output, errors = p.communicate()
    command = "sox '/tmp/{}.mp3' -n spectrogram -Y 200 -X {} -m -r -o '{}.png'".format(newFilename, 50, spectPath + newFilename)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=currentPath)
    output, errors = p.communicate()
    os.remove("/tmp/{}.mp3".format(newFilename))

def createSlicesFromSpectrograms(desiredSize):
    for filename in os.listdir(spectPath):
        if filename.endswith(".png"):
            sliceSpectrogram(filename, desiredSize)

def sliceSpectrogram(filename, desiredSize):
    genre = filename.split("_")[0]
    img = Image.open(spectPath + filename)

    width, height = img.size
    nbSamples = int(width / desiredSize)
    width - desiredSize

    myslicePath = slicePath + "{}/".format(genre)
    if not os.path.exists(os.path.dirname(myslicePath)):
        try:
            os.makedirs(os.path.dirname(myslicePath))
        except OSError as exc:
            print('error')

    for i in range(nbSamples):
        startPixel = i * desiredSize
        img.crop((startPixel, 1, startPixel + desiredSize, desiredSize + 1)).save(
            slicePath + "{}/{}_{}.png".format(genre, filename[:-4], i))

    try:
        os.remove(spectPath + filename)
    except OSError as exc:
        print('No such file')

def songsToData():

    files = os.listdir(path)
    files = [file for file in files if file.endswith(".mp3")]
    nbFiles = len(files)

    if not os.path.exists(os.path.dirname(spectPath)):
        try:
            os.makedirs(os.path.dirname(spectPath))
        except OSError as exc:
            print("error")

    for index, filename in enumerate(files):
        print("Creating spectrogram for file {}/{}...".format(index + 1, nbFiles))
        genre = filename.split("_")[0]
        index1 = filename.split("_")[1].split(".")[0]
        newFilename = genre + "_" + str(index1)
        createSpectrogram(newFilename, newFilename + "mono")

    createSlicesFromSpectrograms(sliceSize)