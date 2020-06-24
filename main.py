import pretty_midi
import matplotlib.pyplot as plt

first_file_name = 'chumbawamba_i_get_knocked_down_1'
second_file_name = 'chumbawamba_i_get_knocked_down_2'


def process_file(file_name):
    mid = pretty_midi.PrettyMIDI('dataset/' + file_name + '.mid')
    print("Total ticks:", mid.time_to_tick(mid.get_end_time()))
    print("Time signatures:", mid.time_signature_changes)
    print("Resolution:", mid.resolution)
    # help(pretty_midi.Note)
    new_mid = pretty_midi.PrettyMIDI()
    new_ch = pretty_midi.Instrument(0)
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
    defined_values = [1, 2, 4, 8, 16, 32, 3, 6, 12, 24, 48]

    def pitch_to_freq(_note):
        return 2 ** ((_note - 69) / 12) * 440

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
                new_pitch = note.pitch if note.pitch < 60 else (note.pitch - 13)

                if new_pitch > bar[starting_tick][0]:
                    old_note_pitch = bar[mid.time_to_tick(note.start)][0]
                    old_note_duration = mid.tick_to_time(bar[starting_tick][4])

                    sum_pitch -= old_note_pitch
                    sum_dur -= old_note_duration

                    sum_pitch += new_pitch
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

    visualization = []
    vis_pitch = []
    vis_ticks = []

    for bar_index, selected_channel in melody_route.items():
        if selected_channel == -1:
            continue

        for original_channel in new_mid_notes[selected_channel]:
            channel_keys = list(original_channel.keys())
            first_key = channel_keys[0]

            if bar_index == original_channel[first_key][2]:
                for time in original_channel:
                    note = pretty_midi.Note(velocity=original_channel[time][5], pitch=original_channel[time][0],
                                            start=mid.tick_to_time(time),
                                            end=mid.tick_to_time(original_channel[time][3]))
                    new_ch.notes.append(note)
                    vis_pitch.append(original_channel[time][0])
                    vis_ticks.append(mid.tick_to_time(time))

                break

    visualization += [vis_ticks, vis_pitch]

    new_mid.instruments.append(new_ch)
    new_mid.write(file_name + '.mid')

    return visualization


first_graph = process_file(first_file_name)
second_graph = process_file(second_file_name)
plt.plot(*first_graph, *second_graph)
plt.show()
