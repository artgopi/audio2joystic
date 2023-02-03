# audio2joystic
Convert audio sent by remote RC to virtual joystick.

I use this script to convert the signal sent by my remote controller that have as audio output used to simulator
The audio is available through a 3.5mm jack, that I connect to my computer using a 3.5 to 3.5 audio cable.

I just test it with my remote and with Linux.

I use it to practice in the excellent RC Quadcopter Racing Simulator - https://fpv-freerider.itch.io/fpv-freerider

Thsi code is based on the work from https://github.com/nigelsim/ppmadapter, but as been substential modified, to
 be more reliable and don't consume much CPU
 
Using an oscilloscope I check that my controller output a signal simillar to:

__    __    __    __    _____________________
  |  |  |  |  |  |  |  |
   --    --    --    --
   
 Where the top space varies when the stick are moved.
