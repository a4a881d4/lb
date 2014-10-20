class PRBS:
	def __init__(self):
		self.state = []
		        
	def setI( self, init ):
		self.state = []
		for x in init:
			self.state.append(x)
	
	def setK( self, k ):
		self.state = []
		for i in range(11):
			self.state.append( (k>>i)&1 )
	"""			
	def ce( self ):
		new = self.state[11]
		for i in range(11,0,-1):
		    self.state[i] = self.state[i-1]
		self.state[1] = new
		self.state[10] ^= new
		self.state[9] ^= new
		self.state[2] ^= new #1 1 0 0 0 0 0 0 1 1 0 1
		return new
	
	def ceB( self ):
		b = [10, 9, 2, 1]
		new = 0
		for i in b:
			new ^= self.state[i]
		self.state.insert(0,new)
		return self.state.pop()	
	"""	
	def ce( self ):
		b = [0, 2, 3, 10]
		new = 0
		for i in b:
			new ^= self.state[i]
		self.state.append(new)
		return self.state.pop(0)	
		
if __name__=='__main__':
	import LBAcc
	import sys
	import ploy
	
	avP = LBAcc.LBAcc()
	a = [ 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1 ]
	aP = ploy.ploy()
	aP.set( a )
	
	bM = PRBS( )
	bM.setK( 0x634 )
	testb = []
	e = []
	for i in range(48):
		r = bM.ce()
		testb.append( (1-2*r) )
		e.append(r)
	avP.count(testb,sys.stdout)
	eP = ploy.ploy()
	eP.set(e)
	fP = eP.mul(aP)
	fP.printOut()