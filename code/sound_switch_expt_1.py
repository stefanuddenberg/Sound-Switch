# Presents randomly generated auditory stimuli according to a
# simple switch rule, and asks participants to judge the
# aesthetic quality of those stimuli using a slider.
# Author: Stefan Uddenberg
# TODO: EVERYTHING
# TODO: GUI
# TODO: Instructions
# TODO: Condition randomization
# TODO: Trial generation
# TODO: Experiment design
# TODO: Data saving

checked = False

from psychopy import visual, monitors, core, event, os, data, gui, misc, logging
from pydub import AudioSegment
from pydub.generators import Sine # XXX Can learn to generate the sine wave natively
from pydub.playback import play
import logging
import numpy as np
import os
import random
import socket
from stefan_utils import tabify, rgb2psychorgb

logging.basicConfig(level=logging.DEBUG)

# Set up window
win = visual.Window(
    fullscr=False,
    size=[1280, 720],
    colorSpace='rgb',
    color='white',
    units='pix',
    monitor='testMonitor'
)

# Set up tones
# Create sine waves of given freqs
frequencies = [440, 659.225] # A4, E5
sample_rate = 44100  # sample rate
bit_depth = 16     # bit depth
chunk_size  = 500  # duration in millisec
crossfade_duration = 150
duration = 2_000 # duration of final song in ms
num_chunks = int(duration / chunk_size)

sine_waves = []
sine_segments = []
for i, frequency in enumerate(frequencies):
    sine_waves.append(Sine(frequency, sample_rate=sample_rate, bit_depth=bit_depth))
    #Convert waveform to audio_segment for playback and export
    sine_segments.append(sine_waves[i].to_audio_segment(duration=chunk_size+crossfade_duration))

# Create audio stream of alternating sine waves
switch_probability = 0.5
this_song = AudioSegment.empty()
which_tone = round(random.random())
for chunks in range(num_chunks):
    this_probability = random.random()

    if this_probability < switch_probability:
        which_tone = 1 - which_tone

    this_segment = sine_segments[which_tone]
    if len(this_song) == 0:
        this_song += this_segment
    else:
        this_song = this_song.append(this_segment, crossfade=crossfade_duration)


# Set up rating scale
rating_scale = visual.RatingScale(
    win,
    low=0,
    high=100,
    marker="triangle", # slider, circle
    lineColor="black",
    markerColor="black",
    textColor="black",
    tickMarks=[0, 100],
    stretch=2.25,
    tickHeight=1.5,
    showValue=False,
    acceptPreText="Click line",
    acceptText="Submit",
    labels=["Not at all beautiful", "Very beautiful"]
)

# Change styling of submit button
rating_scale.accept.italic = False

# Change the color of the submit button before marker placement
# rating_scale.acceptBox.fillColor = rgb2psychorgb([52, 152, 219])
# Change the color of the submit button after marker placement
# (Basically overwriting the implementation in ratingscale.py)
frames_per_cycle = 100
rating_scale.pulseColor = [
    rgb2psychorgb([91, 189, 255])
    for i in range(frames_per_cycle)
]

question = visual.TextStim(
    win,
    text="How beautiful is this sequence?",
    color="black",
    height=25,
    units='pix'
)

# show instructions
instructions = visual.TextStim(
    win,
    text="Press any key to begin.",
    color="black",
    height=25,
    units='pix'
)

event.clearEvents()
instructions.draw()
win.flip()
if 'escape' in event.waitKeys():
    core.quit()

instructions.text = "Playing song..."
instructions.draw()
win.flip()
play(this_song)

# show & update until a response has been made
while rating_scale.noResponse:
    question.draw()
    rating_scale.draw()
    win.flip()
    if event.getKeys(['escape']):
        core.quit()

# Show response
logging.debug(f"Example trial: rating = {rating_scale.getRating()}")

# End experiment
win.close()
core.quit()
