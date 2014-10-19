import numpy
import math
from matplotlib.pylab import *
import PRBS

class LBPilot:
	def __init__(self):
		self.pilot = []
		
	def fromFile( self, fn ):
		with open( fn,'rt') as f:
			for s in f:
				self.pilot.append(complex(s))
			f.close()
	

if __name__=='__main__':
	aP = LBPilot()
	aP.fromFile('d:/works/lb/rightFrame0pilot.txt')
	ang = [ math.atan2(x.imag,x.real) for x in aP.pilot ]
	for i in range(len(ang)):
		ang[i]=(math.pi+ang[i])%math.pi
	phase = -sum(ang)/len(ang)
	for i in range(len(aP.pilot)):
		aP.pilot[i] *= complex( math.cos(phase), math.sin(phase) )
	pp = []
	for x in aP.pilot:
		if x.real>0.:
			pp.append(1)
		else:
			pp.append(-1)
			
	aB = PRBS.PRBS([1 for i in range(11)])
	aM = []
	for i in range(4096):
		aM.append(1-2*aB.ce())
	aX = []
	for i in range(4096-len(pp)):
		sum = 0
		for j in range(len(pp)):
			sum += pp[j]*aM[j+i]
		aX.append(sum)
		
	