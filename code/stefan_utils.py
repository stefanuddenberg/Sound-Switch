# Utility functions for Psychopy Experiments
# Author: Stefan Uddenberg

from psychopy import core, data, event, gui
import json
import os

def tabify(s):
	""" Takes an array of strings and
	outputs a single string separated
	by tab characters
	:type s: list
	:param s: list of strings

	:raises: N/A

	:rtype: string
	"""

	s = '\t'.join(s)
	return s


def rgb2psychorgb(rgbVal):
	""" Takes a tuple rgbVal on scale
	from 0 to 255 and returns a tuple
	along the scale of -1 to 1
	(with 0 being gray)
	:type rgbVal: tuple
	:param rgbVal: tuple of r,g,b values

	:raises: N/A

	:rtype: tuple
	"""

	return tuple((x - 127.5) / 127.5 for index, x in enumerate(rgbVal))


def show_instructions(instructions, instructions_list, key_dict, win):

	""" Shows each instruction string in the list
	one at a time.
	:type instructions: psychopy.visual.TextStim
	:param instructions: The instructions TextStim object

	:type instructions_list: list
	:param instructions_list: list of instruction strings

	:type key_dict: dict
	:param key_dict: Dictionary of usable key presses

	:raises: N/A

	:rtype: void
	"""


	for instr in instructions_list:
		instructions.setText(instr)
		instructions.draw()
		win.flip()
		keys = event.waitKeys(keyList=[v for k, v in key_dict.items()])
		if key_dict["quit"] in keys:
			quit_experiment(win, core)


def get_subject_info(data_dir, experiment_name):

	""" GUI for entering experiment info
	:type data_dir: string
	:param data_dir: Data directory

	:type experiment_name: string
	:param experiment_name: Name of the experiment

	:raises: N/A

	:rtype:
	"""

	last_params_file_name = f"{data_dir}{experiment_name}_#_lastParams.json"
	try:
		# note the '#', for file-ordering purposes
		# exp_info = misc.fromFile(last_params_file_name)
		with open(last_params_file_name, 'r') as fp:
			exp_info = json.load(fp)
	except:
		exp_info = {
			'Experiment': experiment_name,
			'Testing Location': '',
			'Experimenter Initials': 'sdu',
			'Subject Initials': '',
			'Subject ID': '',
			'Subject Age': '',
			'Subject Gender': '',
		}

	exp_info['Start Date'] = data.getDateStr()
	dlg = gui.DlgFromDict(exp_info, title=experiment_name, fixed=['Start Date'])
	if dlg.OK:
		# misc.toFile(last_params_file_name, exp_info)
		with open(last_params_file_name, 'w') as fp:
			json.dump(exp_info, fp)
	else:
		core.quit()

	return exp_info


def make_data_file(data_dir, exp_info, info_order, sync=True):
	""" Creates a data file
	:type exp_info: dict
	:param exp_info: Dictionary of experiment information

	:type info_order: list
	:param info_order: List of strings specifying the output file header

	:type sync: bool
	:param sync:

	:raises: N/A

	:rtype: file handle
	"""

	file_name = "_".join([exp_info['Experiment'], exp_info['Subject ID'], exp_info['Subject Initials'],
						exp_info['Subject Age'], exp_info['Subject Gender'], exp_info['Start Date']])
	ext = ''
	i = 1
	while os.path.exists(f"{file_name}{ext}.txt"):  # changes filename extension to avoid overwriting
		ext = '-' + str(i)
		i += 1

	file_name = f"{data_dir}{file_name}{ext}"
	data_file = open(f"{file_name}.txt", 'a')
	line = tabify(info_order) + '\n'
	data_file.write(line)
	if sync:
		data_file.flush()
		os.fsync(data_file)

	return data_file


def make_subject_file(data_dir, exp_info, sub_info_order, sync=True):
	""" Creates a subject file for the experiment
	:type data_dir: string
	:param data_dir: Data directory

	:type exp_info: dict
	:param exp_info: Dictionary housing all experiment information

	:type sub_info_order: list
	:param sub_info_order: List of strings specifying output file header

	:type sync:
	:param sync:

	:raises: N/A

	:rtype: file_handle
	"""

	file_name = f"{data_dir}subFile_{exp_info['Experiment']}.txt"
	# Write headers if necessary
	if not os.path.exists(file_name):
		line = tabify(sub_info_order) + '\n'  # TABify
		with open(file_name, 'a') as sub_file:
			sub_file.write(line)

	sub_file = open(file_name, 'a')
	line = tabify([str(exp_info[variable]) for variable in sub_info_order])
	line += '\n'  # add a newline
	sub_file.write(line)
	if sync:
		sub_file.flush()
		os.fsync(sub_file)

	return sub_file

def write_to_file(file_handle, info, info_order, sync=True):
	""" Writes a trial (a dictionary) to a fileHandle
	:type file_handle:
	:param file_handle:

	:type info:
	:param info:

	:type info_order:
	:param info_order:

	:type sync:
	:param sync:

	:raises:

	:rtype: void
	"""

	line = tabify([str(info[variable]) for variable in info_order]) + '\n'
	file_handle.write(line)
	if sync:
		file_handle.flush()
		os.fsync(file_handle)

def quit_experiment(win, core):
	""" Quits an experiment
	:type win: psychopy.visual.Window
	:param win: The Window object from Psychopy

	:type core: psychopy.core
	:param core: The Core object from Psychopy

	:raises: N/A

	:rtype: void
	"""

	win.close()
	core.quit()

