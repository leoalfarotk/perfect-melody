{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import essentia.standard\n",
    "from dtw import *\n",
    "import os\n",
    "import pretty_midi\n",
    "from time import time\n",
    "import tslearn.metrics\n",
    "import matplotlib.pyplot as plt\n",
    "from collections import OrderedDict\n",
    "import librosa.feature\n",
    "import numpy as np"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def calculate_gradient_vector(melody):\n",
    "    _gradients = []\n",
    "\n",
    "    for index, note in enumerate(melody):\n",
    "        if index == 0:\n",
    "            continue\n",
    "\n",
    "        _gradients.append(note - melody[index - 1])\n",
    "\n",
    "    return _gradients"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def read_melody_files(filename):\n",
    "    with open(filename) as f:\n",
    "        _notes = f.read()\n",
    "\n",
    "    _notes = _notes.split(',')\n",
    "    return [float(i) for i in _notes]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "def normalize(series, mmin, mmax):\n",
    "    return [((i-mmin)/(mmax-mmin)) for i in series]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h1>Experimento 1 (solo vocal, sin ceros, chromas) - MRR: 0.23 - Top10: 60%</h1>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "melodies_path = 'dataset/chromas/vocals/'\n",
    "hummings_path = 'dataset/hummings/'\n",
    "melodies = os.listdir(melodies_path)\n",
    "hummings = os.listdir(hummings_path)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "numerador_MRR = 0\n",
    "numerador_TOP = 0\n",
    "denominador = 0\n",
    "for hum in hummings:\n",
    "    denominador += 1\n",
    "    results = {}\n",
    "    print(\"........\" + hum + \"........\")\n",
    "    print(\"----------\")\n",
    "    loader = essentia.standard.EqloudLoader(filename=hummings_path + hum, sampleRate=44100)\n",
    "    audio = loader()\n",
    "    pitch_extractor = essentia.standard.PredominantPitchMelodia(frameSize=2048, hopSize=50)\n",
    "    pitch_values, pitch_confidence = pitch_extractor(audio)\n",
    "    pitch_values = pitch_values[pitch_values != 0]\n",
    "    chroma = librosa.feature.chroma_stft(y=np.asarray(pitch_values), sr=44100, hop_length=50)\n",
    "    for melodie in melodies:\n",
    "        chroma_db = np.loadtxt(melodies_path + melodie)\n",
    "        alignment = dtw(chroma.transpose(), chroma_db, step_pattern=rabinerJuangStepPattern(6, \"c\"), keep_internals=False, open_begin=True, open_end=True)\n",
    "        results[melodie] = alignment.distance\n",
    "    ordered_results = OrderedDict({k: v for k, v in sorted(results.items(), key=lambda item: item[1])})\n",
    "    for i, rank in enumerate(ordered_results.items()):\n",
    "        if hum.split('.')[0].split('+')[0] == rank[0].split('.')[0]:\n",
    "            numerador_MRR += (1/(i+1))\n",
    "            if i <= 10:\n",
    "                numerador_TOP += 1\n",
    "        print(i+1, rank[0], rank[1])\n",
    "        print(\"----------\")\n",
    "    print(\"================================\")\n",
    "mrr = numerador_MRR / denominador\n",
    "top10 = numerador_TOP / denominador * 100\n",
    "print('MRR: ', mrr)\n",
    "print('Top-10: ', top10)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h1>Experimento 2 (solo vocal, secuencia completa, con ceros, normalizando y gradientes) - MRR: 0.26 - Top10: 72%</h1>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "melodies_path = 'dataset/melodies/strings/vocals/'\n",
    "hummings_path = 'dataset/hummings/'\n",
    "melodies = os.listdir(melodies_path)\n",
    "hummings = os.listdir(hummings_path)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": false
   },
   "outputs": [],
   "source": [
    "numerador_MRR = 0\n",
    "numerador_TOP = 0\n",
    "denominador = 0\n",
    "for hum in hummings:\n",
    "    denominador += 1\n",
    "    results = {}\n",
    "    print(\"........\" + hum + \"........\")\n",
    "    print(\"----------\")\n",
    "    loader = essentia.standard.EqloudLoader(filename=hummings_path + hum, sampleRate=44100)\n",
    "    audio = loader()\n",
    "    pitch_extractor = essentia.standard.PredominantPitchMelodia(frameSize=2048, hopSize=180)\n",
    "    pitch_values, pitch_confidence = pitch_extractor(audio)\n",
    "    pitch_values = normalize(pitch_values, min(pitch_values), max(pitch_values))\n",
    "    pitch_values = calculate_gradient_vector(pitch_values)\n",
    "    for melodie in melodies:\n",
    "        pitch_values_db = read_melody_files(melodies_path + melodie)\n",
    "        pitch_values_db = normalize(pitch_values_db, min(pitch_values_db), max(pitch_values_db))\n",
    "        pitch_values_db = calculate_gradient_vector(pitch_values_db)\n",
    "        alignment = dtw(pitch_values, pitch_values_db, step_pattern=rabinerJuangStepPattern(6, \"c\"), keep_internals=False, open_begin=True, open_end=True)\n",
    "        results[melodie] = alignment.distance\n",
    "    ordered_results = OrderedDict({k: v for k, v in sorted(results.items(), key=lambda item: item[1])})\n",
    "    for i, rank in enumerate(ordered_results.items()):\n",
    "        if hum.split('.')[0].split('+')[0] == rank[0].split('.')[0]:\n",
    "            numerador_MRR += (1/(i+1))\n",
    "            if i <= 10:\n",
    "                numerador_TOP += 1\n",
    "        print(i+1, rank[0], rank[1])\n",
    "        print(\"----------\")\n",
    "    print(\"================================\")\n",
    "mrr = numerador_MRR / denominador\n",
    "top10 = numerador_TOP / denominador * 100\n",
    "print('MRR: ', mrr)\n",
    "print('Top-10: ', top10)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h1>Experimento 3 (solo vocal, secuencia completa, sin ceros, normalizando y gradientes) - MRR: 0.28 - Top10: 56%</h1>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "melodies_path = 'dataset/melodies/strings/vocals/'\n",
    "hummings_path = 'dataset/hummings/'\n",
    "melodies = os.listdir(melodies_path)\n",
    "hummings = os.listdir(hummings_path)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "numerador_MRR = 0\n",
    "numerador_TOP = 0\n",
    "denominador = 0\n",
    "for hum in hummings:\n",
    "    denominador += 1\n",
    "    results = {}\n",
    "    print(\"........\" + hum + \"........\")\n",
    "    print(\"----------\")\n",
    "    loader = essentia.standard.EqloudLoader(filename=hummings_path + hum, sampleRate=44100)\n",
    "    audio = loader()\n",
    "    pitch_extractor = essentia.standard.PredominantPitchMelodia(frameSize=2048, hopSize=180)\n",
    "    pitch_values, pitch_confidence = pitch_extractor(audio)\n",
    "    pitch_values = pitch_values[pitch_values != 0]\n",
    "    pitch_values = normalize(pitch_values, min(pitch_values), max(pitch_values))\n",
    "    pitch_values = calculate_gradient_vector(pitch_values)\n",
    "    for melodie in melodies:\n",
    "        pitch_values_db = read_melody_files(melodies_path + melodie)\n",
    "        pitch_values_db = [i for i in pitch_values_db if i != 0]\n",
    "        pitch_values_db = normalize(pitch_values_db, min(pitch_values_db), max(pitch_values_db))\n",
    "        pitch_values_db = calculate_gradient_vector(pitch_values_db)\n",
    "        alignment = dtw(pitch_values, pitch_values_db, step_pattern=rabinerJuangStepPattern(6, \"c\"), keep_internals=False, open_begin=True, open_end=True)\n",
    "        results[melodie] = alignment.distance\n",
    "    ordered_results = OrderedDict({k: v for k, v in sorted(results.items(), key=lambda item: item[1])})\n",
    "    for i, rank in enumerate(ordered_results.items()):\n",
    "        if hum.split('.')[0].split('+')[0] == rank[0].split('.')[0]:\n",
    "            numerador_MRR += (1/(i+1))\n",
    "            if i <= 10:\n",
    "                numerador_TOP += 1\n",
    "        print(i+1, rank[0], rank[1])\n",
    "        print(\"----------\")\n",
    "    print(\"================================\")\n",
    "mrr = numerador_MRR / denominador\n",
    "top10 = numerador_TOP / denominador * 100\n",
    "print('MRR: ', mrr)\n",
    "print('Top-10: ', top10)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h1>Experimento 4 (concatenaciones, secuencia completa, sin ceros, normalizando y gradientes) - MRR: 0.22 - Top10: 64%</h1>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "melodies_path = 'dataset/melodies/strings/concatenations/'\n",
    "hummings_path = 'dataset/hummings/'\n",
    "melodies = os.listdir(melodies_path)\n",
    "hummings = os.listdir(hummings_path)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "numerador_MRR = 0\n",
    "numerador_TOP = 0\n",
    "denominador = 0\n",
    "for hum in hummings:\n",
    "    denominador += 1\n",
    "    results = {}\n",
    "    print(\"........\" + hum + \"........\")\n",
    "    print(\"----------\")\n",
    "    loader = essentia.standard.EqloudLoader(filename=hummings_path + hum, sampleRate=44100)\n",
    "    audio = loader()\n",
    "    pitch_extractor = essentia.standard.PredominantPitchMelodia(frameSize=2048, hopSize=180)\n",
    "    pitch_values, pitch_confidence = pitch_extractor(audio)\n",
    "    pitch_values = pitch_values[pitch_values != 0]\n",
    "    pitch_values = normalize(pitch_values, min(pitch_values), max(pitch_values))\n",
    "    pitch_values = calculate_gradient_vector(pitch_values)\n",
    "    for melodie in melodies:\n",
    "        pitch_values_db = read_melody_files(melodies_path + melodie)\n",
    "        pitch_values_db = [i for i in pitch_values_db if i != 0]\n",
    "        pitch_values_db = normalize(pitch_values_db, min(pitch_values_db), max(pitch_values_db))\n",
    "        pitch_values_db = calculate_gradient_vector(pitch_values_db)\n",
    "        alignment = dtw(pitch_values, pitch_values_db, step_pattern=rabinerJuangStepPattern(6, \"c\"), keep_internals=False, open_begin=True, open_end=True)\n",
    "        results[melodie] = alignment.distance\n",
    "    ordered_results = OrderedDict({k: v for k, v in sorted(results.items(), key=lambda item: item[1])})\n",
    "    for i, rank in enumerate(ordered_results.items()):\n",
    "        if hum.split('.')[0].split('+')[0] == rank[0].split('.')[0]:\n",
    "            numerador_MRR += (1/(i+1))\n",
    "            if i <= 10:\n",
    "                numerador_TOP += 1\n",
    "        print(i+1, rank[0], rank[1])\n",
    "        print(\"----------\")\n",
    "    print(\"================================\")\n",
    "mrr = numerador_MRR / denominador\n",
    "top10 = numerador_TOP / denominador * 100\n",
    "print('MRR: ', mrr)\n",
    "print('Top-10: ', top10)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "<h1>Experimento 5 (concatenaciones, secuencia completa, con ceros, normalizando y gradientes) - MRR: 0.24 - Top10: 76%</h1>"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "melodies_path = 'dataset/melodies/strings/concatenations/'\n",
    "hummings_path = 'dataset/hummings/'\n",
    "melodies = os.listdir(melodies_path)\n",
    "hummings = os.listdir(hummings_path)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "numerador_MRR = 0\n",
    "numerador_TOP = 0\n",
    "denominador = 0\n",
    "for hum in hummings:\n",
    "    denominador += 1\n",
    "    results = {}\n",
    "    print(\"........\" + hum + \"........\")\n",
    "    print(\"----------\")\n",
    "    loader = essentia.standard.EqloudLoader(filename=hummings_path + hum, sampleRate=44100)\n",
    "    audio = loader()\n",
    "    pitch_extractor = essentia.standard.PredominantPitchMelodia(frameSize=2048, hopSize=180)\n",
    "    pitch_values, pitch_confidence = pitch_extractor(audio)\n",
    "    pitch_values = normalize(pitch_values, min(pitch_values), max(pitch_values))\n",
    "    pitch_values = calculate_gradient_vector(pitch_values)\n",
    "    for melodie in melodies:\n",
    "        pitch_values_db = read_melody_files(melodies_path + melodie)\n",
    "        pitch_values_db = normalize(pitch_values_db, min(pitch_values_db), max(pitch_values_db))\n",
    "        pitch_values_db = calculate_gradient_vector(pitch_values_db)\n",
    "        alignment = dtw(pitch_values, pitch_values_db, step_pattern=rabinerJuangStepPattern(6, \"c\"), keep_internals=False, open_begin=True, open_end=True)\n",
    "        results[melodie] = alignment.distance\n",
    "    ordered_results = OrderedDict({k: v for k, v in sorted(results.items(), key=lambda item: item[1])})\n",
    "    for i, rank in enumerate(ordered_results.items()):\n",
    "        if hum.split('.')[0].split('+')[0] == rank[0].split('.')[0]:\n",
    "            numerador_MRR += (1/(i+1))\n",
    "            if i <= 10:\n",
    "                numerador_TOP += 1\n",
    "        print(i+1, rank[0], rank[1])\n",
    "        print(\"----------\")\n",
    "    print(\"================================\")\n",
    "mrr = numerador_MRR / denominador\n",
    "top10 = numerador_TOP / denominador * 100\n",
    "print('MRR: ', mrr)\n",
    "print('Top-10: ', top10)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
