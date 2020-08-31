import os
from time import time

import essentia.standard
import essentia.streaming
import pretty_midi


def extract_melody_from_midi(file_name):
    mid = pretty_midi.PrettyMIDI(file_name)
    new_mid_notes = []
    avg_data = []

    if len(mid.time_signature_changes) == 0:
        num = 4
        denom = 4
    else:
        num = mid.time_signature_changes[0].numerator
        denom = mid.time_signature_changes[0].denominator

    resolution = mid.resolution
    ticks_per_note = num * (resolution / (denom / 4))
    total_bars = int(mid.time_to_tick(mid.get_end_time()) // ticks_per_note)

    for current_channel, instrument in enumerate(mid.instruments):
        if instrument.is_drum:
            continue

        ch = []
        avg_data_ch = {}
        bar = {}
        sum_pitch = 0
        sum_dur = 0
        current_bar = int(mid.time_to_tick(instrument.notes[0].start) // ticks_per_note)

        for index, note in enumerate(instrument.notes):
            starting_tick = mid.time_to_tick(note.start)
            nro_bar = int(starting_tick // ticks_per_note)

            if nro_bar != current_bar:
                notes_per_bar = len(bar.keys())
                avg_data_ch[current_bar] = (sum_pitch / notes_per_bar, sum_dur / notes_per_bar)
                ch.append(bar)
                bar = {}
                current_bar = nro_bar
                sum_pitch = sum_dur = 0

            if starting_tick not in bar.keys():
                # We substract 12 pitch levels if
                # the note belongs to a different clef
                sum_pitch += note.pitch if note.pitch < 60 else (note.pitch - 13)
                sum_dur += note.get_duration()
                bar[starting_tick] = (
                    note.pitch, current_channel, nro_bar, mid.time_to_tick(note.end), mid.time_to_tick(note.duration),
                    note.velocity)
            else:
                # If the current note overlaps with a previous one
                # (they play at the same time/tick)
                # we will keep the one with the highest pitch
                if note.pitch > bar[starting_tick][0]:
                    old_note_pitch = bar[mid.time_to_tick(note.start)][0]

                    sum_pitch -= old_note_pitch if old_note_pitch else (old_note_pitch - 13)
                    sum_dur -= mid.tick_to_time(bar[starting_tick][4])

                    sum_pitch += note.pitch if note.pitch < 60 else (note.pitch - 13)
                    sum_dur += note.get_duration()

                    bar[starting_tick] = (
                        note.pitch, current_channel, nro_bar, mid.time_to_tick(note.end),
                        mid.time_to_tick(note.duration), note.velocity)

        notes_per_bar = len(bar.keys())
        avg_data_ch[current_bar] = (sum_pitch / notes_per_bar, sum_dur / notes_per_bar)
        ch.append(bar)

        new_mid_notes.append(ch)
        avg_data.append(avg_data_ch)

    print("================================================================")

    melody_route = {}

    # For each instant of time, get
    # the bar with the highest pitch
    for i in range(0, total_bars):
        selected_channel = (-1, -1)

        for index, channel in enumerate(avg_data):
            if i in channel.keys():
                bar_avg_pitch = channel[i][0]

                if bar_avg_pitch > selected_channel[1]:
                    selected_channel = (index, bar_avg_pitch)

        melody_route[i] = selected_channel[0]

    vis_pitch = []

    for bar_index, selected_channel in melody_route.items():
        if selected_channel == -1:
            continue

        for original_channel in new_mid_notes[selected_channel]:
            channel_keys = list(original_channel.keys())
            first_key = channel_keys[0]

            if bar_index == original_channel[first_key][2]:
                for tiempo in original_channel:
                    vis_pitch.append(original_channel[tiempo][0])

                break

    return vis_pitch


def extract_melody_from_wav(file_name):
    loader_db = essentia.standard.EqloudLoader(filename=file_name, sampleRate=44100)
    audio_db = loader_db()
    pitch_extractor_db = essentia.standard.PredominantPitchMelodia()
    pitch_values_db, pitch_confidence_db = pitch_extractor_db(audio_db)
    contour_extractor_db = essentia.standard.PitchContourSegmentation()
    _onset_db, _duration_db, _MIDI_pitch_db = contour_extractor_db(pitch_values_db, audio_db)

    return _onset_db, _duration_db, _MIDI_pitch_db


global_source_path = 'dataset/sources/'
global_destination_path = 'dataset/melodies/'

wavs = os.listdir(global_source_path + 'wavs/')
midis = os.listdir(global_source_path + 'midis/')

for song in wavs:
    start_time = time()
    _, _, melody = extract_melody_from_wav(global_source_path + 'wavs/' + song)

    with open(global_destination_path + 'wavs/' + song + '.txt', 'w') as writer:
        writer.write(','.join(str(e) for e in melody))

    elapsed_time = time() - start_time
    print('Elapsed time: %f' % elapsed_time)
    print(song)

for song in midis:
    start_time = time()
    melody = extract_melody_from_midi(global_source_path + 'midis/' + song)

    with open(global_destination_path + 'midis/' + song + '.txt', 'w') as writer:
        writer.write(','.join(str(e) for e in melody))

    elapsed_time = time() - start_time
    print(song)
    print('Elapsed time: %f' % elapsed_time)
