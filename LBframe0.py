from LBframe import *
import wave
import numpy
import math

class LBframe0(LBframe):
	def __init__(self,inF,length):
		LBframe.__init__(self,inF,length,1,0)
		self.xc = [[0. for f in self.frames] for g in self.frames]
			
	def xcorr( self ):
		for line in range(len(self.frames)):
			self.xc[line][line] = 1.
			posx = self.frames[line][self.startBlock]
			A = self.z[posx:posx+self.frameLen]
			Apower = self._mypower(A)
			for i in range( line+1, len(self.frames) ):
				pos = self.frames[i][self.startBlock]
				posO, peak, a = self.findMatch(A,pos)
				peak = math.sqrt(peak/(Apower*self.fpowers[i]))
				print i," ",pos,"match:",posO," ",peak," ",a
				self.xc[line][i] = peak*256.
				self.xc[i][line] = peak*256.
	
	def rebuildFrame( self, A, h ):
		hA = math.sqrt(self._mypower(h))
		h = [ x.conjugate()/hA for x in h ]
		B = [ complex(0.,0.) for x in A ]
		B[0:23] = h[22:]
		B[-22:] = h[0:22]
		BF = numpy.fft.fft(B)
		AF = numpy.fft.fft(A)
		CF = [ complex(0.,0.) for i in range(len(AF)) ]
		for i in range(961):
			CF[i]=AF[i]/BF[i]
		for i in range(2265-961,2265):
			CF[i]=AF[i]/BF[i]
		C = numpy.fft.ifft(CF)
		return CF
		 
	def combine( self, li ):
		Apower = self._mypower(self.acc)
		nacc = [ complex(0.,0.) for x in self.acc ]
		for i in range( 0, len(li) ):
			pos = self.frames[li[i]][self.startBlock]
			Bpower = self._mypower(self.z[pos:pos+self.frameLen])
			posO,peak,a,dat = self.findMatch( self.acc, pos )
			print pos," match:",posO," ",math.sqrt(peak/Apower/Bpower)," ",dat
			a = self._normal(a)
			nacc = [ nacc[i] + self.z[posO+i]*a for i in range(self.frameLen) ]
		self.acc = [ x/len(li) for x in nacc ]
		return self.acc
		
	def combine2( self, li ):
		Apower = self._mypower(self.acc)
		FA = numpy.fft.fft(self.acc)
		r = []
		nacc = [ complex(0.,0.) for x in self.acc ]
		for i in range( 0, len(li) ):
			pos = self.frames[li[i]][self.startBlock]
			B = self.z[pos:pos+self.frameLen]
			FB = numpy.fft.fft(B)
			FC = [ FA[i]*FB[i].conjugate() for i in range(len(FA)) ]
			C = numpy.fft.ifft(FC)
			for i in range(16,len(C)-16):
				C[i] = complex(0.,0.)
			FC = numpy.fft.fft(C)
			FAA = [ FB[i]*FC[i] for i in range(len(FA)) ]
			A = numpy.fft.ifft(FAA)
			a = self._xcorrAB( self.acc, A )
			print a
			nacc = [ nacc[i] + A[i] for i in range(self.frameLen) ]

		self.acc = [ x/len(li) for x in nacc ]
		return self.acc	
	
	def resetAcc(self,k):
		posx = self.frames[k][self.startBlock]
		self.acc = self.z[posx:posx+self.frameLen]
		
	def freqErr(self):
		gf = numpy.fft.fft(self.acc)
		for i in range(len(gf)):
			a = gf[i]*gf[i].conjugate()
			gf[i] = a
		rg = numpy.fft.ifft(gf)
		p = rg[1820]
		p = math.atan2(p.imag,p.real)/1820.
		self.power = rg[0].real
		return p
		
	def removeFreq(self,phase):
		delta = complex(math.cos(phase),math.sin(phase))    		
		k = complex(-1.,1.)
		for i in range(len(self.acc)):
			self.acc[i] = self.acc[i]*k
			k = k * delta			 		 
	
	def timing( self, gf, phase ):
		j=complex(1.,0.)
		det = complex( math.cos(phase), math.sin(phase) )
		zgf = []
		for i in range(len(gf)):
			zgf.append(gf[i]*j)
			j = j*det
	
		dgf = []
		dgp = []
		for i in range( 77, 941 ):
			if (i+3)%9 != 0:
				dgf.append(zgf[i])
			if (i+12)%18 == 0:
				dgp.append(zgf[i])	
		gfx = [ x.real for x in dgf ]
		gfy = [ x.imag for x in dgf ]
		return dgf,gfx,gfy,dgp
				
if __name__ == '__main__':

	f = wave.open('d:/works/lb/right.wav',"rb")
	params = f.getparams()  
	nchannels, sampwidth, framerate, nframes = params[:4]
	frame = f.readframes(nframes)
	f.close()
		
	frame0 = LBframe0( frame, nframes )
	frame0.resetAcc(37)	
	aFrame = frame0.combine(range(37,73))
	aFrame = frame0.combine(range(37,73))
	aFrame = frame0.combine(range(37,73))
	phase = frame0.freqErr()
	print phase
	frame0.removeFreq(0.-phase)
	phase = frame0.freqErr()
	print phase
	aFrame = frame0.acc[:1820+454]
	
	j=1.
	for i in range(len(aFrame)):
		aFrame[i] = aFrame[i]*j
		j = j*-1.
	gf = numpy.fft.fft(aFrame)
	start = (len(aFrame)-1280)/2
	cgf = gf[start:start+1280]
	aFrame = numpy.fft.ifft(cgf)
	
	bFrame = aFrame[128:128+1024]
	gf = numpy.fft.fft(bFrame)
	dgf,gfx,gfy,dgp = frame0.timing(gf,469.*math.pi/2048.)
	
	with open('d:/works/lb/rightFrame0pilot.txt','wt') as fp:
		for x in dgp:
			print >>fp,x
		fp.close()
		 	
	