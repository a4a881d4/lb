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
			1516,1687,1340,627,213,1248,238, 238,238,238,238,238,238,238 ]
			
		self.rightPilotInit = [
			1685,1688,1860,1866,382,656,1492,1104,1263,746,984,1687,632,627,1951,1340,
			476,213,1866,844,930,933,191,328,746,1576,631,1397,1516,1867,1340,1337,
			1492,1104,1326,306,1254,1263,632,627,427,1248,1688,1951,1866,844,656,794,
			1104,930,746,1576,1687,153,627,631,1340,1337,213,1648,844,975,933,422,
			449,984,1854,632,1688,1951,1588,476,1860,1866,1104,930,306,191,1263,746,
			627,631,1248,1516,1951,1340,844, 238,238,238,238,238,238,238 ]
		self.offLeft = [ 13, 4, 10, 1, 7, 16 ]
		self.offRight = [ 4, 13, 1, 10, 16, 7 ]
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
		self.conv = self.acc[0:]
		j=1.
		for i in range(len(self.conv)):
			self.conv[i] = self.conv[i]*j
			j = j*-1.
		lengthin = len(self.conv)
		lengthout = int(lengthin*45./20.+0.5)+4
		print lengthin,lengthout
		gf = numpy.fft.fft(self.conv)
		cgf = [ complex(0,0) for i in range(lengthout) ]
		cgf[(lengthout-lengthin)/2:(lengthout-lengthin)/2+lengthin] = gf
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
			ret.append( self._xcorrAB( self.conv[pos:pos+len], self.conv[pos+4096:pos+4096+len] ))
		return ret
		
	def xcorrShiftZ11( self, pos ):
		return self.xcorrShift( [ x for x in range(pos-40,pos+41) ], 1024 )
	
	def findMatch( self, pos ):
		aX = self.xcorrShiftZ11( pos )
		x = []
		for a in aX:
			x.append((a*a.conjugate()).real)
		peak = max(x)
		posMax = x.index(peak)
		pos = pos-40+posMax
		return pos
		
	def rebuildStart( self ):
		self.sPos = [ -23 ]
		for i in range(1,94):
			ss = self.sPos[i-1]+4096+1024
			#if i<93:
			# pos = self.findMatch(ss)
			#print pos," match ",ss,pos-ss
			self.sPos.append(ss)
	
	def buildFreq(self,left):
		if left==1:
			offset = 2048. #-4*16
		else:
			offset = 2048. #-4*16
		for i in range(4096):
			f = []
			self.freqs.append(f)
		k0 = complex(1,0)
		for i in range(94):
			start = self.sPos[i]
			frame = self.conv[start+512:start+512+4096]
			ff = numpy.fft.fft(frame)
			ff = self.timing( ff, offset*math.pi/8192. ) #1927
			for j in range(len(ff)):
				self.freqs[j].append(ff[j]*k0)
			#k0 = k0*complex(0,-1)
			
	"""
	def getPilot(self,left):
		if left==1:
			off = self.offLeft
		else:
			off = self.offRight
		self.blockPilots = [[] for i in range( len( self.freqs[0] ) )]
		self.blockAngs = [[] for i in range( len( self.freqs[0] ) )]
		self.v = [[] for i in range( len( self.freqs[0] ) )]
		
		for i in range(len(self.freqs[0])):
			zk = (i-2) % 6
			for j in range( 77, 941 ):
				if (j-off[zk]-512+18*30)%18 == 0:
					self.blockPilots[i].append(self.freqs[j][i])
					self.blockAngs[i].append(math.atan2(self.freqs[j][i].imag,self.freqs[j][i].real))
				elif (j-off[zk]-512+18*30)%9 != 0:
					self.v[i].append( self.freqs[j][i] )	
	"""
	def retiming2(self,p,k):
		ph = self.estTiming(p)
		print ph
		ph = -ph/9.
		ff = [ self.freqs[j][k] for j in range(4096) ]
		ff = self.timing( ff, ph ) 
		for j in range(len(ff)):
			self.freqs[j][k]=ff[j]
		ff = [ self.freqs[j][k+1] for j in range(4096) ]
		ff = self.timing( ff, ph ) 
		for j in range(len(ff)):
			self.freqs[j][k+1]=ff[j]
	
	def get2Pilot(self,left):
		if left==1:
			off = self.offLeft
			k = complex(1,-1)
		else:
			off = self.offRight
			k = complex(1,1)
		pilot2 = [[] for i in range( len( self.freqs[0] )/2 )]
		Mseq0 = PRBS.PRBS()
		Mseq1 = PRBS.PRBS()
		for i in range(0,len(self.freqs[0]),2):
			if left ==1:
				Mseq0.setK(self.leftPilotInit[i])
				Mseq1.setK(self.leftPilotInit[i+1])
			else:
				Mseq0.setK(self.rightPilotInit[i])
				Mseq1.setK(self.rightPilotInit[i+1])
			zk = (i-2) % 6
			
			for j in range( 77+1536, 941+1536 ):
				if (j-off[zk]-2048+18*30)%18 == 0:
					r = (1 - 2*Mseq0.ce())*k
					pilot2[i/2].append(self.freqs[j][i]*r)
				elif (j-off[zk]-2048+18*30)%18 == 9:
					r = (1 - 2*Mseq1.ce())*k*complex(0,1)
					pilot2[i/2].append( self.freqs[j][i+1]*r )
				
		return pilot2
		
		
	def getDual(self):
		self.leftPilots = self.get2Pilot(1)
		self.rightPilots = self.get2Pilot(0)
		self.v = [[] for i in range( len( self.freqs[0] ) )]
		self.u = [[] for i in range( len( self.freqs[0] ) )]
		for i in range(len(self.freqs[0])):
			zk = (i-2) % 6
			for j in range( 77+1536, 941+1536 ):
				if (j-self.offLeft[zk]-2048+18*30)%9 != 0:
					self.v[i].append( self.freqs[j][i] )
				self.u[i].append(self.freqs[j][i])	
		self.estDual()
		
	def estDual(self):
		size = len( self.leftPilots[0] )
		self.leftChannel = []
		self.rightChannel = []
		for i in range(len(self.leftPilots)):
			self.leftChannel.append(sum( self.leftPilots[i] )/size)
			self.rightChannel.append(sum( self.rightPilots[i] )/size)
		
	def STBCCombine(self,k):
		r = []
		for i in range(len(self.v[k])):
			y1 = self.v[k][i]
			y2 = self.v[k+1][i]
			y2 = y2.conjugate()
			u1 = y1*self.rightChannel[k/2].conjugate() + y2 * self.leftChannel[k/2]
			u2 = -y1*self.leftChannel[k/2].conjugate() + y2 * self.rightChannel[k/2]
			s = self.rightChannel[k/2]*self.rightChannel[k/2].conjugate() + self.leftChannel[k/2]*self.leftChannel[k/2].conjugate()
			r.append(u1/s)
			r.append(u2.conjugate()/s)
		return r
			
	def removePilot( self, left ):
		if left==1:
			init = self.leftPilotInit
		else:
			init = self.rightPilotInit
		aMseq = PRBS.PRBS()
		for i in range(len(self.blockPilots)):
			aMseq.setK(init[i])
			if i%2 == 0:
				k = complex(1,0)
			else:
				k = complex(0,-1)
			for j in range(len(self.blockPilots[i])):
				if aMseq.ce()==1:
					self.blockPilots[i][j] *= -1*k
				else:
					self.blockPilots[i][j] *= k
					
	def retiming(self):
		bTimingE = []
		for p in self.blockPilots:
			ph = self.estTiming(p)
			print ph
			bTimingE.append(-ph/18.)
		for i in range(len(bTimingE)):
			ff = [ self.freqs[j][i] for j in range(4096) ]
			ff = self.timing( ff, bTimingE[i] ) #1927
			for j in range(len(ff)):
				self.freqs[j][i]=ff[j]
			
	def estTiming(self,pilot):
		dd = [ pilot[i]*pilot[i-1].conjugate() for i in range(1,len(pilot)) ]
		s = sum( dd )
		phase = math.atan(s.imag/s.real)
		return phase			
	
	def timing( self, gf, phase ):
		j=complex(1.,0.)
		det = complex( math.cos(phase), math.sin(phase) )
		zgf = []
		for i in range(len(gf)):
			zgf.append(gf[i]*j)
			j = j*det
		return zgf
		
	def estRot( self, pilot ):
		dd = sum( pilot )
		rot = dd / math.sqrt( (dd*dd.conjugate()).real )
		return dd.conjugate()
		
	def removeRot( self, gf, a ):
		return [ x*a for x in gf ]
		
	def rot( self ):
		self.v = []
		for i in range(len(self.blockPilots)):
			a = self.estRot( self.blockPilots[i] )
			ff = [ self.freqs[j][i] for j in range(4096) ]
			for j in range(len(ff)):
				self.freqs[j][i]=ff[j]*a
			#self.v.append( [ ff[j]*a for j in range(1024) ] )
			
	def rots( self, seq, ang ):
		ang *= math.pi/180.
		a = math.tan(ang)
		r = [ complex(x.real+a*x.imag,x.imag) for x in seq ]
		return r
		
	def _judge( self, seq ):
		r = []
		for x in seq:
			if x>0.:
				r.append(1)
			else:
				r.append(-1)
		return r
		
	def cjudge( self, seq ):
		si = [ x.real for x in seq ]
		sq = [ x.imag for x in seq ]
		return self._judge(si), self._judge(sq)
		
		
					

if __name__=='__main__':
	left = 1
	path = 'g:/works/lb/'
	fin = path + 'dualBlk3.txt'
	aBlk = LBBlock()
	aBlk.fromFile(fin)
	aBlk.buildFreq(left)
	"""
	aBlk.getPilot(left)
	aBlk.removePilot(left)
	aBlk.retiming()
	"""
	p = aBlk.get2Pilot(left)
	
	for i in range(len(p)):
		aBlk.retiming2(p[i],2*i)
	
	"""
	aBlk.removePilot(left)
	aBlk.rot()
	aBlk.retiming()
	aBlk.getPilot(left)
	aBlk.removePilot(left)
	"""
	aBlk.getDual()
	
	import LBAcc
	aAcc = LBAcc.LBAcc()
	"""
	v0 = aBlk.rots(aBlk.v[0],47)
	l0,r0 = aBlk.cjudge(v0)
	
	v1 = aBlk.rots(aBlk.v[1],47)
	l1,r1 = aBlk.cjudge(v1)
	
	lr = [ (l0[i],r0[i],l1[i],r1[i]) for i in range(len(l0)) ]
	"""
	m = aBlk.STBCCombine(0)
	"""
	rr = {}
	for i in range(len(m)):
		k = i/2
		if m[i].imag<0.2 and m[i].imag>-0.2:
			print i,
			print aBlk.v[0][k],aBlk.v[1][k],(l0[k],r0[k],l1[k],r1[k])
			if lr[k] in rr:
				rr[lr[k]] += 1
			else:
				rr[lr[k]] = 1
		else:
			print "error ",i,
			print aBlk.v[0][k],aBlk.v[1][k],(l0[k],r0[k],l1[k],r1[k]),m[i]
			if lr[k] in rr:
				rr[lr[k]] -= 1
			else:
				rr[lr[k]] = -1
	"""
	
	buf = aBlk.acc
	gf = []
	for i in range(94):
		gf.append(numpy.fft.fft(buf[i*(1820+455):(i+1)*(1820+455)]))
	for i in range(0,94,2):
		
	gf = numpy.fft.fft(aBlk.acc[:200000])
	gf = [ x*x.conjugate() for x in gf ]
	cgf = numpy.fft.ifft(gf)
	aAcc.plotK(cgf)
	