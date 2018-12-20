# Presents randomly generated auditory stimuli according to a
# simple switch rule, and asks participants to judge the
# beauty or patterned-ness of those stimuli using a slider.
# Author: Stefan Uddenberg

# TODO: Show Alex et al.
# TODO: Decide on final stimuli
# TODO: Update screen parameters

################################
# * IMPORTS/SETUP
################################
checked = False

from psychopy import visual, monitors, core, event, os, data, gui, misc, logging
from pydub import AudioSegment
from pydub.playback import play
import json
import logging
import numpy as np
import os
import random
import socket
from stefan_utils import tabify
from stefan_utils import rgb2psychorgb
from stefan_utils import quit_experiment
from stefan_utils import get_subject_info
from stefan_utils import make_data_file
from stefan_utils import make_subject_file
from stefan_utils import write_to_file
from stefan_utils import show_instructions

logging.basicConfig(level=logging.DEBUG)

################################
# * FUNCTIONS
################################

def create_rating_scale():
	""" Generates a new rating scale object
	from scratch. This is necessary because there
	isn't an elegant way to reuse a rating scale.

	:raises: N/A

	:rtype: psychopy.visual.RatingScale
	"""
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

	return rating_scale


def get_trial_data():
	global rating_scale

	trial_data = {}
	trial_data.update(exp_info)
	trial_data.update(this_song_info)
	trial_data["RT"] = rating_scale.getRT()
	trial_data["Rating"] = rating_scale.getRating()
	trial_data["Rating History"] = rating_scale.getHistory()
	trial_data["Trial #"] = trial_num
	trial_data["Block #"] = block_num
	trial_data["Switch Rate"] = this_song_info["switch_rate"]
	trial_data["Exemplar"] = this_song_info["exemplar"]
	trial_data["File Name"] = this_song_info["song_name"]
	trial_data["Trial Duration"] = trial_clock.getTime()
	trial_data["Block Duration"] = block_clock.getTime()
	trial_data["Session Duration"] = session_clock.getTime()
	trial_data["Experiment Duration"] = experiment_clock.getTime()
	return trial_data


def do_trial(this_song_info, practiceOn):
	""" Performs a trial. Plays the song passed in,
	collects responses using the rating scale, and
	saves the data.

	:type this_song_info:
	:param this_song_info:

	:type practiceOn:
	:param practiceOn:

	:raises:

	:rtype:
	"""
	global rating_scale

	trial_clock.reset()
	rating_scale = create_rating_scale()

	this_song = this_song_info["song"]
	instructions.text = "Playing sequence..."
	for frame in range(num_blank_frames):
		instructions.draw()
		win.flip()
	play(this_song)

	# show & update until a response has been made
	while rating_scale.noResponse:
		question.draw()
		rating_scale.draw()
		win.flip()
		if event.getKeys(key_dict["quit"]):
			quit_experiment(win, core)

	# Save data
	if not practiceOn:
		# Record response
		trial_data = get_trial_data()
		write_to_file(data_file, trial_data, info_order)
		logging.debug(trial_data)

		logging.debug(f"rating_scale.getRating() => {rating_scale.getRating()}")
		logging.debug(f"rating_scale.getRT() => {rating_scale.getRT()}")
		logging.debug(f"rating_scale.getHistory() => {rating_scale.getHistory()}")



def generate_trials():
	""" Generates a list of tuples for each trial,
	where the first element in the tuple is the
	switch rate and the second is the exemplar index.

	:raises: N/A

	:rtype: list
	"""

	trial_order = []
	for switch_probability in switch_probabilities:
		sp = str(round(switch_probability, 2))
		trial_order.extend([(sp, s) for s in range(num_exemplars)])

	random.shuffle(trial_order)
	logging.debug(trial_order)
	return trial_order


################################
# * CONSTANTS
################################
num_blank_frames = 30 # how many frames to wait before playing the sequence
data_dir = "../data/"
stimulus_dir = "../stimuli/guitar_chords/"
switch_probabilities = np.linspace(0.1, 0.9, num=9)
num_exemplars = 10
chunk_size = 500
# 20 stimuli chosen via a random choice without replacement for each switch chunk
# Extra two chosen for 0.4 and 0.6, as they are on either side of 0.5
repeated_trial_order = [
	('0.1', 4),
	('0.1', 5),
	('0.2', 9),
	('0.2', 1),
	('0.3', 8),
	('0.3', 4),
	('0.4', 1),
	('0.4', 8),
	('0.4', 2),
	('0.5', 6),
	('0.5', 9),
	('0.6', 7),
	('0.6', 2),
	('0.6', 4),
	('0.7', 7),
	('0.7', 4),
	('0.8', 3),
	('0.8', 9),
	('0.9', 2),
	('0.9', 1),
]
random.shuffle(repeated_trial_order)

conditions = [
	"beautiful",
	"patterned",
]
question_labels = {
	"beautiful": ["Not at all beautiful", "Extremely beautiful"],
	"patterned": ["Extremely random", "Extremely patterned"],
}

# Valid response keys
key_dict = {
	"quit": "escape",
	"continue": "backslash",
}

################################
# * CLOCKS
################################
session_clock = core.Clock() #roughly, the time since pressing 'run'
experiment_clock = core.Clock() #time since the start of the first trial of the experiment
block_clock = core.Clock() #time since the start of the first trial of the block
trial_clock = core.Clock() #time since the start of the trial

################################
# * SUBJECT INFORMATION
################################
# Get subject info
experiment_name = 'Sound Switch 12-20-2018'
info_order =  [
	'Subject ID',
	'Condition',
	'Block #',
	'Trial #',
	'Switch Rate',
	'Exemplar',
	'File Name',
	'Rating',
	'RT',
	'Rating History',
	'Trial Duration',
	'Block Duration',
	'Session Duration',
	'Experiment Duration',
	'Start Date',
	'Experiment',
	'Testing Location',
	'Experimenter Initials',
	'Subject Initials',
]

sub_info_order = [
	'Subject ID',
	'Condition',
	'Start Date',
	'Experiment',
	'Testing Location',
	'Experimenter Initials',
	'Subject Initials',
]
exp_info = get_subject_info(data_dir, experiment_name)

logging.debug(exp_info["Subject ID"])
logging.debug(type(exp_info["Subject ID"]))

################################
# * CONDITIONS
################################
# Choose condition and question/instruction text
condition = conditions[int(exp_info["Subject ID"]) % len(conditions)]
exp_info["Condition"] = condition # save to exp_info
question_label = question_labels[condition]

# Make data files
data_file = make_data_file(data_dir, exp_info, info_order)
subject_file = make_subject_file(data_dir, exp_info, sub_info_order)

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
	stimuli[sp] = {
		"song_names": [],
		"songs": [],
	}
	for exemplar in range(num_exemplars):
		song_name = f"{stimulus_dir}switch-{sp}_chunk-{str(chunk_size)}_C_G_alternating_{str(exemplar).zfill(2)}.mp3"
		stimuli[sp]["song_names"].append(song_name)
		this_song = AudioSegment.from_mp3(song_name)
		stimuli[sp]["songs"].append(this_song)

# Generate trial order
trial_order = generate_trials()

# Get practice stimulus
this_song_info = {
	"switch_rate": "0.5",
	"exemplar": 0,
}
this_song_info["song_name"] = f"{stimulus_dir}practice_switch-0.5_chunk-{str(chunk_size)}_C_G_alternating_00.mp3"
this_song_info["song"] = AudioSegment.from_mp3(this_song_info["song_name"])

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

show_instructions(instructions, instructions_list, key_dict, win)

################################
# * PRACTICE
################################
do_trial(this_song_info, practiceOn=True)

################################
# * MAIN EXPERIMENT
################################
experiment_clock.reset()
# Show final instructions before moving on
instructions_list = [
	"Any questions? If not, please press backslash (\\) to start the experiment for real."
]

show_instructions(instructions, instructions_list, key_dict, win)

# Main loop
trial_num = 0
block_num = 1
block_clock.reset()
for (switch_rate, exemplar) in trial_order:
	trial_num += 1
	this_song_info = {
		"switch_rate": switch_rate,
		"exemplar": exemplar,
		"song": stimuli[switch_rate]["songs"][exemplar],
		"song_name": stimuli[switch_rate]["song_names"][exemplar],
	}
	do_trial(this_song_info, practiceOn=False)

################################
# * TEST-RETEST SECTION
################################
# Show final instructions before moving on
instructions_list = [
	"You're almost done! Just a few more trials to go. "
	"Press backslash (\\) whenever you're ready to continue."
]

show_instructions(instructions, instructions_list, key_dict, win)

# Test-retest loop
block_num = 2
block_clock.reset()
for (switch_rate, exemplar) in repeated_trial_order:
	trial_num += 1
	this_song_info = {
		"switch_rate": switch_rate,
		"exemplar": exemplar,
		"song": stimuli[switch_rate]["songs"][exemplar],
		"song_name": stimuli[switch_rate]["song_names"][exemplar],
	}
	do_trial(this_song_info, practiceOn=False)


################################
# * END EXPERIMENT
################################
# Show final instructions before moving on
instructions_list = [
	"You're done! Please go to your experimenter."
]

show_instructions(instructions, instructions_list, key_dict, win)

quit_experiment(win, core)

