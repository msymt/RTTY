import wave
import numpy as np
import baudot

"""
smp/45.45
=1秒のサンプル数/45.45
=1bitあたりのサンプル数
=サンプル数/bit

176個/bit　の0と1の数を比較して，0/1 を決めるが，
値の境界は安定しない（ノイズ云々）ため，
大体176個の内，25%(44個，経験則)を超えたあたりから，0と1の数を集計し，比較．
実際は，25%超えたあたりから，大体0/1続きのため，26%~30%あたりでわかる（らしい．要検証）ため，
残りのサンプル（120個くらい）は無視しても大丈夫（要検証）
"""
fname='./rtty3s.wav' # should be specify the filename.
smp= 8000          # Sampling Rate
baud_rate = 45.45   # rtty baud rate
num_of_one_bit_smp = 8000 / baud_rate # number of 1bit sampling, 176
stable_smp_start = num_of_one_bit_smp * 0.2 # 20%
FQm= smp/914.0     # Mark Frequency 914Hz
FQs= smp/1086.0    # Space Frequency 1086Hz
wind= 32           # windows size Integer()
waveFile = wave.open(fname, 'r')

# m: mark, s: space
mq=[]
mi=[]
sq=[]
si=[]

baudot_result = []
num_of_smp = []
result = []

for j in range(waveFile.getnframes()):
	buf = waveFile.readframes(1) # bytes object
	# print(buf[0], ",", buf[0]-128)
	# 8bit 符号なし(0 - 255)　→ 符号あり(-127 - 128)にしたい
	mq.append((buf[0]-128)*np.sin(np.pi*2.0/FQm*j)) # 914のsin, 実部
	mi.append((buf[0]-128)*np.cos(np.pi*2.0/FQm*j)) # 914のcos，虚部
	sq.append((buf[0]-128)*np.sin(np.pi*2.0/FQs*j)) # 実部
	si.append((buf[0]-128)*np.cos(np.pi*2.0/FQs*j)) # 虚部
	# 内積
	mk = np.sqrt(sum(mq)**2 + sum(mi)**2)
	sp = np.sqrt(sum(sq)**2 + sum(si)**2)
	# markがspaceより大きいか否か
	num_of_smp.append(int(mk>sp)) # 電波強度比較して，0か1かを決める
	if len(num_of_smp) >= stable_smp_start:
		# int -> str, 最初と最後以外の中5bit
		data = ''.join(map(str,baudot_result[1:len(baudot_result) - 1]))
		# print(data)
		# LTRSテーブルを見て変換
		itr = baudot.LTRS.get(data)
		if itr != None:
			result.append(itr)
		# 変換結果のうち，特殊文字があれば変換
		# baudot配列をクリア
		baudot_result.clear()
	# if len(num_of_smp >= num_of_one_bit_smp):
	# 	num_of_smp = [] # clear
	# windサイズを超えたものばかり
	if j>wind:
		mq.pop(0)
		mi.pop(0)
		sq.pop(0)
		si.pop(0)
waveFile.close()
print(result)