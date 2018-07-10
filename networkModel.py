import tflearn
from tflearn import input_data, conv_2d, max_pool_2d, fully_connected, dropout, regression

def createModel(classesNumber, imageSize):

    print("[+] Creating model ...")
    network = input_data(shape=[None, imageSize, imageSize, 1], name='input')

    network = conv_2d(network, 64, 2, activation='elu', weights_init="Xavier")
    network = max_pool_2d(network, 2)

    network = conv_2d(network, 128, 2, activation='elu', weights_init="Xavier")
    network = max_pool_2d(network, 2)

    network = conv_2d(network, 256, 2, activation='elu', weights_init="Xavier")
    network = max_pool_2d(network, 2)

    network = conv_2d(network, 512, 2, activation='elu', weights_init="Xavier")
    network = max_pool_2d(network, 2)

    network = fully_connected(network, 1024, activation='elu')
    network = dropout(network, 0.5)

    network = fully_connected(network, classesNumber, activation='softmax')
    network = regression(network, optimizer='rmsprop', loss='categorical_crossentropy')

    network = tflearn.DNN(network)
    print("[+] Model created")

    return network