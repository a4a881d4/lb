import wave
import struct
from LBframe import *
from matplotlib.pylab import *

class LBfile:
	def __init__(self,fn):
		f = wave.open(fn,"rb")
		params = f.getparams()  
		nchannels, sampwidth, framerate, nframes = params[:4]
		frame = f.readframes(nframes)
		f.close()
		
		self.frame = LBframe( frame, nframes )		
		
		
if __name__ == '__main__':

	aLB = LBfile('d:/works/lb/left.wav')
	for i in range(10):
		aLB.frame.match()
		aLB.frame._buildAcc()
	for i in range(0,len(aLB.frame.frames)):
		pos = aLB.frame.frames[i][0]
		aX = aLB.frame.xcorrShiftZ45( aLB.frame.acc, pos )
		x = []
		for a in aX:
			x.append((a*a.conjugate()).real)
		plot( x )
		show()
   
	f = open('d:/works/lb/leftaccFrame0.txt','wt')
	strAcc = [ str(x) for x in aLB.frame.acc ]
	for s in strAcc:
		f.write(s)
		f.write('\n')
	f.close()
	