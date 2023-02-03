#!/usr/bin/env python3
""" Convert audio sent by remote RC to virtual joystick.

I use this script to convert the signal sent by my remote controller that have as audio output used to simulator
The audio is available through a 3.5mm jack, that I connect to my computer using a 3.5 to 3.5 audio cable.

I just test it with my remote and with Linux.

I use it to practice in the excellent RC Quadcopter Racing Simulator - https://fpv-freerider.itch.io/fpv-freerider

Thsi code is based on the work from https://github.com/nigelsim/ppmadapter, but as been substential modified, to be more reliable and don't consume much CPU
"""

import cv2
import pyaudio
import wave
import numpy as np
from evdev import UInput, ecodes

channel=[0,0,0,0,0,0,0]

# Define virtual joystick
mapping = {0: ecodes.ABS_X,
           1: ecodes.ABS_Y,
           2: ecodes.ABS_Z,
           3: ecodes.ABS_THROTTLE}
events = [(v, (0, 0, 255, 5, 0)) for v in mapping.values()]
j=UInput(name='audio2joystick',
           events={ ecodes.EV_ABS: events,
                    ecodes.EV_KEY: {288: 'BTN_JOYSTICK'}
                    })


chunk = 2048      # Each chunk will consist of 2048 audio samples
sample_format = pyaudio.paInt16      # 16 bits per sample
channels = 1      # Number of audio channels
fs = 44100        # Record at 44100 samples per second
 
last_sample=0
positiveSample=0
negativeSample=0
channelIndex=0

NegativeSamples=18   # Then number os consecutive negative sample (18 in my case)
EndSignal=300   # The minimum number os consecutive samples to considere that all channels were processes and new set is expected
NumberOfChannels=4   # The number os channels from the remote
amplification=4   # Amplification value

portAudio = pyaudio.PyAudio()  # Create an interface to PortAudio
 
#Open a Stream with the values we just defined
stream = portAudio.open(format=sample_format,
                channels = channels,
                rate = fs,
                frames_per_buffer = chunk,
                input = True)

# Try to guess the number os channels
channels=0
chooseChanel=[0,0,0,0,0,0,0]
channelIndex=0
chooseNegativeSamples=[]

for loop in range(20):
    data = np.array(wave.struct.unpack("%dh" % chunk, stream.read(chunk))) * np.blackman(chunk)
    for sample in data:
        if (sample>0):
            if (last_sample>0):
                positiveSample+=1
            else:
                if negativeSample>5:
                    channelIndex+=1
                negativeSample=0
        else:
            if (last_sample<0):
                negativeSample+=1
            else:
                if (positiveSample>EndSignal):
                   try:
                       chooseChanel[channelIndex]+=1
                   except:
                       channelIndex=0
                   channelIndex=0
                positiveSample=0
        last_sample=sample
NumberOfChannels=chooseChanel.index(np.max(chooseChanel))-1
print("Number of channels=",NumberOfChannels)

# Try to gess the number os samples for intersignal negative value

for loop in range(100):
    data = np.array(wave.struct.unpack("%dh" % chunk, stream.read(chunk))) * np.blackman(chunk)
    for sample in data:
        if (sample>0):
            if (last_sample>0):
                positiveSample+=1
            else:
                if negativeSample>3:
                    chooseNegativeSamples.append(negativeSample)
                negativeSample=0
        else:
            if (last_sample<0):
                negativeSample+=1
            else:
                if (positiveSample>300 and channelIndex==NumberOfChannels+1):
                    channelIndex=0
                positiveSample=0
        last_sample=sample
NegativeSamples=max(set(chooseNegativeSamples), key = chooseNegativeSamples.count)
print("NegativeSamples=",NegativeSamples)

 
while True:
    # Read chunk from audio
    data = np.array(wave.struct.unpack("%dh" % chunk, stream.read(chunk))) * np.blackman(chunk)
    for sample in data:
        if (sample>0):
            if (last_sample>0):
                positiveSample+=1   # number of consecutive positive samples
            else:
                if (negativeSample==NegativeSamples):   # Only accept data is the negative sample match the expected value
                    channelIndex+=1
                else:
                    channelIndex=0
                negativeSample=0
        else:
            if (last_sample<0):
                negativeSample+=1
            else:
                if (positiveSample>EndSignal and channelIndex==NumberOfChannels+1):   # Only write to virtual joystck if EndSignal was reached and the number of channels was reached (+1 because is end signal)
                    for n1 in range(0,4):
                        j.write(ecodes.EV_ABS, mapping[n1], channel[n1+1])
                        j.syn()
                    channelIndex=0
                try:
                    channel[channelIndex]=positiveSample*amplification
                except:
                    channelIndex=0
                positiveSample=0
        last_sample=sample

# Stop and close the Stream and PyAudio
stream.stop_stream()
stream.close()
portAudio.terminate()
 
