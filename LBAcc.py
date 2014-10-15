import numpy
import math
from matplotlib.pylab import *

class LBAcc:
	def __init__(self):
		self.acc = []
		self.conv = []
		self.freqs = []
		
	def fromFile( self, fn ):
		with open( fn,'rt') as f:
			for s in f:
				self.acc.append(complex(s))
			f.close()
	
	def convert(self):
		self.conv = self.acc[:200000]
		j=1.
		for i in range(len(self.conv)):
			self.conv[i] = self.conv[i]*j
			j = j*-1.
		gf = numpy.fft.fft(self.conv)
		cgf = gf[(200000-112500)/2:(200000+112500)/2]
		self.conv = numpy.fft.ifft(cgf)
		j=1.
		for i in range(len(self.conv)):
			self.conv[i] = self.conv[i]*j
			j = j*-1.

	def freqErr(self):
		gf = numpy.fft.fft(self.acc)
		for i in range(len(gf)):
			a = gf[i]*gf[i].conjugate()
			gf[i] = a
		rg = numpy.fft.ifft(gf)
		p = rg[1820]
		p = math.atan2(p.imag,p.real)/1820.
		return p
		
	def removeFreq(self,phase):
		delta = complex(math.cos(phase),math.sin(phase))    		
		k = complex(-1.,1.)
		for i in range(len(self.acc)):
			self.acc[i] = self.acc[i]*k
			k = k * delta
	
	def buildFreq(self):
		for i in range(1024):
			f = []
			self.freqs.append(f)
		for i in range(87):
			frame = self.conv[i*1280+128:i*1280+128+1024]
			ff = numpy.fft.fft(frame)
			for j in range(len(ff)):
				self.freqs[j].append(ff[j])
	
	def plotFreq(self,k):
		aX = [ x.real for x in self.freqs[k] ]
		aY = [ x.imag for x in self.freqs[k] ]
		plot(aX)
		plot(aY)
		show()
if __name__=='__main__':
	aAcc = LBAcc()
	aAcc.fromFile('d:/works/lb/leftacc.txt')
	phase = aAcc.freqErr()
	print phase
	aAcc.removeFreq(0.-phase)
	phase = aAcc.freqErr()
	print phase
	aAcc.convert()
	aAcc.buildFreq()
		