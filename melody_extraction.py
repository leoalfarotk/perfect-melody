import os
from time import time

from midi_extraction import extract_melody_from_midi
from wav_extraction import extract_melody_from_wav


def extract_melodies(run_wavs=False, run_midis=False):
    global_source_path = 'dataset/sources/'
    global_destination_path = 'dataset/melodies/'

    if run_wavs:
        print('==============================')
        wavs = os.listdir(global_source_path + 'wavs/')

        for song in wavs:
            start_time = time()
            _, _, melody = extract_melody_from_wav(global_source_path + 'wavs/' + song)

            with open(global_destination_path + 'wavs/' + song + '.txt', 'w') as writer:
                writer.write(','.join(str(e) for e in melody))

            elapsed_time = time() - start_time
            print('____________________')
            print(song)
            print('Elapsed time: %f' % elapsed_time)

    if run_midis:
        print('==============================')
        midis = os.listdir(global_source_path + 'midis/')

        for song in midis:
            start_time = time()
            extract_melody_from_midi(global_source_path + 'midis/', song,
                                     destination_path=global_destination_path + 'midis/', save_to_file=True)

            elapsed_time = time() - start_time
            print('____________________')
            print(song)
            print('Elapsed time: %f' % elapsed_time)


extract_melodies(run_wavs=False, run_midis=False)
