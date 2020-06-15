import pretty_midi

mid = pretty_midi.PrettyMIDI('dataset/iceice.mid')
print("Total ticks:", mid.time_to_tick(mid.get_end_time()))
print("Time signatures:", mid.time_signature_changes)
print("Resolution:", mid.resolution)
# help(pretty_midi.Note)
new_mid_notes = []
avg_data = []
num = mid.time_signature_changes[0].numerator
denom = mid.time_signature_changes[0].denominator
resolution = mid.resolution
ticks_per_note = num * (resolution / (denom / 4))


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
            sum_pitch += note.pitch if note.pitch < 60 else (note.pitch - 12)
            sum_dur += note.get_duration()
            bar[starting_tick] = (
                note.pitch, current_channel, nro_bar, mid.time_to_tick(note.end), mid.time_to_tick(note.duration))
        else:
            # If the current note overlaps with a previous one
            # (they play at the same time/tick)
            # we will keep the one with the highest pitch
            if note.pitch > bar[starting_tick][0]:
                old_note_pitch = bar[mid.time_to_tick(note.start)][0]

                sum_pitch -= old_note_pitch if old_note_pitch else (old_note_pitch - 12)
                sum_dur -= mid.tick_to_time(bar[starting_tick][4])

                sum_pitch += note.pitch if note.pitch < 60 else (note.pitch - 12)
                sum_dur += note.get_duration()

                bar[starting_tick] = (
                    note.pitch, current_channel, nro_bar, mid.time_to_tick(note.end), mid.time_to_tick(note.duration))

    notes_per_bar = len(bar.keys())
    avg_data_ch[current_bar] = (sum_pitch / notes_per_bar, sum_dur / notes_per_bar)
    ch.append(bar)

    new_mid_notes.append(ch)
    avg_data.append(avg_data_ch)

for channel in new_mid_notes:
    for bar in channel:
        for starting_tick in bar:
            print("nota:{}  canal:{}  bar:{}  inicio:{}".format(bar[starting_tick][0], bar[starting_tick][1],
                                                                bar[starting_tick][2], starting_tick))

print("================================================================")

for channel in avg_data:
    for bar in channel:
        print("bar:{} avg_pitch: {} avg_dur:{}".format(bar, channel[bar][0], channel[bar][1]))
    print("----------------------")

w = 0.5

denom_pitch = {}
denom_dur = {}
melody_route = {}

for index, channel in enumerate(avg_data):
    for bar in channel:
        if bar not in denom_pitch.keys():
            current_pitch = current_dur = 0

            for c in avg_data:
                if bar in c.keys():
                    current_pitch += c[bar][0]
                    current_dur += c[bar][1]

            denom_pitch[bar] = current_pitch
            denom_dur[bar] = current_dur

        mms = (1 / len(avg_data)) * ((channel[bar][0] / denom_pitch[bar]) + (w * (channel[bar][1] / denom_dur[bar])))

        if bar not in melody_route.keys() or mms > melody_route[bar][1]:
            melody_route[bar] = (index, mms)
    print("----------------------")

print(melody_route)
