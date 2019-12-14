from scipy.io import wavfile
from app.main import checker_model as heartbeat_checker
from app.main import graph
import numpy as np
import librosa
from scipy import signal

from .fun import preprocess


def load_wav_file(name, path):
    _, b = wavfile.read(path + name)
    return b


def repeat_to_length(arr, length):
    result = np.empty((length, ), dtype = 'float32')
    l = len(arr)
    pos = 0
    while pos + l <= length:
        result[pos:pos+l] = arr
        pos += l
    if pos < length:
        result[pos:length] = arr[:length-pos]
    return result


def audio_norm(data):
    max_data = np.max(data)
    min_data = np.min(data)
    data = (data-min_data)/(max_data-min_data+1e-6)
    return data-0.5


def mfcc_transforamtion(audio):
    return np.array([np.array(librosa.feature.mfcc(y=audio[:48000], 
                                                                    sr=16000, n_mfcc=80))])


def evaluate(audio):
    audio = repeat_to_length(audio, 160000)
    example = repeat_to_length(
        wavfile.read('./app/main/util/checker/example.wav')[1].astype(float), 160000)

    audio = audio_norm(preprocess(audio, 16000, 'lowpass'))
    example = audio_norm(preprocess(example, 16000, 'lowpass'))
    
    with graph.as_default():
        return heartbeat_checker.predict([mfcc_transforamtion(example), 
                            mfcc_transforamtion(audio)])[0][0]
