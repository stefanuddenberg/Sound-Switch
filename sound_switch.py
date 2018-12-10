
# coding: utf-8

# ## Imports

# In[7]:


from pydub import AudioSegment
from pydub.generators import Sine # XXX Can learn to generate the sine wave natively
from pydub.playback import play
import copy
import random
import numpy as np
import os


# ## Cutting out sound

# In[45]:


switch_probabilities = np.linspace(0, 1, num=11)
chunk_size = 100 # in ms

song = AudioSegment.from_wav("./stimuli/test.wav")

for switch_probability in switch_probabilities:
    this_song = AudioSegment.empty()
    sound_on = bool(round(random.random()))
    for chunk_start in range(0, len(song)-1, chunk_size):
        this_probability = random.random()

        if this_probability < switch_probability:
            sound_on = not sound_on

        this_segment = song[chunk_start:chunk_start + chunk_size]
        if not sound_on: this_segment = AudioSegment.silent(duration=chunk_size)

        this_song += this_segment
    
    this_song.export(f"./stimuli/{str(switch_probability)}_chunk-{str(chunk_size)}.mp3", format="mp3", bitrate="192k")


# ## Adding delays XXX

# In[2]:


switch_probabilities = np.linspace(0, 1, num=11)
chunk_size = 100 # in ms

song = AudioSegment.from_wav("./stimuli/test.wav")

for switch_probability in switch_probabilities:
    this_song = AudioSegment.empty()
    sound_on = bool(round(random.random()))
    for chunk_start in range(0, len(song)-1, chunk_size):
        this_probability = random.random()

        if this_probability < switch_probability:
            sound_on = not sound_on

        this_segment = song[chunk_start:chunk_start + chunk_size]
        if not sound_on: this_segment = AudioSegment.silent(duration=chunk_size*2)

        this_song += this_segment
    
    this_song.export(f"./stimuli/{str(switch_probability)}_chunk-{str(chunk_size)}_delay.mp3", format="mp3", bitrate="192k")


# # Alternating between pure tones and silence

# In[11]:


song = AudioSegment.from_wav("./stimuli/audiocheck.net_sin_195.998Hz_-3dBFS_0.5s.wav")
duration = 10_000 # in ms
chunk_size = 500 # in ms
num_chunks = int(duration / chunk_size)
switch_probabilities = np.linspace(0, 1, num=11)

for switch_probability in switch_probabilities:
    this_song = AudioSegment.empty()
    sound_on = bool(round(random.random()))
    for chunks in range(num_chunks):
        this_probability = random.random()

        if this_probability < switch_probability:
            sound_on = not sound_on

        this_segment = song[:]
        if not sound_on: this_segment = AudioSegment.silent(duration=chunk_size)

        if len(this_song) == 0:
            this_song += this_segment
        else:
            this_song = this_song.append(this_segment, crossfade=50)

    this_song.export(f"./stimuli/crossfade_switch-{str(switch_probability)}_chunk-{str(chunk_size)}_G3_tone.mp3", format="mp3", bitrate="192k")


# # Alternating between two different pure tones

# In[10]:


songs = [
    AudioSegment.from_wav("./stimuli/audiocheck.net_sin_195.998Hz_-3dBFS_0.5s.wav"),
    AudioSegment.from_wav("./stimuli/audiocheck.net_sin_261.626Hz_-3dBFS_0.5s.wav")
]
duration = 10_000 # in ms
chunk_size = 500 # in ms
num_chunks = int(duration / chunk_size)

switch_probabilities = np.linspace(0, 1, num=11)
for switch_probability in switch_probabilities:
    this_song = AudioSegment.empty()
    which_tone = round(random.random())
    for chunks in range(num_chunks):
        this_probability = random.random()

        if this_probability < switch_probability:
            which_tone = 1 - which_tone

        this_segment = songs[which_tone]
        if len(this_song) == 0:
            this_song += this_segment
        else:
            this_song = this_song.append(this_segment, crossfade=50)



    this_song.export(f"./stimuli/crossfade_switch-{str(switch_probability)}_chunk-{str(chunk_size)}_G3_C4_alternating.mp3", format="mp3", bitrate="192k")    


# # Generate sine waves with Pydub

# In[15]:


#create sine wave of given freq
frequency = 440
sample_rate = 44100  # sample rate
bit_depth = 16     # bit depth
duration  = 5000     # duration in millisec
sine_wave = Sine(frequency, sample_rate=sample_rate, bit_depth=bit_depth)

#Convert waveform to audio_segment for playback and export
sine_segment = sine_wave.to_audio_segment(duration=duration)
sine_segment

