import numpy
import math
from matplotlib.pylab import *
import sys
import ploy
from LBBlock import *

class LBAcc(LBBlock):
	def __init__(self):
		LBBlock.__init__(self)
	
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
				#B.printOut()
				self.primes.append(B)		
											
if __name__=='__main__':
	import PRBS
	left = 1
	dual = 1
	path = 'd:/works/lb/'
	if left ==1:
		fin = path + 'left' + 'acc.txt'
		fout = path + 'left' + 'pilotInit.txt'
	else:
		fin = path + 'right' + 'acc.txt'
		fout = path + 'right' + 'pilotInit.txt'
	if dual==1:
		fin = path + 'dual' + 'acc.txt'
		if left ==1:
			fout = path + 'dualleft' + 'pilotInit.txt'
		else:
			fout = path + 'dualright' + 'pilotInit.txt'
	
	aAcc = LBAcc()
	aAcc.fromFile(fin)
	phase = aAcc.freqErr()
	print phase
	aAcc.removeFreq(0.-phase)
	phase = aAcc.freqErr()
	print phase
	aAcc.convert()
	aAcc.buildFreq(left)
	aAcc.freqPower()
	
	aAcc.getPilot(left)
	aAcc.retiming()
	aAcc.getPilot(left)
	aAcc.decP()
	
	aAcc.toPPs()
	aAcc.prime()
	
	p = aAcc.primes[295]
	hexPI = []
	aMseq = PRBS.PRBS()
	with open(fout,'wt') as fp:
		for i in range(len(aAcc.pps)):
			pp = aAcc.pps[i]
			D = p.mul(pp)
			if D.state[30]==0:
				print >>fp,i/2,
				hp = 0
				for j in range(11):
					hp |= ( pp.state[j]<<j )
				hexPI.append(hp)
				print >>fp,hex(hp)
		for hp in hexPI:
			aMseq.setK(hp)
			e = []
			for i in range(48):
				e.append( 1-2*aMseq.ce() )
			print >>fp,hexPI.index(hp),
			aAcc.count(e,fp)
		fp.close()
	
	
				
	