import time
import numpy as np

import medussa as m
import psylab

menu_max_size = 14

class menus:

    main = """Calibrate!

Options - Explanations:

      t - Use pure tones
      n - Use noise
      d - Specify device options
      q - Quit
"""

    device = """Calibrate! > Device Options

Options - Explanations:

      i - Specify the portaudio device id. current value: {:} [default: 0]
      f - Specify the sample rate. current value: {:} [default: 44100 Hz]
      n - Specify the number of output channels. current value: {:} [default: 2]
      c - Specify the output channel to use. current value: {:} [default: 1]
      b - Back to main menu
"""

    noise = """Calibrate! > Noise

Options - Explanations:

      c - Specify center frequency in Hz. current value: {:} [default: 1000 Hz]
      w - Specify bandwidth in octaves. current value: {:} [default: .33333 Hz]
      r - Specify rms in v.  current value: {:} [default: 0 dB]
      a - Specify amplitude in dB.  current value: {:} [default: 0 dB]
      d - Specify duration in s.   current value: {:} [default: 10 s]
      p - Play stimulus with current parameters
      b - Back to main menu
"""

    noise_rms =  """Calibrate! > Noise > Specify rms in v

Options - Explanations:

 x <= 0 - New rms. Values are v 
      d - Default rms (.18)
[blank] - Leave unchanged
"""

    noise_amp =  """Calibrate! > Noise > Specify amplitude in dB

Options - Explanations:

 x <= 0 - New amplitude. Values are dB atten from max 
      d - Default amplitude (1)
[blank] - Leave unchanged
"""

    noise_dur =  """Calibrate! > Noise > Specify duration in seconds

Options - Explanations:

  0 < x - New duration
      d - Default amplitude (1)
[blank] - Leave unchanged
"""

    noise_cf =  """Calibrate! > Noise > Specify center frequency in Hz

Options - Explanations:

  0 < x - New center frequency
      d - Default center frequency (1000)
[blank] - Leave unchanged
"""

    noise_bw =  """Calibrate! > Noise > Specify bandwidth in octaves

Options - Explanations:

  0 < x - New bandwidth
      d - Default bandwidth (.33333)
[blank] - Leave unchanged
"""

    tone = """Calibrate! > Pure Tones

Options - Explanations:

      f - Specify frequency in Hz. current value: {:} [default: 1000 Hz]
      a - Specify amplitude in v.  current value: {:} [default: 1 v]
      d - Specify duration in s.   current value: {:} [default: 10 s]
      p - Play stimulus with current parameters
      b - Back to main menu
"""

    tone_amp =  """Calibrate! > Pure Tones > Specify amplitude in v

Options - Explanations:

 x <= 1 - New amplitude. Values <= 0 are dB atten; 0 < x <= 1 are linear scaling values 
      d - Default amplitude (1)
[blank] - Leave unchanged
"""

    tone_dur =  """Calibrate! > Pure Tones > Specify duration in seconds

Options - Explanations:

  0 < x - New duration
      d - Default amplitude (1)
[blank] - Leave unchanged
"""

    tone_f =  """Calibrate! > Pure Tones > Specify frequency in Hz

Options - Explanations:

  0 < x - New frequency
      d - Default frequency (1000)
[blank] - Leave unchanged
"""

    dev_id =  """Calibrate! > Device Options > Specify Device ID

Options - Explanations:

 0 <= x - New portaudio device id
      d - Default device id (0)
[blank] - Leave unchanged
"""

    dev_n =  """Calibrate! > Device Options > Specify Output number of channels

Options - Explanations:

  0 < x - New number of channels
      d - Default number of channels (2)
[blank] - Leave unchanged
"""

    dev_ch =  """Calibrate! > Device Options > Specify Output channel number

Options - Explanations:

  0 < x - New output channel #
      d - Default output channel # (1)
[blank] - Leave unchanged
"""

    dev_fs =  """Calibrate! > Device Options > Specify Device sampling frequency

Options - Explanations:

  0 < x - New sampling frequency
      d - Default sampling frequency (44100)
[blank] - Leave unchanged
"""

def is_number(s):
    """ Returns True if string is a number. """
    try:
        np.float32(s)
        return True
    except ValueError:
        return False

class default_tone:
    f = 1000.
    dur = 10.
    amp = 1.
    fs = 44100.

class default_noise:
    dur = 10.
    rms = .18
    amp = 0.
    fs = 44100.
    cf = 1000.
    bw = .3333
    lp = 22050.
    hp = 0.

class default_device:
    fs = 44100.
    id = 0
    n = 2
    ch = 1

def process_noise(menus, dev, noise):

    need_params = True
    status = "Noise menu selected"

    while need_params:
        this_menu = menus.noise.format(noise.cf, noise.bw, noise.rms, noise.amp, noise.dur)
        pad = menu_max_size - this_menu.count("\n")
        print ("\n"*12 + this_menu + "\n"*pad)
        print("Status: {}\n".format(status))
        ret = raw_input("Choose an option: ")

        if ret == "c":
            this_menu = menus.noise_cf
            pad = menu_max_size - this_menu.count("\n") + 2 # +2 when there is no status line
            print ("\n"*12 + this_menu + "\n"*pad)
            new_cf = raw_input("Enter value: ")
            if is_number(new_cf):
                new_cf_f = np.float32(new_cf)
                if new_cf_f > 0:
                    noise.cf = new_cf_f
                    status = "Center frequency changed: {:}".format(new_cf_f)
            elif new_cf == "d":
                noise.cf = default_noise.cf
                status = "Center frequency set to default: {:}".format(default_noise.cf)
            elif new_cf == "":
                status = "Center frequency unchanged: {:}".format(noise.cf)
            else:
                status = "Center frequency unchanged: {:}; Unrecognized  input: {}".format(noise.cf, new_cf)

        if ret == "w":
            this_menu = menus.noise_bw
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_bw = raw_input("Enter value: ")
            if is_number(new_bw):
                new_bw_f = np.float32(new_bw)
                if new_bw_f > 0:
                    noise.bw = new_bw_f
                    status = "Bandwidth changed: {:}".format(new_bw_f)
            elif new_bw == "d":
                noise.bw = default_noise.bw
                status = "Bandwidth set to default: {:}".format(default_noise.bw)
            elif new_bw == "":
                status = "Bandwidth unchanged: {:}".format(noise.bw)
            else:
                status = "Bandwidth unchanged: {:}; Unrecognized  input: {}".format(noise.bw, new_bw)

        elif ret == "a":

            this_menu = menus.noise_amp
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_amp = raw_input("Enter value: ")
            if is_number(new_amp):
                new_amp_f = np.float32(new_amp)
                if new_amp_f <= 1:
                    noise.amp = new_amp_f
                    status = "Amplitude changed: {:}".format(new_amp_f)
            elif new_amp == "d":
                noise.amp = default_noise.amp
                status = "Amplitude set to default: {:}".format(default_noise.amp)
            elif new_amp == "":
                status = "Amplitude unchanged: {:}".format(noise.amp)
            else:
                status = "Amplitude unchanged: {:}; Unrecognized  input: {}".format(noise.amp, new_amp)

        elif ret == "r":

            this_menu = menus.noise_rms
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_rms = raw_input("Enter value: ")
            if is_number(new_rms):
                new_rms_f = np.float32(new_rms)
                if new_rms_f <= 1:
                    noise.rms = new_rms_f
                    status = "RMS changed: {:}".format(new_rms_f)
            elif new_rms == "d":
                noise.rms = default_noise.rms
                status = "RMS set to default: {:}".format(default_noise.rms)
            elif new_rms == "":
                status = "RMS unchanged: {:}".format(noise.rms)
            else:
                status = "RMS unchanged: {:}; Unrecognized  input: {}".format(noise.rms, new_rms)

        elif ret == "d":
            this_menu = menus.noise_dur
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_dur = raw_input("Enter value: ")
            if is_number(new_dur):
                new_dur_f = np.float32(new_dur)
                if 0 <= new_dur_f:
                    noise.dur = new_dur_f
                    status = "Duration changed: {:}".format(new_dur_f)
            elif new_dur == "d":
                noise.dur = default_noise.dur
                status = "Duration set to default: {:}".format(default_noise.dur)
            elif new_dur == "":
                status = "Duration unchanged: {:}".format(noise.dur)
            else:
                status = "Duration unchanged: {:}; Unrecognized  input: {}".format(noise.dur, new_dur)

        elif ret == "p":
            print ("Playing noise with cf={:}; bw={:}; amp={:}; dur={:}".format(noise.cf, noise.bw, noise.amp, noise.dur))
            signal = np.random.randn(np.int32(noise.dur*noise.fs))
            signal = signal * (noise.rms / psylab.signal.rms(signal))
            signal = psylab.signal.atten(signal, noise.amp)
            bw = noise.bw / 2.
            fc = psylab.signal.oct2f(noise.cf, bw)
            hp = fc[0]
            lp = fc[1]
            bh,ah = psylab.signal.filters.butter(6, hp/(noise.fs/2.), btype='high')
            signal = psylab.signal.lfilter(bh, ah, signal)
            bl,al = psylab.signal.filters.butter(6, lp/(noise.fs/2.))
            signal = psylab.signal.lfilter(bl, al, signal)
            signal = psylab.signal.ramps(signal, noise.fs)
            d = m.open_device(int(dev.id), int(dev.id), int(dev.n))
            s = d.open_array(signal, int(dev.fs))
            mm = s.mix_mat
            mm[:] = 0
            mm[int(dev.ch)-1] = 1
            s.mix_mat = mm
            s.play()
            while s.is_playing:
                time.sleep(.1)

            status = "Played noise"

        elif ret == "b":
            status = ""
            need_params = False

    return noise, status


def process_tone(menus, dev, tone):

    need_params = True
    status = "Tone menu selected"

    while need_params:
        this_menu = menus.tone.format(tone.f, tone.amp, tone.dur)
        pad = menu_max_size - this_menu.count("\n")
        print ("\n"*12 + this_menu + "\n"*pad)
        print("Status: {}\n".format(status))
        ret = raw_input("Choose an option: ")

        if ret == "a":
            this_menu = menus.tone_amp
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_amp = raw_input("Enter value: ")
            if is_number(new_amp):
                new_amp_f = np.float32(new_amp)
                if new_amp_f <= 1:
                    tone.amp = new_amp_f
                    status = "Amplitude changed: {:}".format(new_amp_f)
            elif new_amp == "d":
                tone.amp = default_tone.amp
                status = "Amplitude set to default: {:}".format(default_tone.amp)
            elif new_amp == "":
                status = "Amplitude unchanged: {:}".format(tone.amp)
            else:
                status = "Amplitude unchanged: {:}; Unrecognized  input: {}".format(tone.amp, new_amp)

        elif ret == "d":
            this_menu = menus.tone_dur
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_dur = raw_input("Enter value: ")
            if is_number(new_dur):
                new_dur_f = np.float32(new_dur)
                if 0 <= new_dur_f:
                    tone.dur = new_dur_f
                    status = "Duration changed: {:}".format(new_dur_f)
            elif new_dur == "d":
                tone.dur = default_tone.dur
                status = "Duration set to default: {:}".format(default_tone.dur)
            elif new_dur == "":
                status = "Duration unchanged: {:}".format(tone.dur)
            else:
                status = "Duration unchanged: {:}; Unrecognized  input: {}".format(tone.dur, new_dur)

        elif ret == "f":
            this_menu = menus.tone_f
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_f = raw_input("Enter value: ")
            if is_number(new_f):
                new_f_f = np.float32(new_f)
                if 0 < new_f_f:
                    tone.f = new_f_f
                    status = "Frequency changed: {:}".format(new_f_f)
            elif new_f == "d":
                tone.f = default_tone.f
                status = "Frequency set to default: {:}".format(default_tone.f)
            elif new_f == "":
                status = "Frequency unchanged: {:}".format(tone.f)
            else:
                status = "Frequency unchanged: {:}; Unrecognized input: {}".format(tone.f, new_f)

        elif ret == "p":
            print ("Playing pure tone with f={:}; amp={:}; dur={:}".format(tone.f, tone.amp, tone.dur))
            signal = psylab.signal.tone(tone.f, tone.fs, tone.dur*1000., amp=tone.amp)
            signal = psylab.signal.ramps(signal, tone.fs)
            print ("Device id: {}".format(dev.id))
            d = m.open_device(int(dev.id), int(dev.id), int(dev.n))
            s = d.open_array(signal, int(dev.fs))
            mm = s.mix_mat
            mm[:] = 0
            mm[int(dev.ch)-1] = 1
            s.mix_mat = mm
            s.play()
            while s.is_playing:
                time.sleep(.1)

            status = "Played tone"

        elif ret == "b":
            status = ""
            need_params = False

    return tone, status


def process_device(menus, dev):

    need_params = True
    status = "Device menu selected"

    while need_params:
        this_menu = menus.device.format(dev.id, dev.fs, dev.n, dev.ch)
        pad = menu_max_size - this_menu.count("\n")
        print ("\n"*12 + this_menu + "\n"*pad)
        print("Status: {}\n".format(status))
        ret = raw_input("Choose an option: ")
        if ret == "i":
            this_menu = menus.dev_id
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_id = raw_input("Enter value: ")
            if is_number(new_id):
                new_id_i = np.float32(new_id)
                if new_id_i > 0:
                    dev.id = new_id_i
                    status = "Device ID changed: {:}".format(new_id_i)
            elif new_id == "d":
                dev.id = default_dev.id
                status = "Device ID set to default: {:}".format(default_dev.id)
            elif new_id == "":
                status = "Device ID unchanged: {:}".format(dev.id)
            else:
                status = "Device ID unchanged: {:}; Unrecognized  input: {}".format(dev.id, new_id)

        elif ret == "n":
            this_menu = menus.dev_n
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_n = raw_input("Enter value: ")
            if is_number(new_n):
                new_n_f = np.float32(new_n)
                if new_n_f > 0:
                    dev.n = new_n_f
                    status = "Device # channels changed: {:}".format(new_ch_f)
            elif new_n == "d":
                dev.n = default_dev.n
                status = "Device # channels set to default: {:}".format(default_dev.n)
            elif new_n == "":
                status = "Device # channels unchanged: {:}".format(dev.n)
            else:
                status = "Device # channels unchanged: {:}; Unrecognized  input: {}".format(dev.n, new_n)

        elif ret == "c":
            this_menu = menus.dev_ch
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_ch = raw_input("Enter value: ")
            if is_number(new_ch):
                new_ch_f = np.float32(new_ch)
                if new_ch_f > 0:
                    dev.ch = int(new_ch_f)
                    status = "Device output channel changed: {:}".format(new_ch_f)
            elif new_ch == "d":
                dev.ch = default_dev.ch
                status = "Device output channel set to default: {:}".format(default_dev.ch)
            elif new_ch == "":
                status = "Device output channel unchanged: {:}".format(dev.ch)
            else:
                status = "Device channels unchanged: {:}; Unrecognized  input: {}".format(dev.ch, new_ch)

        elif ret == "f":
            this_menu = menus.dev_fs
            pad = menu_max_size - this_menu.count("\n") + 2
            print ("\n"*12 + this_menu + "\n"*pad)
            new_fs = raw_input("Enter value: ")
            if is_number(new_fs):
                new_fs_f = np.float32(new_fs)
                if new_fs_f > 0:
                    dev.fs = new_fs_f
                    status = "Device sampling frequency changed: {:}".format(new_fs_f)
            elif new_fs == "d":
                dev.fs = default_dev.fs
                status = "Device sampling frequency set to default: {:}".format(default_dev.fs)
            elif new_fs == "":
                status = "Device sampling frequency unchanged: {:}".format(dev.fs)
            else:
                status = "Device sampling frequency unchanged: {:}; Unrecognized  input: {}".format(dev.fs, new_fs)

        elif ret == "b":
            status = ""
            need_params = False


    return dev, status


if __name__ == '__main__':

    need_params = True
    status = ""

    tone = default_tone()
    noise = default_noise()
    dev = default_device()

    while need_params:
        this_menu = menus.main
        pad = menu_max_size - this_menu.count("\n")
        print ("\n"*12 + this_menu + "\n"*pad)
        print("Status: {}\n".format(status))
        ret = raw_input("Choose an option: ")

        if ret == "t":

            tone, status = process_tone(menus, dev, tone)

        elif ret == "n":

            noise, status = process_noise(menus, dev, noise)

        elif ret == "d":

            dev, status = process_device(menus, dev)

        elif ret == "q":
            print("\nQuitter detected...\n")
            need_params = False
