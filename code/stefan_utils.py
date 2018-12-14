# Utility functions
# Author: Stefan Uddenberg

###############################
# Takes an array of strings and
# outputs a single string separated
# by tab characters
def tabify(s):
    s = '\t'.join(s)
    return s

################################
# Takes a tuple rgbVal on scale
# from 0 to 255 and returns a tuple
# along the scale of -1 to 1
# (with 0 being gray)
def rgb2psychorgb(rgbVal):
    return tuple((x - 127.5) / 127.5 for index, x in enumerate(rgbVal))
