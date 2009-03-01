#!/usr/bin/env python

#
# papertimer 0.0.1 -- Simple full-screen countdown timer
# Copyright (C) 2009 Christoph Sommer <mail@christoph-sommer.de>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# 

from Tkinter import *
import time
import os
import math

_VERSION = "0.0.1"
_BG = "blue"
_BGOUT = "red"
_FG = "white"
_FGWARN = "red"
_DIGITWIDTH = 32*1.5
_DIGITHEIGHT = 32*2*1.5
_SEGMENTWIDTH = _DIGITWIDTH / 6.0
_DIGITSPACING = _SEGMENTWIDTH

pausedAt = None
endTime = time.time() + 30*60
warnInterval = 5*60
prefixBuffer = 0  # buffers whatever gets input on the keyboard
prefixBufferExpires = time.time()  # time when the prefixBuffer will be cleared
last_draw_parameters = None

def draw_h_segment(c, x, y, w, h, segmentwidth, y_offset, fg):
	"""
	y_offset: 0, 0.5, or 1. Depending on y position to draw segment at
	"""
	x += 0
	y += y_offset * (h - segmentwidth)
	margin = 2
	c.create_polygon(x+0.5*segmentwidth+margin,y+0.5*segmentwidth, x+segmentwidth,y+segmentwidth-margin, x+w-segmentwidth,y+segmentwidth-margin, x+w-0.5*segmentwidth-margin,y+0.5*segmentwidth, x+w-segmentwidth,y+margin, x+segmentwidth,y+margin, fill=fg)

def draw_v_segment(c, x, y, w, h, segmentwidth, x_offset, y_offset, fg):
	"""
	x_offset: 0 or 1. Depending on x position to draw segment at
	y_offset: 0 or 1. Depending on y position to draw segment at
	"""
	x += x_offset * (w - segmentwidth)
	y += y_offset * (h/2.0)
	h = h/2.0-0.5*segmentwidth
	if y_offset==0: y+=0.5*segmentwidth
	margin = 2
	c.create_polygon(x+0.5*segmentwidth,y+margin, x+margin,y+0.5*segmentwidth, x+margin,y+h-0.5*segmentwidth, x+0.5*segmentwidth,y+h-margin, x+segmentwidth-margin,y+h-0.5*segmentwidth, x+segmentwidth-margin,y+0.5*segmentwidth, fill=fg)

def draw_colon(c, x, y, w, h, segmentwidth, fg):
	_COLONSPACING = h/6.0
	oy = y
	y = oy + 0.5 * h - 0.5*segmentwidth - _COLONSPACING
	c.create_polygon(x+0.5*segmentwidth,y, x+segmentwidth,y+0.5*segmentwidth, x+0.5*segmentwidth,y+segmentwidth, x,y+0.5*segmentwidth, fill=fg)
	y = oy + 0.5 * h - 0.5*segmentwidth + _COLONSPACING
	c.create_polygon(x+0.5*segmentwidth,y, x+segmentwidth,y+0.5*segmentwidth, x+0.5*segmentwidth,y+segmentwidth, x,y+0.5*segmentwidth, fill=fg)

def draw_digit(c, x, y, w, h, segmentwidth, digit, fg):
	"""
	 1
	4 5
	 2
	6 7
	 3
	"""
	segments = ()
	if digit == "0": segments = (1, 3, 4, 5, 6, 7)	
	if digit == "1": segments = (5, 7)	
	if digit == "2": segments = (1, 2, 3, 5, 6)	
	if digit == "3": segments = (1, 2, 3, 5, 7)	
	if digit == "4": segments = (2, 4, 5, 7)	
	if digit == "5": segments = (1, 2, 3, 4, 7)	
	if digit == "6": segments = (1, 2, 3, 4, 6, 7)	
	if digit == "7": segments = (1, 5, 7)	
	if digit == "8": segments = (1, 2, 3, 4, 5, 6, 7)	
	if digit == "9": segments = (1, 2, 3, 4, 5, 7)	
	if 1 in segments: draw_h_segment(c, x, y, w, h, segmentwidth, 0, fg)
	if 2 in segments: draw_h_segment(c, x, y, w, h, segmentwidth, 0.5, fg)
	if 3 in segments: draw_h_segment(c, x, y, w, h, segmentwidth, 1, fg)
	if 4 in segments: draw_v_segment(c, x, y, w, h, segmentwidth, 0, 0, fg)
	if 5 in segments: draw_v_segment(c, x, y, w, h, segmentwidth, 1, 0, fg)
	if 6 in segments: draw_v_segment(c, x, y, w, h, segmentwidth, 0, 1, fg)
	if 7 in segments: draw_v_segment(c, x, y, w, h, segmentwidth, 1, 1, fg)

def draw_number(c, x, y, w, h, segmentwidth, number, fg):
	if number == ":":
		draw_colon(c, x, y, w, h, segmentwidth, fg)
	else:
		if number > 99: number = 99
		digit1 = number / 10
		digit2 = number % 10
		draw_digit(c, x, y, w, h, segmentwidth, str(digit1), fg)
		draw_digit(c, x + w + _DIGITSPACING, y, w, h, segmentwidth, str(digit2), fg)
	
def draw_time(c, x, y, seconds, drawColon=True, warn=False):
	seconds = int(seconds)
	minutes = seconds / 60
	seconds = seconds % 60
	draw_number(c, x, y, _DIGITWIDTH, _DIGITHEIGHT, _SEGMENTWIDTH, minutes, fg=(_FG, _FGWARN)[warn])
	if drawColon: draw_number(c, x + 2 * _DIGITWIDTH + 2 * _DIGITSPACING, 0.4*_DIGITHEIGHT+y, 0.6*_DIGITWIDTH, 0.6*_DIGITHEIGHT, 0.6*_SEGMENTWIDTH, ":", fg=(_FG, _FGWARN)[warn])
	draw_number(c, x + 2 * _DIGITWIDTH + 3 * _DIGITSPACING + 0.6*_DIGITSPACING, 0.4*_DIGITHEIGHT+y, 0.6*_DIGITWIDTH, 0.6*_DIGITHEIGHT, 0.8*_SEGMENTWIDTH, seconds, fg=(_FG, _FGWARN)[warn])

def OnPressSpace(event):
	global pausedAt, endTime

	if pausedAt == None:
		pausedAt = endTime - time.time()
	else:
		endTime = time.time() + pausedAt
		pausedAt = None

	draw()

def OnConfigure(event):
	draw(force=True)

def OnQuit(event):
	root.quit()

def OnPressDigit(event):
	global prefixBuffer, prefixBufferExpires

	c = event.char
	d = 0
	if c == "0": d = 0
	if c == "1": d = 1
	if c == "2": d = 2
	if c == "3": d = 3
	if c == "4": d = 4
	if c == "5": d = 5
	if c == "6": d = 6
	if c == "7": d = 7
	if c == "8": d = 8
	if c == "9": d = 9
	if prefixBufferExpires <= time.time():
		prefixBuffer = 0
	prefixBuffer = 10 * prefixBuffer + d*60
	prefixBufferExpires = time.time() + 1

def OnPressEnter(event):
	global prefixBuffer, prefixBufferExpires
	global endTime, pausedAt

	if prefixBufferExpires <= time.time():
		prefixBuffer = 0
	if prefixBuffer == 0:
		prefixBuffer = 30*60
	endTime = time.time() + prefixBuffer
	if pausedAt != None:
		pausedAt = prefixBuffer
	prefixBuffer = 0

	draw()

def OnPressPlus(event):
	global prefixBuffer, prefixBufferExpires
	if prefixBufferExpires <= time.time():
		prefixBuffer = 0
	if prefixBuffer == 0:
		prefixBuffer = 1*60

	addTime(+prefixBuffer)

	prefixBuffer = 0

def OnPressMinus(event):
	global prefixBuffer, prefixBufferExpires
	if prefixBufferExpires <= time.time():
		prefixBuffer = 0
	if prefixBuffer == 0:
		prefixBuffer = 1*60

	addTime(-prefixBuffer)

	prefixBuffer = 0

def OnPressS(event):
	global prefixBuffer, prefixBufferExpires
	if prefixBufferExpires <= time.time():
		prefixBuffer = 0
	if prefixBuffer == 0:
		prefixBuffer = 10*60
	prefixBuffer /= 60
	prefixBufferExpires = time.time() + 1

def addTime(seconds):
	global endTime, pausedAt

	if endTime < time.time():
		endTime = time.time()
		if pausedAt != None:
			pausedAt = 0
	endTime += seconds
	if pausedAt != None:
		pausedAt += seconds

	draw()

def draw(force = False):
	global _DIGITWIDTH, _DIGITHEIGHT, _SEGMENTWIDTH, _DIGITSPACING
	global last_draw_parameters

	w = c.winfo_width()
	h = c.winfo_height()
	_DIGITWIDTH = w / 4.3
	_DIGITHEIGHT = _DIGITWIDTH * 2
	_SEGMENTWIDTH = _DIGITWIDTH / 6.0
	_DIGITSPACING = _SEGMENTWIDTH 
	x = _DIGITSPACING
	y = 0.5 * (h - _DIGITHEIGHT) 

	remainingTime = endTime - time.time()
	if pausedAt != None:
		remainingTime = pausedAt
	remainingSeconds = int(math.ceil(remainingTime))

	warn = False
	if remainingSeconds <= warnInterval:
		#if int(remainingTime * 2) % 2 != 0:
		warn = True

	seconds = max(0, remainingSeconds/10*10)
	colon = (remainingSeconds % 2 == 0) or (pausedAt != None)
	bgcolor = _BG
	if remainingSeconds <= 0 and remainingSeconds % 2 == 0:
		bgcolor = _BGOUT

	draw_parameters = (x, y, seconds, colon, warn, bgcolor)
	if draw_parameters != last_draw_parameters or force:
		c.delete(ALL)
		c.config(bg = bgcolor)
		draw_time(c, x, y, seconds=seconds, drawColon=colon, warn=warn)
		last_draw_parameters = draw_parameters
	
def tick():
	draw()
	root.after(100, tick)


root = Tk()
root.title("papertimer %s" % (_VERSION));
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
#root.overrideredirect(1)
root.geometry("%dx%d+0+0" % (w, h))
#root.wm_attributes('-fullscreen', 1)
c = Canvas(master=root, width=800, height=600, bg=_BG)
c.pack(fill=BOTH, expand=YES)
#c.place(x=0, y=0)
root.bind("<space>", OnPressSpace)
root.bind("<Return>", OnPressEnter)
root.bind("<Configure>", OnConfigure)
root.bind("<Escape>", OnQuit)
if os.uname()[0] == "Darwin":
	root.bind("<Command-q>", OnQuit)
for i in range(0, 10): root.bind(str(i), OnPressDigit)
root.bind("+", OnPressPlus)
root.bind("-", OnPressMinus)
root.bind("s", OnPressS)
root.bind("<Up>", OnPressPlus)
root.bind("<Down>", OnPressMinus)
tick()
root.mainloop()
