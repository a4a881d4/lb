import LBfile

aLB = LBfile.LBfile('d:/works/lb/nulldual.wav')
block = 3
f = open('d:/works/lb/dualBlk3.txt','wt')
start = aLB.frame.frames[block][0]
length = len(aLB.frame.frames[block])*(1820+455)
frame = aLB.frame.z[start:start+length]
strAcc = [ str(x) for x in frame ]
for s in strAcc:
	f.write(s)
	f.write('\n')
f.close()
	