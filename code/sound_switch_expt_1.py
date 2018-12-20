# Presents randomly generated auditory stimuli according to a
# simple switch rule, and asks participants to judge the
# aesthetic quality of those stimuli using a slider.
# Author: Stefan Uddenberg
# TODO: EVERYTHING
# TODO: GUI
# TODO: Instructions
# TODO: Trial generation
# TODO: Experiment design
# TODO: Data saving

################################
# * IMPORTS/SETUP
################################
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

################################
# * FUNCTIONS
################################

def show_instructions(instructions_list):
    for instr in instructions_list:
        instructions.setText(instr)
        instructions.draw()
        win.flip()
        keys = event.waitKeys(keyList=[v for k, v in key_dict.items()])
        if key_dict["quit"] in keys:
            win.close()
            core.quit()

def do_trial(practiceOn):
    # global instructions
    # global question
    # global win
    # global this_song
    # global stimuli
    # global trial_data
    # global rating_scale

    trial_data = {}
    this_song = this_song_info["file"]
    instructions.text = "Playing sequence..."
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

    # Record response
    trial_data.update(this_song_info)
    trial_data["RT"] = rating_scale.getRT()
    trial_data["response"] = rating_scale.getRating()
    trial_data["choice_history"] = rating_scale.getHistory()
    logging.debug(f"Example trial: rating = {trial_data['response']}")

    # Save data



################################
# * CONSTANTS
################################
stimulus_dir = "../stimuli/guitar_chords/"
switch_probabilities = np.linspace(0.1, 0.9, num=9)
num_exemplars = 10
chunk_size = 500
# 20 stimuli chosen via a random choice without replacement for each switch chunk
# Extra two chosen for 0.4 and 0.6, as they are on either side of 0.5
repeated_stimuli = [
    f"{stimulus_dir}switch-0.1_chunk-{str(chunk_size)}_C_G_alternating_04.mp3",
    f"{stimulus_dir}switch-0.1_chunk-{str(chunk_size)}_C_G_alternating_05.mp3",
    f"{stimulus_dir}switch-0.2_chunk-{str(chunk_size)}_C_G_alternating_09.mp3",
    f"{stimulus_dir}switch-0.2_chunk-{str(chunk_size)}_C_G_alternating_01.mp3",
    f"{stimulus_dir}switch-0.3_chunk-{str(chunk_size)}_C_G_alternating_08.mp3",
    f"{stimulus_dir}switch-0.3_chunk-{str(chunk_size)}_C_G_alternating_04.mp3",
    f"{stimulus_dir}switch-0.4_chunk-{str(chunk_size)}_C_G_alternating_01.mp3",
    f"{stimulus_dir}switch-0.4_chunk-{str(chunk_size)}_C_G_alternating_08.mp3",
    f"{stimulus_dir}switch-0.4_chunk-{str(chunk_size)}_C_G_alternating_02.mp3",
    f"{stimulus_dir}switch-0.5_chunk-{str(chunk_size)}_C_G_alternating_06.mp3",
    f"{stimulus_dir}switch-0.5_chunk-{str(chunk_size)}_C_G_alternating_09.mp3",
    f"{stimulus_dir}switch-0.6_chunk-{str(chunk_size)}_C_G_alternating_07.mp3",
    f"{stimulus_dir}switch-0.6_chunk-{str(chunk_size)}_C_G_alternating_02.mp3",
    f"{stimulus_dir}switch-0.6_chunk-{str(chunk_size)}_C_G_alternating_04.mp3",
    f"{stimulus_dir}switch-0.7_chunk-{str(chunk_size)}_C_G_alternating_07.mp3",
    f"{stimulus_dir}switch-0.7_chunk-{str(chunk_size)}_C_G_alternating_04.mp3",
    f"{stimulus_dir}switch-0.8_chunk-{str(chunk_size)}_C_G_alternating_03.mp3",
    f"{stimulus_dir}switch-0.8_chunk-{str(chunk_size)}_C_G_alternating_09.mp3",
    f"{stimulus_dir}switch-0.9_chunk-{str(chunk_size)}_C_G_alternating_02.mp3",
    f"{stimulus_dir}switch-0.9_chunk-{str(chunk_size)}_C_G_alternating_01.mp3",
]
conditions = [
    "beautiful",
    "patterned",
]
question_labels = {
    "beautiful": ["Not at all beautiful", "Extremely beautiful"],
    "patterned": ["Extremely random", "Extremely patterned"],
}

key_dict = {
    "quit": "escape",
    "continue": "backslash",
}
################################
# * SUBJECT INFORMATION
################################
# ! XXX Get subject info
subject_number = 1

################################
# * CONDITIONS
################################
# Choose condition and question/instruction text
condition = conditions[subject_number % len(conditions)]
question_label = question_labels[condition]

################################
# * DISPLAY ITEMS
################################
screen_width = 1280
screen_height = 720
units = 'pix'
resolution = [screen_width, screen_height]  # XXX: change for final computer

win = visual.Window(
    fullscr=False,
    size=resolution,
    colorSpace="rgb",
    color="white",
    units=units,
    monitor="testMonitor",
    winType="pyglet"
)

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
    labels=question_label
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

# Set up question text
question = visual.TextStim(
    win,
    text=f"How {condition} is this sequence?",
    color="black",
    height=25,
    units=units
)

################################
# * STIMULI
################################
# Get sound stimuli
stimuli = {}
for switch_probability in switch_probabilities:
    sp = str(round(switch_probability, 2))
    stimuli[sp] = []
    for exemplar in range(num_exemplars):
        song_name = f"{stimulus_dir}switch-{sp}_chunk-{str(chunk_size)}_C_G_alternating_{str(exemplar).zfill(2)}.mp3"
        this_song = AudioSegment.from_mp3(song_name)
        stimuli[sp].append(this_song)

    # Make sure to randomize the order of the stimuli
    random.shuffle(stimuli[sp])

# Get repeated stimuli for test-retest reliability
stimuli["repeat"] = []
for repeated_stimulus in repeated_stimuli:
    this_song = AudioSegment.from_mp3(repeated_stimulus)
    stimuli["repeat"].append(this_song)

# Make sure to randomize the order of the stimuli
random.shuffle(stimuli["repeat"])


################################
# * INSTRUCTIONS
################################
# Set up instructions
# Use the first font found in the list below
font_list = ['Helvetica', 'Arial', 'Verdana']
instructions = visual.TextStim(
    win,
    font=font_list,
    text="Press any key to begin.",
    alignHoriz='center',
    alignVert='center',
    pos=(0,0),
    color="black",
    height=25,
    units=units,
    wrapWidth=screen_width-200
)

# Show instructions
instructions_list = []
instructions_list.append(
    "Hello! Thank you for participating in our study. "
    "Have a seat in front of the computer, and take "
    "a moment to adjust your chair so that "
    "you can comfortably watch the monitor and "
    "use the mouse and keyboard. The lights will be dimmed "
    "during the experiment to minimize outside "
    "interference. Please also take a moment to "
    "silence your phone, etc., so that you're not "
    "interrupted by any messages."
)

instructions_list.append(
    "Before we begin, this study requires that "
    "you have normal visual acuity; "
    "glasses or contacts are fine. In addition, "
    "it is important that you have normal hearing. "
    "Please let me know right away if you expect to "
    "have any difficulties with seeing what is on the "
    "screen, or hearing what is playing."
)

instructions_list.append(
    "In this experiment, you will hear a sequence of "
    "two different different sounds that will be played "
    "one at a time in some order. "
    "For example, you might hear a guitar strum one note, "
    "and then strum a different note. \n\n"
    "Your job is to listen to the sequence, and then "
    f"tell us how {condition} you think it sounded "
    "by clicking on the rating scale."
)

instructions_list.append(
    "There are no right or wrong answers, and we are interested "
    "in your gut feeling about the sequences of sounds. "
    "\n\n"
    "The experiment as a whole should last roughly 30 minutes in total. "
    "I know that it is difficult to stay focused "
    "for this long, but I ask you to please do your very best to "
    "remain as focused and attentive as "
    "possible, even toward the end of the experiment. "
    "Since I am investigating the limits of attention in "
    "this experiment, your results are only useful to science "
    "if you really do your best to stay engaged "
    "throughout the experiment."
)
instructions_list.append("Let's give that a try! Press backslash (\\) to do a practice trial.")

show_instructions(instructions_list)

################################
# * PRACTICE
################################
this_song_info = {
    "switch_rate": "0.9",
    "exemplar": np.random.randint(0, 10),
}
this_song_info["file"] = stimuli[this_song_info["switch_rate"]][this_song_info["exemplar"]]
do_trial(practiceOn=True)

################################
# * MAIN EXPERIMENT
################################
# Show final instructions before moving on
instructions_list = [
    "Any questions? If not, please press backslash (\\) to start the experiment for real."
]

show_instructions(instructions_list)


# End experiment
win.close()
core.quit()
