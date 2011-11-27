#!/usr/bin/env python
"""
    BrainWave : Binaural beat generator (C) Raja Jamwal 2011, <www.experiblog.co.cc> 
    <linux1@zoho.com>

    Distributed under GNU GPL License

    Brainwave, is a pretty advance binaural beat generator program
    Copyright (C) 2011  Raja Jamwal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import gtk
import pygst
pygst.require("0.10")
import gst
import time
from optparse import OptionParser
import types
import gobject
import sys
gobject.threads_init()
import re

freq_table = [
	["delta", 0, 4],
	["theta", 4, 8],
	["alpha", 8, 13],
	["beta", 13, 30],
	["gamma", 30, 100],
	["mu", 8, 13]
	]

overlay_list = [[0],[0],[0],[" "],[0]]
"""first line is freq table, second line is freq channel volume, thrid is freq pan value
,fourth is files(audio) paths, fifth is audio volumes, sixth is audio pan values"""
sequential_list = [[" "],[0]]
which_audio =1
filename = None

def diff_freq(a ,b):
	if a>b:
		return a-b
	else:
		return b-a

def print_info(line):
	print "--> "+line

def on_message(player):
	player.set_property("uri", player.get_property('uri'))

def sequence(player):
	global which_audio
	which_audio+=1
	if(which_audio>=len(sequential_list[0])):
		which_audio =1
	print_info("Generating seq "+str(which_audio)+" audio:\""+str(sequential_list[0][which_audio])+"\" vol:"+str(sequential_list[1][which_audio])+"%")
	player.set_property("uri", "file://"+sequential_list[0][which_audio])
	
def create_sequentials():	
	#print_info( sequential_list[0][i])
	if str(sequential_list[0][1]) == " ":
		return 1;
	print_info("Generating seq "+str(which_audio)+" audio:\""+str(sequential_list[0][1])+"\" vol:"+str(sequential_list[1][1])+"%")
	player = gst.element_factory_make("playbin2", "player")
	player.set_property("volume", float(sequential_list[1][1])/100)
	player.set_property('uri', 'file://'+str(sequential_list[0][1]))
	player.connect("about-to-finish", sequence)
	player.set_state(gst.STATE_PLAYING)
	
def create_overlays():
  if int(overlay_list[0][1]) != 0:
    for i in range(1, len(overlay_list[0])):
	# left pipeline
	print_info("Generating overlay frq:"+str(overlay_list[0][i])+"Hz,vol:"+str(overlay_list[1][i])+"%Pan:"+str(overlay_list[1][i])) 
	over_frq = gst.Pipeline("overlay_frequency_pipe")
        audiotestsrc = gst.element_factory_make("audiotestsrc", "audio")
        audiotestsrc.set_property("freq", float(overlay_list[0][i]))
	audiotestsrc.set_property("volume", float(overlay_list[1][i])/100)

	pan = gst.element_factory_make("audiopanorama", "panner")
	pan.set_property("panorama", float(overlay_list[2][i])/100)
        sink = gst.element_factory_make("alsasink", "sink")

        over_frq.add(audiotestsrc, pan, sink)
        gst.element_link_many(audiotestsrc, pan, sink)
	over_frq.set_state(gst.STATE_PLAYING)

  if str(overlay_list[3][1]) != " ":
    for i in range(1, len(overlay_list[3])):
	#creates a playbin (plays media form an uri) 
	print_info("Generating overlay audio:\""+str(overlay_list[3][i])+"\" vol:"+str(overlay_list[4][i])+"%")
	player = gst.element_factory_make("playbin2", "player"+str(i))
	player.set_property("volume", float(overlay_list[4][i])/100)
	player.set_property('uri', 'file://'+str(overlay_list[3][i]))
	player.connect("about-to-finish", on_message)
	player.set_state(gst.STATE_PLAYING)
        
def generate_channel(left_freq, left_vol, right_freq, right_vol, bg_file, bg_vol):
	print_info("Inducing "+str(diff_freq(left_freq, right_freq))+"Hz brainwave")
	print_info("Left freq "+str(left_freq)+"Hz : Right freq "+str(right_freq)+"Hz")
	print_info("Base freq volume left:"+str(left_vol*100)+" right:"+str(right_vol*100)) 
	# left pipeline
	left_pipe = gst.Pipeline("left_pipe")
        audiotestsrc_left = gst.element_factory_make("audiotestsrc", "audio")
        audiotestsrc_left.set_property("freq", left_freq)
	audiotestsrc_left.set_property("volume", float(left_vol))

	pan_left = gst.element_factory_make("audiopanorama", "panner")
	pan_left.set_property("panorama", -1.0)
        sink_left = gst.element_factory_make("alsasink", "sink")

        left_pipe.add(audiotestsrc_left, pan_left, sink_left)
        gst.element_link_many(audiotestsrc_left, pan_left, sink_left)
	left_pipe.set_state(gst.STATE_PLAYING)


	# right pipeline
	right_pipe = gst.Pipeline("left_pipe")
        audiotestsrc_right = gst.element_factory_make("audiotestsrc", "audio")
        audiotestsrc_right.set_property("freq", right_freq)
	audiotestsrc_right.set_property("volume", float(right_vol))

	pan_right = gst.element_factory_make("audiopanorama", "panner")
	pan_right.set_property("panorama", 1.0)
        sink_right = gst.element_factory_make("alsasink", "sink")

        right_pipe.add(audiotestsrc_right, pan_right, sink_right)
        gst.element_link_many(audiotestsrc_right, pan_right, sink_right)

	right_pipe.set_state(gst.STATE_PLAYING)

	#creates a playbin (plays media form an uri)
	print_info("Using bg audio \""+str(bg_file)+"\" vol:"+str(float(bg_vol)*100)+"%") 
	player = gst.element_factory_make("playbin2", "player")
	player.set_property("volume", float(bg_vol))
	player.set_property('uri', 'file://'+bg_file)
	player.connect("about-to-finish", on_message)
	player.set_state(gst.STATE_PLAYING)
	
	create_overlays()
	create_sequentials()

	
class brainwave:
    def __init__(self):
	global filename
	global overlay_list
	base_freq = 400
	bg_file = ""	
	parser = OptionParser()
	parser.set_defaults( left_frq = 400, left_vol=100, right_frq = 408, right_vol=100, wait_t=5, wave="", base=400, file_name="", bg_vol=100, overlay_frq="0;0;0" , overlay_audio=" ;0", seq_audio=" ;0") 
	parser.add_option("--left",action="store",dest="left_frq",help="" )
	parser.add_option("--left-volume", action="store", dest="left_vol", help="")
	parser.add_option("--right",action="store",dest="right_frq",help="" )
	parser.add_option("--right-volume", action="store", dest="right_vol", help="")
	parser.add_option("--time",action="store",dest="wait_t",help="" )	
	parser.add_option("--wave",action="store",dest="wave",help="" )
	parser.add_option("--base",action="store",dest="base",help="" )
	parser.add_option("--bg",action="store",dest="file_name",help="" )
	parser.add_option("--bg-volume",action="store",dest="bg_vol",help="" )
	parser.add_option("--overlay-frequency",action="store",dest="overlay_frq",help="" )
	parser.add_option("--overlay-audio",action="store",dest="overlay_audio",help="" )
	parser.add_option("--sequential-audio",action="store",dest="seq_audio",help="" )
	(options, args) = parser.parse_args()
	base_freq = int(options.base)
	filename = bg_file = options.file_name
	pattern = re.compile(",")
	pattern1 = re.compile(";")
	# process freq list in format (freq;vol;pan)
	frq_list = re.split(pattern, options.overlay_frq)
	for i in range(0, len(frq_list)):	
		temp = re.split(pattern1, frq_list[i])
		overlay_list[0].append(temp[0])
		overlay_list[1].append(temp[1])
		overlay_list[2].append(temp[2])
		
	# process audio list in format (freq;vol;pan) TODO: implement pan for audio overlays
	audio_list = re.split(pattern, options.overlay_audio)
	for i in range(0, len(audio_list)):	
		temp = re.split(pattern1, audio_list[i])
		overlay_list[3].append(temp[0])
		overlay_list[4].append(temp[1])
		#overlay_list[5].append(temp[2]) TODO: create audio-overlay panning
	
	#process audio list in format (freq;vol;pan) TODO: implement pan for sequential audio		
	seq_list = re.split(pattern, options.seq_audio)
	for i in range(0, len(seq_list)):	
		temp = re.split(pattern1, seq_list[i])
		sequential_list[0].append(temp[0])
		sequential_list[1].append(temp[1])
		#overlay_list[5].append(temp[2]) TODO: create audio-overlay panning
			
	
	#print bg_file
	print_info("Brainwave : Binaural beat generator 0.1 alpha") 
	print_info("Copyright (C) Raja Jamwal, <linux1@zoho.com>\n")
	print_info("This program is free software: you can redistribute it and/or modify")
    	print_info("it under the terms of the GNU General Public License as published by")
    	print_info("the Free Software Foundation, either version 3 of the License, or")
    	print_info("(at your option) any later version.")

    	print_info("This program is distributed in the hope that it will be useful,")
    	print_info("but WITHOUT ANY WARRANTY; without even the implied warranty of")
    	print_info("MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
    	print_info("GNU General Public License for more details.\n")


	if(options.wave ==""):
		generate_channel(options.left_frq, float((options.left_vol))/100, options.right_frq, float((options.right_vol))/100, options.file_name, float(options.bg_vol)/100)
	else:
		lft = 0
		rgt = 0
		is_wave_found = False
		for i in range(0, len(freq_table)):
			if (freq_table[i][0] == options.wave):
				print_info("Inducing "+freq_table[i][0]+" wave")
				generate_channel(base_freq, float((options.left_vol))/100, base_freq+(freq_table[i][2]+freq_table[i][1])/2, float((options.right_vol))/100, options.file_name, float(options.bg_vol)/100)
				is_wave_found = True

		if(is_wave_found == False):
			print_info("Error : Invalid brain wave specified, "+options.wave)
		
	time.sleep(float(options.wait_t));


if __name__ == "__main__":
    instance = brainwave()
    #instance.main()
