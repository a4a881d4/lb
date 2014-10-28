import wave
import LBframe0
f = wave.open('d:/works/lb/nullleft.wav',"rb")
params = f.getparams()  
nchannels, sampwidth, framerate, nframes = params[:4]
frame = f.readframes(nframes)
f.close()
		
frame0 = LBframe0.LBframe0( frame, nframes )
