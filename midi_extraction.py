import pretty_midi


def extract_notes(midi_handler: pretty_midi.PrettyMIDI):
    print("Total ticks:", midi_handler.time_to_tick(midi_handler.get_end_time()))
    print("Time signatures:", midi_handler.time_signature_changes)
    print("Resolution:", midi_handler.resolution)
    new_mid_notes = []
    avg_data = []

    if len(midi_handler.time_signature_changes) == 0:
        num = 4
        denom = 4
    else:
        num = midi_handler.time_signature_changes[0].numerator
        denom = midi_handler.time_signature_changes[0].denominator

    resolution = midi_handler.resolution
    ticks_per_bar = num * (resolution / (denom / 4))
    total_bars = int(midi_handler.time_to_tick(midi_handler.get_end_time()) // ticks_per_bar)

    for current_channel, instrument in enumerate(midi_handler.instruments):
        if instrument.is_drum:
            continue

        ch = []
        avg_data_ch = {}
        bar = {}
        sum_pitch = 0
        sum_dur = 0
        current_bar = int(midi_handler.time_to_tick(instrument.notes[0].start) // ticks_per_bar)

        for index, note in enumerate(instrument.notes):
            starting_tick = midi_handler.time_to_tick(note.start)
            nro_bar = int(starting_tick // ticks_per_bar)

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
                    note.pitch, current_channel, nro_bar, midi_handler.time_to_tick(note.end),
                    midi_handler.time_to_tick(note.duration),
                    note.velocity)
            else:
                # If the current note overlaps with a previous one
                # (they play at the same time/tick)
                # we will keep the one with the highest pitch
                new_pitch = note.pitch if note.pitch < 60 else (note.pitch - 13)
                old_pitch = bar[starting_tick][0] if bar[starting_tick][0] < 60 else (bar[starting_tick][0] - 13)

                if new_pitch > old_pitch:
                    old_duration = midi_handler.tick_to_time(bar[starting_tick][4])

                    sum_pitch -= old_pitch
                    sum_dur -= old_duration

                    sum_pitch += new_pitch
                    sum_dur += note.get_duration()

                    bar[starting_tick] = (
                        note.pitch, current_channel, nro_bar, midi_handler.time_to_tick(note.end),
                        midi_handler.time_to_tick(note.duration), note.velocity)

        notes_per_bar = len(bar.keys())
        avg_data_ch[current_bar] = (sum_pitch / notes_per_bar, sum_dur / notes_per_bar)
        ch.append(bar)

        new_mid_notes.append(ch)
        avg_data.append(avg_data_ch)

    return [avg_data, new_mid_notes, total_bars]


def generate_melody(average_data, total_bars):
    melody_route = {}

    # For each instant of time, get
    # the bar with the highest pitch
    for i in range(0, total_bars):
        selected_channel = (-1, -1)

        for index, channel in enumerate(average_data):
            if i in channel.keys():
                bar_avg_pitch = channel[i][0]

                if bar_avg_pitch > selected_channel[1]:
                    selected_channel = (index, bar_avg_pitch)

        melody_route[i] = selected_channel[0]

    return melody_route


def extract_melody_from_midi(source_path, file_name, destination_path='', generate_midi=False, generate_graph=False,
                             save_to_file=False):
    mid_handler = pretty_midi.PrettyMIDI(source_path + file_name)
    [avg_data, new_mid_notes, total_bars] = extract_notes(mid_handler)
    melody_route = generate_melody(avg_data, total_bars)
    new_mid = pretty_midi.PrettyMIDI()
    new_ch = pretty_midi.Instrument(0)

    visualization = []
    vis_pitch = []
    vis_ticks = []
    pitch_list = []

    for bar_index, selected_channel in melody_route.items():
        if selected_channel == -1:
            continue

        for original_channel in new_mid_notes[selected_channel]:
            channel_keys = list(original_channel.keys())
            first_key = channel_keys[0]

            if bar_index == original_channel[first_key][2]:
                for time in original_channel:
                    if generate_midi:
                        note = pretty_midi.Note(velocity=original_channel[time][5], pitch=original_channel[time][0],
                                                start=mid_handler.tick_to_time(time),
                                                end=mid_handler.tick_to_time(original_channel[time][3]))
                        new_ch.notes.append(note)

                    if generate_graph:
                        vis_pitch.append(original_channel[time][0])
                        vis_ticks.append(mid_handler.tick_to_time(time))

                    if save_to_file:
                        pitch_list.append(original_channel[time][0])

                break

    if generate_midi:
        new_mid.instruments.append(new_ch)
        new_mid.write(file_name)

    if generate_graph:
        visualization += [vis_ticks, vis_pitch]

    if save_to_file:
        if destination_path is not '':
            destination_file = destination_path + file_name
        else:
            destination_file = source_path + file_name

        with open(destination_file + '.txt', 'w') as writer:
            writer.write(','.join(str(e) for e in pitch_list))

    return [vis_pitch, visualization]
