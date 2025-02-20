# Demodulation Radio Teletype (RTTY) in Python
This is a Python program to demodulate the radio teletype known as FSK modulation.
This is the simplest example, and only the Terminal Unit part of the RTTY is implemented. The rest should be coded according to ITA2, for example.

### Convert ogg file to wave format

Install [ffmpeg](https://www.ffmpeg.org/) and run:

~~~
ffmpeg -i RTTY.ogg -ar 8k -c:a pcm_u8 -f wav rtty3s.wav
~~~

- -ar: sampling rate
- -c:a(or -acodec)
  - c:codec
  - a:audio 
- pcm_u8: 8bit

ref: http://www.xucker.jpn.org/pc/ffmpeg_wav.html

## USAGE

```Python
python3 ./src/rtty8k.py
```

## Description of the source code

~~~
import wave
import numpy as np
fname='rtty3s.wav' # should be specify the filename.
smp= 8000          # Sampling Rate
FQm= smp/914.0     # Mark Frequency 914Hz
FQs= smp/1086.0    # Space Frequency 1086Hz
wind= 32           # windows size Integer
waveFile = wave.open(fname, 'r')

mq=[];mi=[];sq=[];si=[]
for j in range(waveFile.getnframes()):
      buf = waveFile.readframes(1)
      mq.append((buf[0]-128)*np.sin(np.pi*2.0/FQm*j))
      mi.append((buf[0]-128)*np.cos(np.pi*2.0/FQm*j))
      sq.append((buf[0]-128)*np.sin(np.pi*2.0/FQs*j))
      si.append((buf[0]-128)*np.cos(np.pi*2.0/FQs*j))
      mk = np.sqrt(sum(mq)**2 + sum(mi)**2)
      sp = np.sqrt(sum(sq)**2 + sum(si)**2)     
      print(mk,sp,int(mk>sp),sep=",")
      if j>wind:
            mq.pop(0);mi.pop(0);sq.pop(0);si.pop(0)
waveFile.close()
~~~
## Sample sound file
should be convet to wave format.<p>
The input audio file should have a sampling rate of 8000 Hz and a quantization bit rate of 8 bits.<p>
https://en.wikipedia.org/wiki/File:RTTY.ogg <p>
it is from wikipedia<p>
      
## Parameters
Some parameters in the source code need to be modified according to the audio file to be input. 
~~~
fname='rtty3s.wav' # should be specify the filename.
smp= 8000          # Sampling Rate
FQm= smp/914.0     # Mark Frequency 914Hz
FQs= smp/1086.0    # Space Frequency 1086Hz
~~~
- fname   
should be specify the filename.
- smp   
Sampling Rate.
- FQm     
smp / Mark Frequency 
- FQs   
smp / Space Frequency 

## How to specify the MARK & SPACE frequency
To find MARK & SPACE frequences, You can use any spectrum analyze tools on your PC. For example I use Sazanami Version 1.7.3 2020/10/22
. 

- MARK Frequency about 915Hz    
![](img/space.png)
- SPACE Frequency is about 1085Hz   
![](img/mark.png)


## Usage
Please specify an appropriate audio file for the input.
This program assumes 8KHz sampling, mono, 8bit quantization, and no sign.
~~~
python rtty8k.py > rtty.csv
~~~
Demodulation example
![](img/2021-02-01.png)
