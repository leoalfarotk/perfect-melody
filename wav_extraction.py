import essentia.standard
import essentia.streaming


def extract_melody_from_wav(file_name):
    loader_db = essentia.standard.EqloudLoader(filename=file_name, sampleRate=44100)
    audio_db = loader_db()
    pitch_extractor_db = essentia.standard.PredominantPitchMelodia()
    pitch_values_db, pitch_confidence_db = pitch_extractor_db(audio_db)
    contour_extractor_db = essentia.standard.PitchContourSegmentation()
    _onset_db, _duration_db, _MIDI_pitch_db = contour_extractor_db(pitch_values_db, audio_db)

    return _onset_db, _duration_db, _MIDI_pitch_db
