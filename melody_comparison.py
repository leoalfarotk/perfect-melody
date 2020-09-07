import os
from time import time
from collections import OrderedDict

import essentia.standard
import essentia.streaming
import numpy as np
from dtw import *


def dynamic_alignment(cut_size, _song, hum, show_graph=False):
    i = 0
    min_distance = float('Inf')
    best_i = i

    while i < len(_song):
        ini = i
        fin = ini + cut_size - 1
        if fin > len(_song) - 1:
            break
            # fin = len(_song) - 1
        alignment = dtw(hum, _song[ini:fin], keep_internals=True, open_end=True)

        if alignment.distance < min_distance:
            min_distance = alignment.distance
            best_i = i

        # print(len(hum))
        # print(len(_song[ini:fin]))
        # alignment = np.corrcoef(hum, _song[ini:fin])
        # coeff = 1 - abs(alignment[0][1])
        # if coeff < min_distance:
        # min_distance = coeff
        # best_i = i
        i = i + cut_size

    ini = best_i
    fin = ini + cut_size - 1

    if fin > len(_song) - 1:
        fin = len(_song) - 1
        # Penalization due to a shorter
        # subsequence than the humming's length
        min_distance += 50

    # Show graph for analysis purposes
    if show_graph:
        dtw(hum, _song[ini:fin], keep_internals=True, open_end=True,
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

    return _onset, _duration, pitch_values


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


def run_comparison(humming_filename):
    global_path = 'dataset/melodies/'
    wavs = os.listdir(global_path + 'wavs/')
    midis = os.listdir(global_path + 'midis/')

    _, _, hummed_melody = process_humming('dataset/hummings/' + humming_filename)
    hummed_melody_gradient = calculate_gradient_vector(hummed_melody)

    print('Comparing with wav files...')

    wav_results = {}
    midi_results = {}

    for song in wavs:
        melody = read_melody_files(global_path + 'wavs/' + song)
        # start_time = time()
        distance = dynamic_alignment(len(hummed_melody), melody, hummed_melody)
        # gradients = calculate_gradient_vector(melody)
        # distance = dynamic_alignment(len(hummed_melody), gradients, hummed_melody_gradient)
        # elapsed_time = time() - start_time
        wav_results[song] = distance
        # print('___________________________')
        # print(melody)
        # print(gradients)
        # print('Elapsed time: %f' % elapsed_time)
        # print('DTW distance: %f' % distance)

    ordered_wav_result = OrderedDict({k: v for k, v in sorted(wav_results.items(), key=lambda item: item[1])})

    print('Comparing with MIDI files...')

    if False:
        for song in midis:
            melody = read_melody_files(global_path + 'midis/' + song)
            # start_time = time()
            distance = dynamic_alignment(len(hummed_melody), melody, hummed_melody)
            # distance = np.corrcoef(hummed_melody, melody)
            # gradients = calculate_gradient_vector(melody)
            # distance = dynamic_alignment(len(hummed_melody), gradients, hummed_melody_gradient)
            # elapsed_time = time() - start_time
            midi_results[song] = distance
            # print('___________________________')
            # print(song)
            # print(melody)
            # print(gradients)
            # print('Elapsed time: %f' % elapsed_time)
            # print('DTW distance: %f' % distance)

        ordered_midi_result = OrderedDict({k: v for k, v in sorted(midi_results.items(), key=lambda item: item[1])})

    print('Results for ' + humming_filename + ':')
    print('Wav:')
    for key, value in ordered_wav_result.items():
        print(value, key)

    if False:
        print('Midi:')
        for key, value in ordered_midi_result.items():
            print(value, key)
