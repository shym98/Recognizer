import string
import argparse
import random

from songConverting import *
from networkModel import *
from dataset import *
from tkinter.filedialog import *
from tkinter import messagebox
from shutil import copyfile, rmtree

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

#List genres
genres = os.listdir(slicePath)
genres = [filename for filename in genres if os.path.isdir(slicePath+filename)]
nbClasses = len(genres)

#Create model
model = createModel(nbClasses, sliceSize)

# Choosing file to recognize
def chooseFile():
	model.load('musicDNN.tflearn')
	filename = askopenfilename()
	if filename.endswith(".mp3"):
		fileLabel.config(text=filename)
	else:
		messagebox.showinfo("Error", "Incorrect file extension. Must be *.mp3")
		return

# Recognizing song
def recognize():
	filePath = fileLabel['text']
	copyfile(filePath, path + "test.mp3")
	createSpectrogram("test", "test_mono")
	sliceSpectrogram("test_mono.png", sliceSize)
	data = []
	for filename in os.listdir(slicePath + "test/"):
		if filename.endswith(".png"):
			data.append(getImageData(slicePath + "test/" + filename, sliceSize))
	predictionSoftmax = model.predict(data)[0]
	print(toFixed(predictionSoftmax[0],3),toFixed(predictionSoftmax[1],3), toFixed(predictionSoftmax[2],3), toFixed(predictionSoftmax[3],3))
	predictedIndex = max(enumerate(predictionSoftmax), key=lambda x: x[1])[0]
	text = genres[predictedIndex]
	messagebox.showinfo("Result", text)
	rmtree(slicePath + "test/")
	try:
		os.remove(path + "test.mp3")
	except OSError as exc:
		print('No such file')

# Open main form
if len(sys.argv) == 1:

	root = Tk()
	root.title("Recognizer")

	nameLabel = Label(root, text = "File path: ")
	nameLabel.grid(row = 1, column = 1)
	fileLabel = Label(root, text = "                                                                 ", bg = "white", justify = "center")
	fileLabel.grid(row = 1, column = 2)
	choseButton = Button(root, text = "Browse", bg = "white", command = chooseFile).grid(row = 1, column = 3)
	recognizeButton = Button(root, text = "Recognize", bg = "white", command = recognize).grid(row = 2, column = 1, columnspan = 3)

	root.mainloop()

	exit(0)

# Parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("mode", nargs='+', choices=["train","test","slice"])
args = parser.parse_args()

# Converting songs into spectrogram and slicing them
if "slice" in args.mode:
	songsToData()
	sys.exit()

# Train model
if "train" in args.mode:

	#Create or load new dataset
	train_X, train_y, validation_X, validation_y = getDataset(filesPerGenre, genres, sliceSize, validationRatio, testRatio, mode="train")

	#Define run id for graphs
	run_id = "MusicGenres - "+str(batchSize)+" "+''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(10))

	#Train the model
	print("[+] Training the model...")
	model.fit(train_X, train_y, n_epoch=numberOfEpoch, batch_size=batchSize, shuffle=True, validation_set=(validation_X, validation_y), snapshot_step=100, show_metric=True, run_id=run_id)
	print("    Model trained!")

	#Save trained model
	print("[+] Saving the weights...")
	model.save('musicDNN.tflearn')
	print("[+] Weights saved!")

# Test model
if "test" in args.mode:

	#Create or load new dataset
	test_X, test_y = getDataset(filesPerGenre, genres, sliceSize, validationRatio, testRatio, mode="test")

	#Load weights
	print("[+] Loading weights...")
	model.load('musicDNN.tflearn')
	print("    Weights loaded! ✅")

	testAccuracy = model.evaluate(test_X, test_y)[0]
	print("[+] Test accuracy: {} ".format(testAccuracy))
	#rename()
