import essentia.standard
from dtw import *
import os
import pretty_midi
from time import time
import tslearn.metrics
from collections import OrderedDict
import librosa.feature
import numpy as np
import argparse
from pathlib import Path
import json


def calculate_gradient_vector(melody):
    _gradients = []

    for index, note in enumerate(melody):
        if index == 0:
            continue

        _gradients.append(note - melody[index - 1])

    return _gradients


def read_melody_files(filename):
    with open(filename) as f:
        _notes = f.read()

    _notes = _notes.split(',')
    return [float(i) for i in _notes]


def normalize(series, mmin, mmax):
    return [((i - mmin) / (mmax - mmin)) for i in series]


def findSong(file_path):
    melodies_path = 'dataset/chromas/vocals/'
    melodies = os.listdir(melodies_path)

    results = {}
    print("........" + hum + "........")
    print("----------")
    loader = essentia.standard.EqloudLoader(filename=file_path, sampleRate=44100)
    audio = loader()
    pitch_extractor = essentia.standard.PredominantPitchMelodia(frameSize=2048, hopSize=50)
    pitch_values, pitch_confidence = pitch_extractor(audio)
    pitch_values = pitch_values[pitch_values != 0]
    chroma = librosa.feature.chroma_stft(y=np.asarray(pitch_values), sr=44100, hop_length=50)

    for melodie in melodies:
        chroma_db = np.loadtxt(melodies_path + melodie)
        alignment = dtw(chroma.transpose(), chroma_db, step_pattern=rabinerJuangStepPattern(6, "c"),
                        keep_internals=False, open_begin=True, open_end=True)
        results[melodie] = alignment.distance

    ordered_results = OrderedDict({k: v for k, v in sorted(results.items(), key=lambda item: item[1])})

    return ordered_results


parser = argparse.ArgumentParser(description='Identify a song from a humming audio file.')
parser.add_argument('humming_path', metavar='N', nargs=1,
                    help='The absolute path of the humming audio file')

args = parser.parse_args()
humming_path = ''.join(args.humming_path)

file_path = Path(humming_path)
if not file_path.is_file():
    print('{}')

results = findSong(file_path)

print(json.dumps(results))
