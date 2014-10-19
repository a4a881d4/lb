import numpy
import math
from matplotlib.pylab import *
import sys
import ploy

class LBAcc:
	def __init__(self):
		self.acc = []
		self.conv = []
		self.freqs = []
		self.power = 0.
		self.freqPowers = []

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
	
	def buildFreq(self):
		for i in range(1024):
			f = []
			self.freqs.append(f)
		for i in range(87):
			frame = self.conv[i*1280+128:i*1280+128+1024]
			ff = numpy.fft.fft(frame)
			ff = self.timing( ff, 1927.*math.pi/8192. ) #1927
			for j in range(len(ff)):
				self.freqs[j].append(ff[j])
	
	def freqPower(self):
		for i in range(1024):
			f = []
			for x in self.freqs[i]:
				f.append((x*x.conjugate()).real)
			self.freqPowers.append(f)
			
	def plotFreq(self,k):
		aX = [ x.real for x in self.freqs[k] ]
		aY = [ x.imag for x in self.freqs[k] ]
		figure(1)
		plot(aX)
		plot(aY)
		figure(2)
		plot(aX,aY)
	def plotK(self,k):
		aX = [ x.real for x in k ]
		aY = [ x.imag for x in k ]
		figure(1)
		plot(aX)
		plot(aY)
		figure(2)
		plot(aX,aY)
		
	def getPilot(self,left):
		if left==1:
			off = [ 13, 4, 10, 1, 7, 16 ]
		else:
			off = [ 13, 4, 1, 10, 16, 7 ]
		self.blockPilots = [[] for i in range( len( self.freqs[0] ) )]
		self.blockAngs = [[] for i in range( len( self.freqs[0] ) )]
		
		for i in range(len(self.freqs[0])):
			zk = (i-2) % 6
			for j in range( 77, 941 ):
				if (j-off[zk]-512+18*30)%18 == 0:
					self.blockPilots[i].append(self.freqs[j][i])
					self.blockAngs[i].append(math.atan2(self.freqs[j][i].imag,self.freqs[j][i].real))	
	
	def decP(self):
		self.pilots = []
		for pp in self.blockPilots:
			pilot = [1]
			c = 1
			for i in range(1,len(pp)):
				d = pp[i]*pp[i-1].conjugate()
				if d.real < 0:
					c *= -1
				pilot.append(c)
			self.pilots.append(pilot)
			
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
		lp = pilot[:-1]
		p = 0.
		s = 0.
		for i in range(1,len(pilot)):
			dd = pilot[i]*pilot[i-1].conjugate()
			s += dd.imag*dd.real
			p += dd.real*dd.real
		p /= 2.
		phase = math.asin(s/p)
		return phase/2			
	def timing( self, gf, phase ):
		j=complex(1.,0.)
		det = complex( math.cos(phase), math.sin(phase) )
		zgf = []
		for i in range(len(gf)):
			zgf.append(gf[i]*j)
			j = j*det
		return zgf
	
	def count(self,p,fp):
		c = 1
		f = p[0]
		if f>0:
			print >>fp,'+',
		else:
			print >>fp,'-',
		for x in p[1:]:
			if x==f:
				c+=1
			else:
				print >>fp,c,
				if x>0:
					print >>fp,'+',
				else:
					print >>fp,'-',
				c = 1
			f = x
		print >>fp,c
		
	def checkM(self,p,k,m):
		l = len(p)-m
		for i in range(l):
			print p[i]*p[i+k]*p[i+m],
		print 'e'
			
	def xorM(self,a,b):
		x = [ a[i]*b[i] for i in range(len(a)) ]
		self.count(x,sys.stdout)
	
	def findM( self, a, m ):
		l = len(a)-m
		b = [ a[i]*a[i+m] for i in range(l) ]
		self.count(b,sys.stdout)
	    	
	def toPPs( self ):
		self.pps = []
		for p in self.pilots:
			pp = ploy.ploy()
			pp.setA(p)
			self.pps.append(pp)
			pp = ploy.ploy()
			pp.setB(p)
			self.pps.append(pp)
			
	def divM( self, k, n ):		
			return self.rdiv(pps[k],pps[n])
			
	def rdiv( self, A1, B1 ):
		if A1.l>B1.l:
			A = A1
			B = B1
		else:
			A = B1
			B = A1
			
		C,D = A.div(B)
	
		while( D.zero()==0 ):
			A = B
			B = D
			C,D = A.div(B)
		
		return C,D	
		
	def div2048(self,A):
		for i in range(65536):
			p = ploy.ploy()
			p.setK(i)
			p.xn(48)
			C,D = p.div(A)
			if D.zero()==1:
				C.printOut()
	
	def prime(self):
		self.primes = []
		A = ploy.ploy()
		A.set( [ 0,1 ] )
		self.primes.append(A)
		for j in range(3,4096):
			B = ploy.ploy()
			B.setK(j)
			isP = 1
			for p in self.primes:
				if p.l==B.l:
					continue
				C,D = B.div(p)
				if D.zero()==1:
					isP=0
					break
			if isP==1:
				B.printOut()
				self.primes.append(B)		
											
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
	aAcc.freqPower()
	aAcc.getPilot(1)
	aAcc.retiming()
	aAcc.getPilot(1)
	aAcc.decP()
	with open('d:/works/lb/leftpilot.txt','wt') as fp:
		for p in aAcc.pilots:
			print >>fp,aAcc.pilots.index(p),
			aAcc.count(p,fp)
		fp.close()
	
	aAcc.toPPs()
	
	aAcc.prime()
	p = aAcc.primes[295]
	
	for pp in aAcc.pps:
		D = p.mul(pp)
		D.printOut()
				
	