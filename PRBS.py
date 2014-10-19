class PRBS:
	def __init__( self, init ):
		self.state = []
		for x in init:
			self.state.append(x)
		
	def ce( self ):
		new = self.state[8]^self.state[10]
		self.state.insert(0,new)
		self.state.pop
		return new
		
if __name__=='__main__':
	aM = PRBS([ 1 for i in range(11) ])
	test = []
	for i in range(2048):
		test.append( (1-2*aM.ce()) )
	