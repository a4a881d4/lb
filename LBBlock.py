import numpy
import math
import PRBS

class LBBlock:
	def __init__(self):
		self.acc = []
		self.conv = []
		self.freqs = []
		self.power = 0.
		self.freqPowers = []
		self.leftPilotInit = [
			1588,953,656,1588,1104,1860,306,382,1687,306,627,1263,1248,984,213,1248,
			844,1951,794,476,328,794,1576,930,153,191,1867,153,1337,631,1648,1516,
			306,382,1263,1492,984,1326,1248,984,1951,632,476,427,794,476,930,1866,
			191,656,153,191,631,746,1516,1687,1648,1516,975,1340,238,213,1421,238,
			632,1254,427,449,476,427,1866,1688,656,1588,191,656,746,1104,1687,306,
			1516,1687,1340,627,213,1248,238 ]


	def fromFile( self, fn ):
		with open( fn,'rt') as f:
			for s in f:
				self.acc.append(complex(s))
			f.close()
		phase = self.freqErr()
		print phase
		self.removeFreq(0.-phase)
		phase = self.freqErr()
		print phase
		self.convert()
		self.rebuildStart()
		
	def convert(self):
		self.conv = self.acc[:200000]
		j=1.
		for i in range(len(self.conv)):
			self.conv[i] = self.conv[i]*j
			j = j*-1.
		gf = numpy.fft.fft(self.conv)
		cgf = gf[(200000-112500)/2:(200000+112500)/2]
		self.conv = numpy.fft.ifft(cgf)

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
	
	def _xcorrAB( self, A, B ):
		sums = complex(0.,0.)
		for j in range(len(A)):
			sums = sums + A[j]*B[j].conjugate()
		return sums
	
	def xcorrShift( self, posRange, len ):
		ret = []
		for pos in posRange:
			ret.append( self._xcorrAB( self.conv[pos:pos+len], self.conv[pos+1024:pos+1024+len] ))
		return ret
		
	def xcorrShiftZ11( self, pos ):
		return self.xcorrShift( [ x for x in range(pos-5,pos+6) ], 256 )
	
	def findMatch( self, pos ):
		aX = self.xcorrShiftZ11( pos )
		x = []
		for a in aX:
			x.append((a*a.conjugate()).real)
		peak = max(x)
		posMax = x.index(peak)
		pos = pos-5+posMax
		return pos
		
	def rebuildStart( self ):
		self.sPos = [ 0 ]
		for i in range(1,87):
			ss = self.sPos[i-1]+1280
			pos = self.findMatch(ss)
			print pos," match ",ss
			self.sPos.append(pos)
	
	def buildFreq(self,left):
		if left==1:
			offset = 2048 #2048.-4*16
		else:
			offset = 2048.-4*16
		for i in range(1024):
			f = []
			self.freqs.append(f)
		for i in range(87):
			start = self.sPos[i]
			frame = self.conv[start+128:start+128+1024]
			ff = numpy.fft.fft(frame)
			ff = self.timing( ff, offset*math.pi/8192. ) #1927
			for j in range(len(ff)):
				self.freqs[j].append(ff[j])
	
	def getPilot(self,left):
		if left==1:
			off = [ 13, 4, 10, 1, 7, 16 ]
		else:
			off = [ 4, 13, 1, 10, 16, 7 ]
		self.blockPilots = [[] for i in range( len( self.freqs[0] ) )]
		self.blockAngs = [[] for i in range( len( self.freqs[0] ) )]
		
		for i in range(len(self.freqs[0])):
			zk = (i-2) % 6
			for j in range( 77, 941 ):
				if (j-off[zk]-512+18*30)%18 == 0:
					self.blockPilots[i].append(self.freqs[j][i])
					self.blockAngs[i].append(math.atan2(self.freqs[j][i].imag,self.freqs[j][i].real))	

	def removePilot( self, left ):
		if left==1:
			init = self.leftPilotInit
		aMseq = PRBS.PRBS()
		for i in range(len(self.blockPilots)):
			aMseq.setK(init[i])
			for j in range(len(self.blockPilots[i])):
				if aMseq.ce()==1:
					self.blockPilots[i][j] *= -1.
					
	def retiming(self):
		bTimingE = []
		for p in self.blockPilots:
			ph = self.estTiming(p)
			print ph
			bTimingE.append(-ph/18.)
		for i in range(len(bTimingE)):
			ff = [ self.freqs[j][i] for j in range(1024) ]
			ff = self.timing( ff, bTimingE[i] ) #1927
			for j in range(len(ff)):
				self.freqs[j][i]=ff[j]
			
	def estTiming(self,pilot):
		p = 0.
		s = 0.
		for i in range(1,len(pilot)):
			dd = pilot[i]*pilot[i-1].conjugate()
			s = dd.imag
			p = dd.real
		phase = math.atan(s/p)
		return phase			
	
	def timing( self, gf, phase ):
		j=complex(1.,0.)
		det = complex( math.cos(phase), math.sin(phase) )
		zgf = []
		for i in range(len(gf)):
			zgf.append(gf[i]*j)
			j = j*det
		return zgf

if __name__=='__main__':
	path = 'd:/works/lb/'
	fin = path + 'leftBlk1.txt'
	aBlk = LBBlock()
	aBlk.fromFile(fin)
	aBlk.buildFreq(1)
	aBlk.getPilot(1)
	aBlk.removePilot(1)
	aBlk.retiming()
	aBlk.getPilot(1)
	aBlk.removePilot(1)
	