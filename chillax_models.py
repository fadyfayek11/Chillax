from transformers import AutoTokenizer, TFAutoModel
import tensorflow as tf
import pickle
import numpy as np
import re
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import string
from keras_preprocessing.sequence import pad_sequences
import tensorflow_hub as hub
import tensorflow_text as text

def __get_depression_model():
    # Bert layers
    text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
    preprocessed_text = bert_preprocess_model(text_input)
    outputs = bert_encoder(preprocessed_text)

    # Neural network layers
    l = tf.keras.layers.Dropout(0.1, name="dropout")(outputs['pooled_output'])
    l = tf.keras.layers.Dense(1, activation='sigmoid', name="output")(l)
    ##

    # Use inputs and outputs to construct a final model
    model = tf.keras.Model(inputs=[text_input], outputs = [l])
    return model

bert_preprocess_model = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")
bert_encoder = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4")

depression_model = __get_depression_model()

depression_model.load_weights('./PredictionModels/depression_bert_weights.h5')

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
    X = tf.convert_to_tensor(np.array([preprocessed_text]), dtype=tf.string)
    prediction = depression_model(X)
    if prediction[0] >= 0.5:
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
    
    return new_tweet

# while True:
#     input_text = input("enter text:")
#     choice = int(input("predict:\n1-Off & HS\n2-Depression\n"))
#     if choice == 1:
#         print(f'Offensive: {make_offensive_prediction(input_text)}, Hatespeech: {make_hs_prediction(input_text)}')
#     elif choice == 2:
#         print(f'Depression: {make_depression_prediction(input_text)}')
#     else:
#         break


