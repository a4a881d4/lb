import LBfile

aLB = LBfile.LBfile('e:/works/lb/left.wav')
block = 2
f = open('e:/works/lb/leftBlk2.txt','wt')
start = aLB.frame.frames[block][0]
length = len(aLB.frame.frames[block])*(1820+455)
frame = aLB.frame.z[start:start+length]
strAcc = [ str(x) for x in frame ]
for s in strAcc:
	f.write(s)
	f.write('\n')
f.close()
	