class ploy:
	def __init__( self ):
		self.state = []
		self.l = 0
		
	def setA( self, s ):
		self.state = []
		for x in s:
			if x>0:
				self.state.append(0)
			else:
				self.state.append(1)
		self.l = len(s)
		self.set( self.state )
	
	def setB( self, s ):
		self.state = []
		for x in s:
			if x>0:
				self.state.append(1)
			else:
				self.state.append(0)
		self.l = len(s)
		self.set( self.state )
	
	def set( self, s ):
		i=0
		for i in range(len(s)-1,-1,-1):
			if s[i]!=0:
				break
		self.l = i+1
		self.state = [ x for x in s[:self.l] ]
	
	def noA( self ):
		self.state = [ x^1 for x in self.state ]
		self.set( self.state )
	
	def mul( self, b ):
		r = ploy()
		r.l = self.l+b.l-1
		r.state = [ 0 for i in range(r.l) ]
		for i in range(self.l):
			if self.state[i]==1:
				for j in range(b.l):
					r.state[i+j] ^= b.state[j]
		r.set( r.state )
		return r
			
	def div( self, b ):
		if self.l<b.l:
			C = ploy()
			C.set( [ 0 ] )
			D = ploy()
			D.set( self.state )
			return C,D
			
		dl = self.l - b.l+1
		s = [ x for x in self.state ]
		r = []
		for i in range( dl ):
			if s[ self.l-1-i ]==1:
				for j in range(b.l):
					s[self.l-b.l-i+j] ^= b.state[j]
				r.insert(0,1)
			else:
				r.insert(0,0)
		res = ploy()
		res.set(s)
		d = ploy()
		d.set(r)
		return d,res
		
	def printOut( self ):
		for x in self.state:
			print x,
		print self.l
		
	def zero(self):
		if self.state[0]==0 and self.l<=1:
			return 1
		else:
			return 0
	
	def xn(self,k):
		for i in range(k):
			self.state.insert(0,0)
		self.set( self.state )
		
	def setK(self,k):
		self.state = []
		while( k!=0 ):
			self.state.append(k&1)
			k>>=1
		self.set( self.state )
		
	def count( self ):
		s = []
		c = 1
		f = self.state[0]
		for x in self.state[1:]:
			if x^f==0:
				c+=1
			else:
				s.append(c)
				c=1
			f = x
		s.append(c)
		return max(s)
							
if __name__=='__main__':
	A = [ 1 for i in range(13) ]
	B = [ 1, 1]
	aP = ploy()
	aP.set(A)
	bP = ploy()
	bP.set(B)
	print aP.l,bP.l
	aP.printOut()
	bP.printOut()
	
	C,D = aP.div(bP)
	C.printOut()
	D.printOut()
	print C.l,D.l
	
	
			 
		