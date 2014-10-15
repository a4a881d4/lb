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
	for i in range(10):
	    aLB.frame.match()
	    aLB.frame._buildAcc()
	   
	f = open('g:/works/lb/leftacc.txt','w')
	strAcc = [ str(x) for x in aLB.frame.acc ]
	for s in strAcc:
		f.write(s)
		f.write('\n')
	f.close()
	aLB.frame.plotMatch()
