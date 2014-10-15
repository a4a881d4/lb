import wave
import struct
from LBframe import *

class LBfile:
	def __init__(self,fn):
		f = wave.open(fn,"rb")
		params = f.getparams()  
		nchannels, sampwidth, framerate, nframes = params[:4]
		frame = f.readframes(nframes)
		f.close()
		
		self.frame = LBframe( frame, nframes )		
		
		
if __name__ == '__main__':

	aLB = LBfile('g:/works/lb/left.wav')
	aLB.frame.plotMatch()
	
