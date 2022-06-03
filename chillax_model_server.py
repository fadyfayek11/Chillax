import json
import pyarabic.trans as pas
from chillax_models import make_depression_prediction, make_hs_prediction, make_offensive_prediction
import win32pipe, win32file
import sys
import traceback
import logging

def segment_message(message):
    ar_text = ""
    non_ar_text = ""
    msg_segmented = pas.segment_language(message)
    for segment in msg_segmented:
        if segment[0] == 'arabic':
            ar_text += f' {segment[1]}'
        else:
            non_ar_text += f' {segment[1]}'
    return (ar_text, non_ar_text)

PIPE_NAME = r'\\.\pipe\ChillaxSocket'

pipe = win32pipe.CreateNamedPipe(
    PIPE_NAME,
    win32pipe.PIPE_ACCESS_DUPLEX,
    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
    1, 65536, 65536,
    0,
    None)

# try:
while True:
    try:
        print("waiting for client")
        win32pipe.ConnectNamedPipe(pipe, None)
        print("client connected")
        bytes_to_read = int(win32file.ReadFile(pipe, 4, None)[1].decode('utf-8'))
        client_message = win32file.ReadFile(pipe, bytes_to_read, None)[1].decode('utf-8')
        json_message = json.loads(client_message)
        print('Received message: ', json_message['Message'])
        segmented_message = segment_message(json_message["Message"])
        off_prediction = make_offensive_prediction(segmented_message[0])
        hs_prediction = make_hs_prediction(segmented_message[0])
        depression_prediction = make_depression_prediction(segmented_message[1])
        is_off = False
        is_hs = False
        is_depression = False
        if off_prediction[0] == 1:
            is_off = True
        if hs_prediction[0] == 1:
            is_hs = True
        if depression_prediction == 1:
            is_depression = True
        response = json.dumps({'IsOffensive': is_off, 'IsHatespeech': is_hs, 'IsDepression': is_depression, 'Message': json_message['Message']})
        win32file.WriteFile(pipe, len(response.encode('utf-8')).to_bytes(4, sys.byteorder))
        win32file.WriteFile(pipe, response.encode('utf-8'))
        print(f'response sent: {response}')        
    except Exception as e:
        print(traceback.format_exc())
        win32pipe.DisconnectNamedPipe(pipe)      
         

