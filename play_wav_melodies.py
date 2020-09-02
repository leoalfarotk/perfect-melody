import os
from time import time

import pretty_midi

from wav_extraction import extract_melody_from_wav

global_source_path = 'dataset/sources/'
global_destination_path = 'dataset/built_midis/'

wavs = os.listdir(global_source_path + 'wavs/')

for song in wavs:
    start_time = time()
    notes_time, notes_duration, notes = extract_melody_from_wav(global_source_path + 'wavs/' + song)

    new_mid = pretty_midi.PrettyMIDI()
    new_ch = pretty_midi.Instrument(0)

    for x in range(0, len(notes)):
        note = pretty_midi.Note(pitch=int(notes[x]), velocity=100, start=notes_time[x],
                                end=notes_time[x] + notes_duration[x])
        new_ch.notes.append(note)

    new_mid.instruments.append(new_ch)
    new_mid.write(global_destination_path + song + '.mid')

    elapsed_time = time() - start_time
    print('____________________')
    print(song)
    print('Elapsed time: %f' % elapsed_time)
