from nltk.stem import SnowballStemmer
import pickle
import random
import json
import numpy as np
import nltk  # natural language toolkit
nltk.download('punkt')
stemmer = SnowballStemmer('spanish')


def calcAnswer(question):
    ############################################################################################
    ##############################PREPROCESAMENT################################################
    ############################################################################################

    with open("intents.json") as file:
        data = json.load(file)

    dictionary = []
    classes = []

    #####CREACIÓ DE DICCIONARI##################################################################
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            # funcio que concatena les paraules en una llista
            word_array = nltk.word_tokenize(pattern)
            dictionary.extend(word_array)  # vector amb totes les paraules

        classes.append(intent["class"])

    # process de "stemming" : quedarse amb el cor de les paraules
    dictionary = [stemmer.stem(word.lower()) for word in dictionary]

    dictionary = sorted(list(set(dictionary)))
    classes = sorted(classes)

    dictionary = np.array(dictionary)
    classes = np.array(classes)

    #####  TRACTAMENT DELS EXEMPLES   ##########################################################

    input_x = []  # features
    output_y = []  # labels

    # creem un vector amb totes les frases y les corresponents classes
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            sentence = nltk.word_tokenize(pattern)
            # Steem de input_x
            words = [stemmer.stem(word)
                     for word in sentence if word not in "?"]
            input_x.append(words)
            output_y.append(intent["class"])

    # numero de paraules en el diccionari (dimensions del vector)
    D, = dictionary.shape
    M, = classes.shape  # numero de possibles classificacions
    N = len(input_x)  # numero dexemples per entrenar el model

    output_y_nums = np.zeros((N, 1))

    for i in range(N):
        for j in range(M):
            if output_y[i] == classes[j]:
                output_y_nums[i] = j

    ########################################################################################
    # Creem una "bag of words".
    # Methode "One Hot Encoding" tenim la paraula?->1; no hi ha la paraula ->0.
    ########################################################################################

    training = np.zeros((N, D))
    output = output_y_nums

    for j, sentence in enumerate(input_x, 0):

        bag_of_words = np.zeros(len(dictionary))

        for i in range(D):
            word = dictionary[i]
            if word in sentence:
                bag_of_words[i] = 1
            else:
                bag_of_words[i] = 0

        training[j] = bag_of_words


    ############################################################################################
    ###########################  MODEL DE DEEP LEARNING  #######################################
    ############################################################################################

    import tensorflow as tf

    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(8, activation=tf.nn.relu, input_dim=D))
    model.add(tf.keras.layers.Dense(8, activation=tf.nn.relu))
    model.add(tf.keras.layers.Dense(M, activation=tf.nn.softmax))

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # model.summary()

    try:
        new_model = tf.keras.models.load_model('chatbot.model')

    except:
        model.fit(training, output, epochs=300)
        model.save('chatbot.model')
        new_model = model

    ############################################################################################
    #######################################  START CHATBOT #####################################
    ############################################################################################
    question = nltk.word_tokenize(question)
    question = [stemmer.stem(word.lower(
    )) for word in question if word not in "?" if word not in "!"if word not in ","]

    bag_of_words = np.zeros(len(dictionary))

    bag_of_words = bag_of_words.reshape(D, 1).T

    for i in range(D):

        word = dictionary[i]
        if word in question:
            bag_of_words[0][i] = 1
        else:
            bag_of_words[0][i] = 0

    prediction = new_model.predict(bag_of_words)[0]
    index_of_the_most_probable_prediction = np.argmax(prediction)

    result = classes[np.argmax(prediction)]

    if prediction[index_of_the_most_probable_prediction] > 0.4:

        for classe in data["intents"]:
            if classe["class"] == result:
                responses = classe["responses"]

    else:
        responses = ["No he entendido lo que has dicho, aún estoy aprendiendo :), mejor intentalo de nuevo",
                     "Soy un Bot...no té he entendido, mejor prueba de nuevo! :)", "No pillé lo que has dicho :(, porfa intentalo otra vez!"]

    return random.choice(responses)
