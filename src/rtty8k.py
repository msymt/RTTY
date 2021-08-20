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
def main():
	fname='./rtty3s.wav' # should be specify the filename.
	smp= 8000          # Sampling Rate
	baud_rate = 45.45   # rtty baud rate
	num_of_one_bit_smp = 8000 / baud_rate # number of 1bit sampling, 176
	stable_smp_start = num_of_one_bit_smp * 0.2 # 20%, 44
	stable_smp_end = num_of_one_bit_smp * 0.3 # 30%, 52.8
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
	formar_noise_buf = []
	result = []
	decode_count = 1
	count = 0
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
		# markがspaceより大きいか否か/ 電波強度比較して，0か1かを決める
		formar_noise_buf.append(int(mk>sp))

		# 最初の20%までは別のbufferに保存し，それ以上の時に保存
		# if len(formar_noise_buf) >= stable_smp_start and num_of_one_bit_smp > len(formar_noise_buf):
		if len(formar_noise_buf) >= stable_smp_start:
			num_of_smp.append(int(mk>sp))

		# # 20%を超えた後のbufに30％まで入った場合
		# if num_of_smp >= stable_smp_start:
		if len(num_of_smp) >= (num_of_one_bit_smp - stable_smp_start): # 20% ~ one bit
			buf = num_of_smp[0:(stable_smp_end - stable_smp_start)]
			zero_num = buf.count(0)
			one_num = buf.count(1)
			# print(zero_num, one_num)
			# print(count);count += 1
			# if not(zero_num == 0 or one_num == 0):
			# 	pass
			# elif zero_num >= one_num:
			if zero_num >= one_num:
				baudot_result.append(0)
			else:
				baudot_result.append(1)
			# print(len(num_of_smp))
			# print(len(formar_noise_buf))
			# print(len((num_of_one_bit_smp - stable_smp_start)))
			num_of_smp.clear()
			formar_noise_buf.clear()

		# 0/1bitを7個格納したとき
		if len(baudot_result) >= 7:
			decode_result = decode(baudot_result)
			result.append(decode_result)
			baudot_result.clear()
			decode_count += 1

		# if j >= decode_count * num_of_one_bit_smp:
		# 	if len(num_of_smp) >= stable_smp_start:
		# 		zero_num = num_of_smp.count(0)
		# 		one_num = num_of_smp.count(1)
		# 		if zero_num >= one_num:
		# 			baudot_result.append(0)
		# 		else:
		# 			baudot_result.append(1)
		# 		num_of_smp.clear()

		# 	if len(baudot_result) >= 7:
		# 		decode_result = decode(baudot_result)
		# 		result.append(decode_result)
		# 		baudot_result.clear()
		# 	decode_count += 1

		if j>wind:
			mq.pop(0)
			mi.pop(0)
			sq.pop(0)
			si.pop(0)
	waveFile.close()
	# print(result)
	for item in result:
		if (item == None):
			pass
		elif item[1:len(item)-1] == "Space":
			print(" ", end="")
		else:
			print(item, end="")
	print("")

# baudt conversion
def decode(baudot_buf):
	data = ''.join(map(str,baudot_buf[1:len(baudot_buf) - 1])) # 開始と終了含めた7bit -> 5bit -> str
	itr = baudot.LTRS.get(data) # conversion table
	if itr != None:
		return itr
	return None


if __name__ == "__main__":
	main()