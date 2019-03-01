---
jupyter:
  jupytext:
    metadata_filter:
      cells:
        additional: all
      notebook:
        additional: all
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.0'
      jupytext_version: 0.8.6
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
  language_info:
    codemirror_mode:
      name: ipython
      version: 3
    file_extension: .py
    mimetype: text/x-python
    name: python
    nbconvert_exporter: python
    pygments_lexer: ipython3
    version: 3.6.7
---

# Generate stimuli for Sound-Switch Experiment 1 <a class="tocSkip">
C and G guitar chords generated [here](https://www.apronus.com/music/onlineguitar.htm) and subsequently recorded and amplified (25.98 db and 25.065 db respectively) using Audacity version 2.3.0 (using Effect --> Amplify) via Windows 10's Stereo Mix drivers.


# Imports

```python
from pydub import AudioSegment
from pydub.generators import Sine
from pydub.playback import play
import random
import numpy as np
import os
```

# Functions

```python
def generate_songs(path_prefix):
    for switch_probability in switch_probabilities:
        for exemplar in range(num_exemplars):
            # Begin with silence
            this_song = silence
            # Choose random tone to start with
            which_tone = round(random.random())
            for chunk in range(num_chunks):
                this_probability = random.random()

                # Change tones if necessary
                if this_probability < switch_probability:
                    which_tone = 1 - which_tone

                this_segment = songs[which_tone][:chunk_size]

                # Add intervening silence
                this_song = this_song.append(silence, crossfade=crossfade_duration)
                # Add tone
                this_song = this_song.append(this_segment, crossfade=crossfade_duration)

            # Add final silence
            this_song.append(silence, crossfade=crossfade_duration)
            song_name = f"{path_prefix}switch-{str(round(switch_probability,2))}_chunk-{str(chunk_size)}_C_G_alternating_{str(exemplar).zfill(2)}.mp3"
            this_song.export(song_name, format="mp3", bitrate="192k")
```

# Stimulus Generation


## Guitar chords

```python
songs = [
    AudioSegment.from_mp3("guitar_chords/guitar_C.mp3"),
    AudioSegment.from_mp3("guitar_chords/guitar_G.mp3"),
]

chunk_size = 500 # in ms
num_chunks = 20
crossfade_duration = 50 # in ms
silence_duration = 100 # in ms
switch_probabilities = np.linspace(0.1, 0.9, num=9)
num_exemplars = 10
silence = AudioSegment.silent(duration=silence_duration)
# Generate the songs
generate_songs(path_prefix="guitar_chords/")
```

## Tones

```python
# Create sine waves of given freqs
frequencies = [261.626, 391.995] # C4, G4
sample_rate = 44100  # sample rate
bit_depth = 16     # bit depth

# Same params as above for guitar
chunk_size = 500 # in ms
num_chunks = 20
crossfade_duration = 50 # in ms
silence_duration = 100 # in ms
switch_probabilities = np.linspace(0.1, 0.9, num=9)
num_exemplars = 10
silence = AudioSegment.silent(duration=silence_duration)

sine_waves = []
songs = []
for i, frequency in enumerate(frequencies):
    sine_waves.append(Sine(frequency, sample_rate=sample_rate, bit_depth=bit_depth))
    #Convert waveform to audio_segment for playback and export
    songs.append(sine_waves[i].to_audio_segment(duration=chunk_size*2)) # just to make sure it's long enough

generate_songs(path_prefix="pure_tones/")
```

# Practice Stimulus
Just choose one of the above stimuli to be a practice stimulus, and remake the stimuli so that it doesn't get repeated.
