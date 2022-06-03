from transformers import AutoTokenizer, TFAutoModel
import tensorflow as tf
import pickle
import numpy as np
from keras.models import model_from_json
import re
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import string
from keras.models import model_from_json
from keras.preprocessing.sequence import pad_sequences

with open('./PredictionModels/depression_model.json') as depression_json:
    depression_model = model_from_json(depression_json.read())

depression_model.load_weights('./PredictionModels/weights.h5')

depression_tokenizer = pickle.load(open('./PredictionModels/depression_tokenizer.pkl', 'rb'))

marbert_model_path = 'UBC-NLP/MARBERT'
tokenizer = AutoTokenizer.from_pretrained(marbert_model_path, from_tf=True)
marbert_model = TFAutoModel.from_pretrained(
    marbert_model_path, output_hidden_states=True)

off_scaler = pickle.load(open('./PredictionModels/offensive_scaler.pkl', 'rb'))
off_lr_model = pickle.load(open('./PredictionModels/lr_offensive_model.sav', 'rb'))

hs_scaler = pickle.load(open('./PredictionModels/hs_scaler.pkl', 'rb'))
hs_lr_model = pickle.load(open('./PredictionModels/lr_hs_model.sav', 'rb'))

def __bert_tokenize(text: str, tokenizer) -> list:
    max_len = len(tokenizer.tokenize(f'[CLS] {text} [SEP]'))
    tokens = tokenizer(text, padding='max_length',
                       truncation=True, max_length=max_len)
    return (np.expand_dims(np.array(tokens['input_ids']), 0), np.expand_dims(np.array(tokens['attention_mask']), 0), np.expand_dims(np.array(tokens['token_type_ids']), 0))

def __get_embeddings(tokens):
    ids = tf.convert_to_tensor(tokens[0])
    mask = tf.convert_to_tensor(tokens[1])
    type_ids = tf.convert_to_tensor(tokens[2])
    hidden_states = marbert_model(
        input_ids=ids, attention_mask=mask, token_type_ids=type_ids)[2]
    sentence_embd = tf.reduce_mean(tf.reduce_sum(
        tf.stack(hidden_states[-4:]), axis=0), axis=1)
    return sentence_embd

def __get_features(text, tokenizer):
    inputs = __bert_tokenize(text, tokenizer)
    return __get_embeddings(inputs)

def make_offensive_prediction(text):
    features = __get_features(text, tokenizer)
    features = off_scaler.transform(features)
    return off_lr_model.predict(features)

def make_hs_prediction(text):
    features = __get_features(text, tokenizer)
    features = hs_scaler.transform(features)
    return hs_lr_model.predict(features)

def make_depression_prediction(text):
    preprocessed_text = __preprocess_depression(text)
    texts = []
    texts.append(preprocessed_text)
    X = depression_tokenizer.texts_to_sequences(texts)
    X = pad_sequences(X,maxlen=300)
    prediction = depression_model(X)
    if prediction[0] >= 0.6:
        return 1
    return 0

def __preprocess_depression(tweet):
    username = "@\S+"
    new_tweet = re.sub(username, ' ',tweet) # Remove @tags
    
    new_tweet = new_tweet.lower() # Smart lowercase
    
    new_tweet = re.sub(r'\d+', ' ', new_tweet) # Remove numbers
    
    text_noise = "https?:\S+|http?:\S|[^A-Za-z0-9]+" 
    new_tweet = re.sub(text_noise, ' ', new_tweet) # Remove links
    
    new_tweet = new_tweet.translate(new_tweet.maketrans('','',string.punctuation)) # Remove Punctuation
    
    new_tweet = new_tweet.strip() # Remove white spaces
    
    new_tweet = word_tokenize(new_tweet) # Tokenize into words
    
    new_tweet = ' '.join([word for word in new_tweet if word.isalpha()]) # Remove non alphabetic tokens
    
    stop_words = set(stopwords.words('english'))
    new_tweet = ' '.join([word for word in new_tweet.split() if not word in stop_words]) # Filter out stop words
    
    lemmatizer = WordNetLemmatizer()
    new_tweet = ' '.join([lemmatizer.lemmatize(word,"v") for word in new_tweet.split()]) # Word Lemmatization
    
    return new_tweet