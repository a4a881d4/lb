import wave
import struct

class LBfile:
	def __init__(self,fn):
		f = wave.open(fn,"rb")
		params = f.getparams()  
		nchannels, sampwidth, framerate, nframes = params[:4]
		self.frame = f.readframes(nframes)
		f.close()
		self.z = []
		for i in range(nframes):
			c = struct.unpack_from('2h',self.frame,i*4)
			self.z.append(complex(c[0],c[1]))
		self.powers = []
		for i in range(len(self.z)/256-1):
			self.powers.append( self._power( self.z[i*256:(i+1)*256] ))
		self.avgPower = sum(self.powers)/len(self.powers)
			
	def _power( self, d ):
		p = 0
		for a in d:
			p = p + a*a.conjugate()
		return p.real
	
	def _xcorr( self, src, pos, delay, len ):
		CP = src[pos:pos+len]
		aFrame = src[pos+delay:pos+delay+len]
		sums = complex(0.,0.)
		for j in range(len):
			sums = sums + CP[j]*aFrame[j].conjugate()
		return sums
	
	def xcorrZ( self, pos ):
		return self._xcorr( self.z, pos, 1820, 445 )
		
	def findFrame( self, start ):
		# find power
		pos256 = start/256+1
		while self.powers[pos256]<self.avgPower/2.:
			pos256 = pos256 + 1
			if pos256>=len(self.powers):
				return -1
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
		pos = x.index(max(x)) + pos256*256+pos16*16
		return pos
		
		
if __name__ == '__main__':

	aLB = LBfile('e:\works\lb\left.wav')
	f = []
	f1 = aLB.findFrame(0)
	f.append(f1)
	for i in range(1,100):
		f1 = aLB.findFrame( f1+1820 )
		f.append( f1 )
		
	
