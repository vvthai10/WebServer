import os
import pandas as pd
import re
import gensim
import pickle
from sklearn import preprocessing
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn import linear_model

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

# HANDLE PROCESSING DATA
def get_stopwords():
    stopword_path = os.path.join(CURRENT_PATH, "data/vnest_stopwords.txt")
    with open(stopword_path, 'r', encoding='utf-8') as f:
        stopwords = [line.strip() for line in f]

    return stopwords

def preprocessing_doc(doc, stopwords):
    lines = gensim.utils.simple_preprocess(doc)
    lines = [word for word in lines if word not in stopwords]
    lines = ' '.join(lines)
    return lines

def processing_data(train=False, stopwords=None):

    train_text_command_path = os.path.join(CURRENT_PATH, "data/train_text_command.csv")
    X_data_path = os.path.join(CURRENT_PATH, "data/X_data.pkl")
    Y_data_path = os.path.join(CURRENT_PATH, "data/y_data.pkl")

    if train:
        
        df = pd.read_csv(train_text_command_path)
        X_data = df["sentence"].to_numpy()
        # y_data = np.unique(df["command"].to_numpy())
        y_data = df["command"].to_numpy()

        for i in range(len(X_data)):
            lines = X_data[i]
            # lines = ' '.join(lines)
            X_data[i] = preprocessing_doc(lines, stopwords)
            
        pickle.dump(X_data, open(X_data_path, 'wb'))
        pickle.dump(y_data, open(Y_data_path, 'wb'))
    else:
        X_data = pickle.load(open(X_data_path, 'rb'))
        y_data = pickle.load(open(Y_data_path, 'rb'))

    print("Length of X: ", X_data.shape)
    
    return X_data, y_data

def processing_vector(train=False, X_data = None):
    tfidf_vect_path = os.path.join(CURRENT_PATH, "data/tfidf_vect.pkl")
    if train:
        tfidf_vect = TfidfVectorizer(analyzer='word', max_features=30000)
        tfidf_vect.fit(X_data) # learn vocabulary and idf from training set
        with open(tfidf_vect_path, 'wb') as file:
            pickle.dump(tfidf_vect, file)
    else:
        with open(tfidf_vect_path, 'rb') as file:
            tfidf_vect = pickle.load(file)

    return tfidf_vect

# HANDLE MODEL
def train_model(classifier, X_data, y_data, is_neuralnet=False, n_epochs=3):       
    X_train, X_val, y_train, y_val = train_test_split(X_data, y_data, test_size=0.1, random_state=42)
    
    if is_neuralnet:
        classifier.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=n_epochs, batch_size=16)
        val_predictions = classifier.predict(X_val)
        val_predictions = val_predictions.argmax(axis=-1)
    else:
        classifier.fit(X_train, y_train)
    
        train_predictions = classifier.predict(X_train)
        val_predictions = classifier.predict(X_val)
        
    print("Validation accuracy: ", metrics.accuracy_score(val_predictions, y_val))

def train():
    stopwords = get_stopwords()
    X_data, y_data = processing_data(train=True, stopwords=stopwords)
    tfidf_vect = processing_vector(train=True, X_data=X_data)

    X_data_tfidf =  tfidf_vect.transform(X_data)

    print("Traning model...")
    encoder = preprocessing.LabelEncoder()
    y_data = encoder.fit_transform(y_data)

    encoder_path = os.path.join(CURRENT_PATH, "data/encoder.pkl")
    with open(encoder_path, 'wb') as file:
        pickle.dump(encoder, file)  
    
    model = linear_model.LogisticRegression()
    train_model(model, X_data_tfidf, y_data, is_neuralnet=False)

    model_path = os.path.join(CURRENT_PATH, "model/model.pkl")
    with open(model_path, 'wb') as file:
        pickle.dump(model, file)

# ======== USE MODEL TO PREDICT ========
def get_command(sentence):
    encoder_path = os.path.join(CURRENT_PATH, "data/encoder.pkl")
    model_path = os.path.join(CURRENT_PATH, "model/model.pkl")

    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    stopwords = get_stopwords()
    sen = preprocessing_doc(sentence, stopwords)
    tfidf_vect = processing_vector()
    sen_tfidf = tfidf_vect.transform([sen])


    with open(encoder_path, 'rb') as file:
        encoder = pickle.load(file)

    predict = model.predict(sen_tfidf)
    classes = encoder.classes_
    print(classes)
    print(predict)

    message = {"type": classes[predict][0]}

    if classes[predict] == "call" or classes[predict] == "metting":
        pattern = r"\b\d+\s?giờ\b"
        matches = re.findall(pattern, sentence)
        message["time"] = matches[0]
    
    print("Thông tin res: ", message)

    return message

if __name__ == "__main__":
    TRAIN = False
    if TRAIN:
        train()

    # TODO Test model
    sentence = "Hỗ trợ"
    get_command(sentence)
