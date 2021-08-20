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
ただし，そのまま取るとスタート/ストップビットと重ならないため，工夫が必要
"""
def main():
	fname='./rtty3s.wav' # should be specify the filename.
	smp= 8000          # Sampling Rate
	baud_rate = 45.45   # rtty baud rate
	num_of_one_bit_smp = int(8000 / baud_rate) # number of 1bit sampling, 176
	stable_smp_start = int(num_of_one_bit_smp * 0.25) # 25%, 44
	stable_smp_end = int(num_of_one_bit_smp * 0.3) # 30%, 52.8
	FQm= smp/914.0     # Mark Frequency 914Hz
	FQs= smp/1086.0    # Space Frequency 1086Hz
	wind= 32           # windows size Integer()
	waveFile = wave.open(fname, 'r')
	mode = "Letters" # default

	# m: mark, s: space
	mq=[]
	mi=[]
	sq=[]
	si=[]

	baudot_result = []
	whole_smp = []
	for j in range(waveFile.getnframes()):
		buf = waveFile.readframes(1) # bytes object
		# 8bit 符号なし(0 - 255)　→ 符号あり(-127 - 128)にしたい
		mq.append((buf[0]-128)*np.sin(np.pi*2.0/FQm*j)) # 914のsin, 実部
		mi.append((buf[0]-128)*np.cos(np.pi*2.0/FQm*j)) # 914のcos，虚部
		sq.append((buf[0]-128)*np.sin(np.pi*2.0/FQs*j)) # 実部
		si.append((buf[0]-128)*np.cos(np.pi*2.0/FQs*j)) # 虚部

		# 内積(高速化)
		sumq = sum(mq);sumi = sum(mi);sumsq = sum(sq);sumsi = sum(si)
		mk = np.sqrt(sumq*sumq + sumi*sumi)
		sp = np.sqrt(sumsq*sumsq + sumsi*sumsi)
		whole_smp.append(int(mk>sp))
		if j>wind:
			mq.pop(0);mi.pop(0);sq.pop(0);si.pop(0)
	waveFile.close()

	# for item in result:
	# 	print(item, end="")
	# print("")

	# whole_smp
	divide_one_bit = [] # 176個ずつに分けた
	rmv_formar_bit = [] # 前半25%を除いた
	bit_chunk = [] # 0/1の数から大小比較した結果
	start = 0
	for item in whole_smp:
		bit_buf = whole_smp[start:start+num_of_one_bit_smp:1]
		divide_one_bit.append(bit_buf)
		rmv_formar_bit.append(bit_buf[stable_smp_start:])
		start += num_of_one_bit_smp
		if start >= len(whole_smp):
			break
	divide_one_bit = divide_one_bit[:-1] # 最後の端は削除

	for item in rmv_formar_bit:
		zero_one = decide_bit_zero_or_one(item)
		bit_chunk.append(zero_one)
	# print(bit_chunk)
	data_bit_chunk = gen_bit_chunk(bit_chunk)
	# print(data_bit_chunk)
	baudot_result = []
	mode = "Letters"
	for item in data_bit_chunk:
		decode_result = decode_rtty(item, mode)
		# print(decode_result)
		if decode_result is None: # [Figures] or [Letters]
			pass
		else:
			baudot_result.append(decode_result)
	for item in baudot_result:
		print(item, end="")
	print("")


def gen_bit_chunk(bit_buf, start_bit='0', stop_bit='1'):
	start_bit_index = None
	bit_index = 0 #5個分かぞえるためのindex
	bit_chunk = [] # data bit(5bit)
	result = []
	for index in range(len(bit_buf)):
		if start_bit_index is None:
			if bit_buf[index] == start_bit:
				start_bit_index = index
		else:
			if bit_index < 5:
				bit_chunk.append(bit_buf[index])
				bit_index += 1
			else:
				if bit_buf[index] == stop_bit:
					result.append(bit_chunk)
					start_bit_index = None
					bit_index = 0
					bit_chunk = []
	return result


def decide_bit_zero_or_one(bit_buf):
	zero_num = bit_buf.count(0)
	one_num = bit_buf.count(1)
	if zero_num > one_num:
		return "0"
	else:
		return "1"


# baudt conversion
def decode_rtty(data, mode):
	data = ''.join(map(str,data))
	if mode == "[Figures]":
		itr = decode_FIGS(data)
	else:
		itr = decode_LTRS(data)
	if itr == "[Figures]" or itr == "[Letters]":
		mode = itr
		return
	return itr

def decode_LTRS(data):
	return baudot.LTRS.get(data)

def decode_FIGS(data):
	return baudot.FIGS.get(data)

if __name__ == "__main__":
	main()
