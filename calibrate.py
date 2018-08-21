#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Christopher Brown
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this script.  If not, see <http://www.gnu.org/licenses/>.
#
# Bug reports, bug fixes, suggestions, enhancements, or other 
# contributions are welcome. Go to http://www.github.com/cbrown1/calibrate 
# for more information and to contribute. Or send an e-mail to: 
# cbrown1@pitt.edu.
#

import sys
import time

import asciimatics as am
import asciimatics.widgets as am_widgets
import asciimatics.scene as am_scene
import asciimatics.screen as am_screen
import asciimatics.exceptions as am_exceptions
from asciimatics.event import KeyboardEvent
from collections import defaultdict

import numpy as np
import scipy.signal
import medussa as m
#import psylab


class get_input(am_widgets.Frame):
    
    """A generic full-screen menu form that can handle three types of menu options:
        
          - asciimatics frames: move back and forth between menu screens (am frames)
          - functions: run arbitrary functions, with access to all available data
          - variables: update variables, display their current state, specify 
              defaults & (numeric) var types. Var types must be numeric (float, int, 
              etc) at this point. This is because the interface is designed to make
              navigation as efficient as possible, so that a single keypress is 
              interpreted as a menu selection. Since letter keys are used for menus,
              if letters were allowed to be used in updating variables, it would be 
              impossible to know which was intended by the user. The usecase also 
              required many numeric variables but no text, so this is not a problem. 


    """
    def __init__(self, screen):
        super(get_input, self).__init__(screen,
                                        screen.height,
                                        screen.width,
                                        title="Calibrate!")

        self.number_keys = [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'), ord('0'), ord('.') ]
        layout1 = am_widgets.Layout([1], fill_frame=False)
        layout2 = am_widgets.Layout([2,8], fill_frame=False)
        layout3 = am_widgets.Layout([91,9], fill_frame=False)
        self._nav = am_widgets.Label(self.nav)
        self._hl = am_widgets.Divider()
        self._blankline = am_widgets.Divider(height=1, draw_line=False)
        self._psylab = am_widgets.Label(u"psylab")
        # The listbox takes up 1 more line than is visible, because quit is added after
        # the height is computed. So setting height to FILL_FRAME pushes the bottom line 
        # of the visible screen. There are 9 additional lines on the screen other than
        # the listbox, so subtract 9 from screen. 
        list_height = self._screen.height - 9 
        self._list = am_widgets.ListBox(
            list_height,
#            am_widgets.Widget.FILL_FRAME,
            options=[],
            on_change=self._on_change,
            on_select=self._on_select,
            name="list_main",
            )
        self.enter_key = u"\u21B2"
        self.keys = []
        n = 0
        has_val = False
        for val in self.options:
            if len(val['desc']) > n:
                n = len(val['desc'])
            if val['type'] not in ["frame", "func"]:
                has_val = True
        fmt_key  = u"    {}{} :  "
        fmt_desc = u"{{:{:}}}".format(n)
        fmt_cur_ = u"   {}"
        for val in self.options:
            val["fmt_key"] = fmt_key
            val["fmt_desc"] = fmt_desc.format(val["desc"])
            if val.has_key("cur_str"):
                val["fmt_cur"] = fmt_cur_.format(val["cur_str"])
            else:
                val["fmt_cur"] = ""
            self.keys.append(ord(val["key"]))
        if has_val:
            expl = u"Option :  " + fmt_desc.format("Explanation") + u"   [value]"
        else:
            expl = u"Option :  Explanation"
        self._explain = am_widgets.Label(expl)
        self.instructions_no_opt = u"Choose an option"
        self.instructions_opt = u"Choose an option or type value (blank=default), enter to update."
        self._instructions = am_widgets.Label(self.instructions_no_opt)
        self._input_label = am_widgets.Label("Enter a value: ")
        self._input = am_widgets.Text(name="input")
        self.add_layout(layout1)
        self.add_layout(layout2)
        self.add_layout(layout3)
        layout1.add_widget(self._nav)
        layout1.add_widget(self._hl)
        layout1.add_widget(self._explain)
        layout1.add_widget(self._blankline)
        layout1.add_widget(self._list)
        layout2.add_widget(self._input_label)
        layout2.add_widget(self._input, column=1)
        layout2.add_widget(self._blankline)
        layout3.add_widget(self._instructions)
        layout3.add_widget(self._psylab, column=1)
        self.fix()
        self._input.disabled = True
        self._input_label.disabled = True
        self.current_type = None
#        self._list.value = 0
#        self._list._on_select()

        # Add my own colour palette
        self.palette = defaultdict(
            lambda: (am_screen.Screen.COLOUR_WHITE, am_screen.Screen.A_NORMAL, am_screen.Screen.COLOUR_BLACK))
        for key in ["selected_focus_field", "label"]:
            self.palette[key] = (am_screen.Screen.COLOUR_WHITE, am_screen.Screen.A_BOLD, am_screen.Screen.COLOUR_BLACK)
        self.palette["title"] = (am_screen.Screen.COLOUR_BLACK, am_screen.Screen.A_BOLD, am_screen.Screen.COLOUR_WHITE)
        self.palette["disabled"] = (am_screen.Screen.COLOUR_BLACK, am_screen.Screen.A_NORMAL, am_screen.Screen.COLOUR_BLACK)


    def process_event(self, event):

        unhandled = True
        if isinstance(event, am.event.KeyboardEvent):


            # self._scene.add_effect(
            #    am_widgets.PopUpDialog(self._screen,
            #                            "{:}".format(event.key_code),
            #                            ["Cancel", "OK"],
            #                            on_close=self._confirm_quit))
            if event.key_code in self.keys:
                self._list.value = self.keys.index(event.key_code)
                self._list._on_select()
                unhandled = False

            elif event.key_code in [ord('q')]:
                self._list.value = len(self.options)
                self._list._on_select()
                unhandled = False

            elif self._list.value != None:
                # self._scene.add_effect(
                #   am_widgets.PopUpDialog(self._screen,
                #                           "Value!",
                #                           ["Cancel", "OK"],
                #                           on_close=self._confirm_quit))
                if self._list.value < len(self.options):
                    # self._scene.add_effect(
                    #   am_widgets.PopUpDialog(self._screen,
                    #                           "Option!",
                    #                           ["Cancel", "OK"],
                    #                           on_close=self._confirm_quit))
                    if self.options[self._list.value]["type"] not in ['frame', 'func']:
                        # self._scene.add_effect(
                        #   am_widgets.PopUpDialog(self._screen,
                        #                           "Var!",
                        #                           ["Cancel", "OK"],
                        #                           on_close=self._confirm_quit))
                        if event.key_code in [10]:
                            # User hit enter. Update 
                            if self._input.value == "":
                                # Textbox has no value, update the selected var with default
                                self.options[self._list.value]["val"] = self.options[self._list.value]["default"]
                            else:
                                # Textbox is not empty; Update the selected var with val from textbox
                                self.options[self._list.value]["val"] = self.options[self._list.value]["type"](self._input.value)
                            self._list._on_select()
                            # Empty the textbox
                            self._input.value = ""
                            unhandled = False

                        elif event.key_code in [-300]:
                            # Backspace key; delete last character in textbox
                            self._input.value = self._input.value[:-1]
                            unhandled = False
                        elif event.key_code in self.number_keys:
                            self._input.value = self._input.value + chr(event.key_code)
                            unhandled = False
        
        if unhandled:
            # Pass unhandled events to lower levels for normal handling
            return super(get_input, self).process_event(event)


    def _on_select(self):

        if self._list.value == len(self.options):
            self._scene.add_effect(
                am_widgets.PopUpDialog(self._screen,
                                        "Really quit?",
                                        ["No", "Yes"],
                                        on_close=self._confirm_quit))

        elif self.options[self._list.value]["type"] == "frame":
            # Item is a frame; Go there
            key = self.options[self._list.value]["key"]
            frame = self.options[ self.keys.index(ord(key)) ] ["val"]
            self.next_scene(frame)

        elif self.options[self._list.value]["type"] == "func":
            # Item is a function; Call it
            ret = getattr(self, self.options[self._list.value]["val"])()

        else:
            # Re-populate the listbox to update the value that changed
            self.populate_list()
            # Force a redraw
            self._screen.force_update()


    def _on_change(self):

        if self._list.value != None: 
            if self._list.value < len(self.options):
                if self.options[self._list.value]["type"] in ["func", "frame"]:
                    self._instructions.text = self.instructions_no_opt
                    self._input.disabled = True
                    self._input_label.disabled = True
                    self._input_label.custom_colour = self.palette['label']
                    self._input.blur()
                else:
                    self._instructions.text = self.instructions_opt
                    self._input.disabled = False
                    self._input_label.disabled = False
                    self._input_label.custom_colour = self.palette['disabled']
                    self._input.focus()

            elif self._list.value == len(self.options):
                # Quit; update in case user cancels
                self._instructions.text = self.instructions_no_opt
                self._input.disabled = True
                self._input_label.disabled = True
                self._input_label.custom_colour = self.palette['label']
                self._input.blur()

        # Redraw
        self._screen.force_update()


    def populate_list(self):

        # Get current value of the listbox
        value = self._list.value
        options_l = []
        for i, val in enumerate(self.options):
            if i == value and val["type"] not in ["func", "frame"]:
                # This listbox item is the selected on; use special prompt (pound sign & enter char)
                key = val["fmt_key"].format(u"#", self.enter_key)
            else:
                # This listbox item is not the selected on; use normal prompt (a char)
                key = val["fmt_key"].format(val['key'], u" ")
            # fmt_desc is already expanded since it doesn't change
            desc = val["fmt_desc"]
            if val.has_key("val"):
                cur_val = val["fmt_cur"].format(unicode(val["val"]))
            else:
                cur_val = ""
            options_l.append((key + desc + cur_val, len(options_l)))

        # Add quit to the list
        key = val["fmt_key"].format("q", u" ")

        options_l.append((key+"Quit", len(options_l)))

        # Assign the newly created options to the listbox
        self._list.options = options_l
        # Select the previously selected option
        self._list.value = value


    def _update(self, frame_no):

        if self._list.value < len(self.options):
            self.populate_list()

#        elif value == len(self.options):
#            self._scene.add_effect(
#                am_widgets.PopUpDialog(self._screen,
#                            "Really quit?",
#                            ["No", "Yes"],
#                            on_close=self._confirm_quit))

        super(get_input, self)._update(frame_no)

    @staticmethod
    def _confirm_quit(selected):
        # Yes is the second button
        if selected == 1:
            raise am_exceptions.StopApplication("User requested exit")

    @staticmethod
    def next_scene(frame):
        raise am_exceptions.NextScene(frame)


class Frame_Main(get_input):

    nav = "Main"
    options = [
               {"key": "t", 
                "desc": "Use pure tones",
                "type": "frame",
                "val": "Frame_Tone",
               },
               {"key": "n", 
                "desc": "Use noise", 
                "type": "frame",
                "val": "Frame_Noise",
               },
              ]


class Frame_Tone(get_input):
    nav = "Main / Tone"
    options = [
               {"key": "f",            # The key to press to select this option
                "desc": "Frequency",   # A description of this option
                "type": float,         # The type of menu item this is; frame, func, or a var type
                "val": 1000.,          # If frame or func, the name; if var type, holds the value
                "cur_str": "[{:} Hz]", # A format string to display the current value (var only)
                "default": 1000.,      # A default value, applied when no value is entered (var only)
               },
               {"key": "a", 
                "desc": "Amplitude",
                "val": 1.,
                "cur_str": "[{:} v]",  
                "default": 1.,
                "type": float,
               },
               {"key": "d", 
                "desc": "Duration",
                "val": 10.,
                "cur_str": "[{:} s]", 
                "default": 10.,
                "type": float,
               },
               {"key": "i",
                "desc": "Portaudio device id",
                "val": 0,
                "cur_str": "[{:}]", 
                "default": 0,
                "type": int,
               },
               {"key": "s",
                "desc": "Sample rate",
                "val": 44100.,
                "cur_str": "[{:} Hz]", 
                "default": 44100.,
                "type": float,
               },
               {"key": "n",
                "desc": "Number of output channels",
                "val": 2,
                "cur_str": "[{:} channels]", 
                "default": 2,
                "type": int,
               },
               {"key": "o",
                "desc": "Output channel",
                "val": 1,
                "cur_str": "[channel {:}]", 
                "default": 1,
                "type": int,
               },
                {"key": "p", 
                 "desc": "Play stimulus",
                 "type": "func",
                 "val": "play",
                },
                {"key": "b",
                 "desc": "Back",
                 "type": "frame",
                 "val": "Frame_Main",
                },
               ]

    def play(self):

        # Get values
        i = self.options[ self.keys.index(ord('i')) ]["val"]
        s = self.options[ self.keys.index(ord('s')) ]["val"]
        n = self.options[ self.keys.index(ord('n')) ]["val"]
        o = self.options[ self.keys.index(ord('o')) ]["val"]

        f = self.options[ self.keys.index(ord('f')) ]["val"]
        a = self.options[ self.keys.index(ord('a')) ]["val"]
        d = self.options[ self.keys.index(ord('d')) ]["val"]

        # Create tone
        dur = np.int32((np.float32(d) * s))
        freq = np.ones(dur) * f
        signal = np.sin(2. * np.pi * np.cumsum(freq) / s)

        # 20-ms ramps
        rdur = np.int(np.round(.02*s))
        rf = np.hanning(np.int32(2.*rdur))
        signal[0:rdur] = signal[0:rdur] * rf[0:rdur]
        signal[-(rdur-1):] = signal[-(rdur-1):] * rf[-(rdur-1):,]

        dev = m.open_device(i,i,n)
        stream = dev.open_array(signal, s)
        mm = stream.mix_mat
        mm[:] = 0
        mm[o-1] = 1
        stream.mix_mat = mm
        self.disabled = True
        inst = self._instructions.text
        self._instructions.text = "Playing tone..."
        self._screen.force_update()
        stream.play()
        while stream.is_playing:
            time.sleep(.1)
        self.disabled = False
        self._instructions.text = inst
        self._screen.force_update()


class Frame_Noise(get_input):
    nav = "Main / Noise"
    options = [
               {"key": "c", 
                "desc": "Center frequency",
                "cur_str":  "[{:} Hz]", 
                "val": 1000., 
                "default": 1000.,
                "type": float,
               },
               {"key": "w", 
                "desc": "Bandwidth",
                "val": .333333,
                "cur_str":  "[{:} oct]",  
                "default": .333333,
                "type": float,
               },
               {"key": "r", 
                "desc": "Root-mean-square",
                "val": .18,
                "cur_str":  "[{:} v]",  
                "default": .18,
                "type": float,
               },
               {"key": "a", 
                "desc": "Attenuation",
                "val": 0.,
                "cur_str":  "[{:} dB]", 
                "type": float,
                "default": 0.,
               },
               {"key": "d",
                "desc": "Duration",
                "val": 10.,
                "cur_str":  "[{:} s]", 
                "default": 10.,
                "type": float,
               },
               {"key": "i",
                "desc": "Portaudio device id",
                "val": 0,
                "cur_str": "[{:}]", 
                "default": 0,
                "type": int,
               },
               {"key": "s",
                "desc": "Sample rate",
                "val": 44100.,
                "cur_str": "[{:} Hz]", 
                "default": 44100.,
                "type": float,
               },
               {"key": "n",
                "desc": "Number of output channels",
                "val": 2,
                "cur_str": "[{:} channels]", 
                "default": 2,
                "type": int,
               },
               {"key": "o",
                "desc": "Output channel",
                "val": 1,
                "cur_str": "[channel {:}]", 
                "default": 1,
                "type": int,
               },
               {"key": "p",
                "desc": "Play stimulus",
                "type": "func",
                "val": "play",
               },
               {"key": "b",
                "desc": "Back",
                "type": "frame",
                "val": "Frame_Main",
               },
              ]

    def play(self):

        # Get values
        i = self.options[ self.keys.index(ord('i')) ]["val"]
        s = self.options[ self.keys.index(ord('s')) ]["val"]
        n = self.options[ self.keys.index(ord('n')) ]["val"]
        o = self.options[ self.keys.index(ord('o')) ]["val"]

        c = self.options[ self.keys.index(ord('c')) ]["val"]
        w = self.options[ self.keys.index(ord('w')) ]["val"]
        r = self.options[ self.keys.index(ord('r')) ]["val"]
        a = self.options[ self.keys.index(ord('a')) ]["val"]
        d = self.options[ self.keys.index(ord('d')) ]["val"]

        # Create noise
        signal = np.random.randn(np.int32(d*s))
        # RMS
        signal = signal * (r / np.sqrt(np.mean(np.square(signal))))
        # Atten
        signal = signal * np.exp(np.float32(-a)/8.6860)

        # Filter
        hp = np.round(c*(2.**np.float32(-w/2.)));
        lp = np.round(c*(2.**np.float32(w/2.)));
        bh,ah = scipy.signal.butter(6, hp/(s/2.), btype='high')
        signal = scipy.signal.lfilter(bh, ah, signal)
        bl,al = scipy.signal.butter(6, lp/(s/2.))
        signal = scipy.signal.lfilter(bl, al, signal)

        # 20-ms ramps
        rdur = np.int(np.round(.02*s))
        rf = np.hanning(np.int32(2.*rdur))
        signal[0:rdur] = signal[0:rdur] * rf[0:rdur]
        signal[-(rdur-1):] = signal[-(rdur-1):] * rf[-(rdur-1):,]

        # Access hardware
        dev = m.open_device(i,i,n)
        stream = dev.open_array(signal, s)
        mm = stream.mix_mat
        mm[:] = 0
        mm[o-1] = 1
        stream.mix_mat = mm
        self.disabled = True
        inst = self._instructions.text
        self._instructions.text = "Playing noise; {:}-{:} Hz".format(hp,lp)
        self._screen.force_update()
        self._screen.force_update()
        stream.play()
        while stream.is_playing:
            time.sleep(.1)
        self.disabled = False
        self._instructions.text = inst
        self._screen.force_update()


def main(screen, scene):
    scenes = [
        am_scene.Scene([Frame_Main(screen)], -1, name="Frame_Main"),
        am_scene.Scene([Frame_Tone(screen)], -1, name="Frame_Tone"),
        am_scene.Scene([Frame_Noise(screen)], -1, name="Frame_Noise"),
    ]
    screen.play(scenes, stop_on_resize=True, start_scene=scene)

last_scene = None
while True:
    try:
        am_screen.Screen.wrapper(main, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except am_exceptions.ResizeScreenError as e:
        last_scene = e.scene
