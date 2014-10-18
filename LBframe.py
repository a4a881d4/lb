import struct
import math

class LBframe:
	def __init__(self,inF,length):
		self.z = []
		for i in range(length):
			c = struct.unpack_from( '2h', inF, i*4 )
			self.z.append(complex(c[0],c[1]))
		self.powers = []
		for i in range(len(self.z)/256-1):
			self.powers.append( self._power( self.z[i*256:(i+1)*256] ))
		self.avgPower = sum(self.powers)/len(self.powers)
		self.frames = []
		
		self.frames = []
		f = []
		f1,peak = self.findFrame(0)
		f.append(f1)
		while 1:
			f2,peak = self.checkFrame( f1+1820+455 )
			if f2-f1>(1820*2):
				self.frames.append(f)
				f = [ f2 ]
				print "find ",f2, "frame\n"
				f1 = f2
			elif f2==-1:
				self.frames.append(f)
				break
			else:
				f.append(f2)
				f1 = f2
		
		for frame in self.frames:
			if len(frame)!=94:
				self.frames.remove( frame )
		self.frameLen = 1*(1820+455)		
		self.acc = self.z[self.frames[0][0]:(self.frames[0][0]+self.frameLen)]
		self.accp = self._mypower(self.acc)
		self.fpowers = [ 0. for f in self.frames ]
		self.framePower()
		self.matchPos = []
		self.match()
		self._buildAcc()
		
	def _power( self, d ):
		p = 0
		for a in d:
			p = p + a*a.conjugate()
		return p.real
	
	def _xcorr( self, src, pos0, pos1, len ):
		A = src[pos0:pos0+len]
		B = src[pos1:pos1+len]
		return self._xcorrAB(A,B)
	
	def _xcorrAB( self, A, B ):
		sums = complex(0.,0.)
		for j in range(len(A)):
			sums = sums + A[j]*B[j].conjugate()
		return sums
	
	def xcorrZ( self, pos ):
		return self._xcorr( self.z, pos, pos+1820, 445 )
	
	def xcorrShift( self, A, B, posRange ):
		ret = []
		for pos in posRange:
			ret.append( self._xcorrAB( A, B[pos:(pos+len(A))]) )
		return ret
		
	def xcorrShiftZ45( self, A, pos ):
		return self.xcorrShift( A, self.z, [ x for x in range(pos-22,pos+23) ] )
	
	def findMatch( self, A, pos ):
		aX = self.xcorrShiftZ45( A, pos )
		x = []
		for a in aX:
			x.append((a*a.conjugate()).real)
		peak = max(x)
		posMax = x.index(peak)
		pos = pos-22+posMax
		return pos,peak,aX[posMax]
			
	def findFrame( self, start ):
		# find power
		pos256 = start/256+1
		while self.powers[pos256]<self.avgPower/2.:
			pos256 = pos256 + 1
			if pos256>=len(self.powers):
				return -1,0.
		# scan from (pos256-1)*256
		pos256 = pos256-1
		x = []
		for i in range(0,1820+445+256,16):
			a = self.xcorrZ(i+pos256*256)
			x.append((a*a.conjugate()).real)
		pos16 = x.index(max(x))-2
		x = []
		for i in range( 0,pos16*16+64 ):
			a = self.xcorrZ(i+pos256*256+pos16*16)
			x.append((a*a.conjugate()).real)
		peak = max(x)
		pos = x.index(peak) + pos256*256+pos16*16
		return pos,peak 
	
	def checkFrame( self, start ):
		pos256 = (start+1820+455)/256+1
		if pos256>=len(self.powers):
			return -1,0.
		if self.powers[pos256]<self.avgPower/2.:
			return self.findFrame(start)
		start = start-5
		x = []
		for i in range( start,start+9 ):
			a = self.xcorrZ(i)
			x.append((a*a.conjugate()).real)
		peak = max(x)
		pos = x.index(peak) + start
		return pos,peak	
	
	def match( self ):
		self.matchPos = []
		for i in range(len(self.frames)):
			pos = self.frames[i][0]
			posO, peak, a = self.findMatch(self.acc,pos)
			print pos,"match:",posO," ",peak/(self.accp*self.fpowers[i])," ",a
			self.matchPos.append((posO,self._normal(a),peak))
			
	
	def _normal( self, x ):
		return x/math.sqrt((x*x.conjugate()).real)
	
	def _buildAcc( self ):
		sum = 0.
		for ( start,a,p ) in self.matchPos:
			sum = sum + p
		length = self.frameLen
		self.acc = [ complex(0.,0.) for i in range(length) ]
		for (start,a,p) in self.matchPos:
			for i in range(length):
				self.acc[i] = self.acc[i] + self.z[start+i]*a*math.sqrt(p/sum)
		self.accp = self._mypower(self.acc)

	def _mypower( self, x ):
		sum = 0.
		for a in x:
			sum = sum + (a*a.conjugate()).real
		return sum

	def framePower( self ):
		for i in range(len(self.frames)):
			pos = self.frames[i][0]
			self.fpowers[i] = self._mypower( self.z[pos:pos+len(self.acc)] )
	
