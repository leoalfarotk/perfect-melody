import os
from time import time

import essentia.standard
import essentia.streaming
from dtw import *


def dynamic_alignment(cut_size, _song, hum):
    i = 0
    min_distance = float('Inf')
    best_i = i

    while i < len(_song):
        ini = i
        fin = ini + cut_size - 1
        if fin > len(_song) - 1:
            fin = len(_song) - 1
        alignment = dtw(hum, _song[ini:fin], keep_internals=True)
        if alignment.distance < min_distance:
            min_distance = alignment.distance
            best_i = i
        i = i + cut_size

    ini = best_i
    fin = ini + cut_size - 1

    if fin > len(_song) - 1:
        fin = len(_song) - 1
        # Penalization due to a shorter
        # subsequence than the humming's length
        min_distance += 50

    # Show graph for analysis purposes
    dtw(hum, _song[ini:fin], keep_internals=True,
        step_pattern=rabinerJuangStepPattern(6, "c")) \
        .plot(type="twoway", offset=-2)

    return min_distance


def process_humming(filename):
    loader = essentia.standard.EqloudLoader(filename=filename, sampleRate=44100)
    audio = loader()
    pitch_extractor = essentia.standard.PredominantPitchMelodia(frameSize=2048, hopSize=128)
    pitch_values, pitch_confidence = pitch_extractor(audio)
    contour_extractor = essentia.standard.PitchContourSegmentation()
    _onset, _duration, _MIDI_pitch = contour_extractor(pitch_values, audio)

    return _onset, _duration, _MIDI_pitch


def read_melody_files(filename):
    with open(filename) as f:
        _notes = f.read()

    _notes = _notes.split(',')
    return [float(i) for i in _notes]


global_path = 'dataset/melodies/'
wavs = os.listdir(global_path + 'wavs/')
midis = os.listdir(global_path + 'midis/')

_, _, hummed_melody = process_humming('dataset/hummings/all_star.wav')

print('Running dynamic approach')
print('Using wav files...')

for song in wavs:
    melody = read_melody_files(global_path + 'wavs/' + song)
    start_time = time()
    distance = dynamic_alignment(len(hummed_melody), melody, hummed_melody)
    elapsed_time = time() - start_time
    print('___________________________')
    print(song)
    print('Elapsed time: %f' % elapsed_time)
    print('DTW distance: %f' % distance)

print('================================================')
print('================================================')

print('Using MIDI files...')

for song in midis:
    melody = read_melody_files(global_path + 'midis/' + song)
    start_time = time()
    distance = dynamic_alignment(len(hummed_melody), melody, hummed_melody)
    elapsed_time = time() - start_time
    print('___________________________')
    print(song)
    print('Elapsed time: %f' % elapsed_time)
    print('DTW distance: %f' % distance)

print('================================================')
print('================================================')
print('================================================')
print('================================================')

print('Running static approach')
