import wave
import numpy as np
import baudot

"""
smp/45.45
=1秒のサンプル数/45.45
=1bitあたりのサンプル数
=サンプル数/bit

最初のノイズを捨てて，マーク→スペースになった瞬間から取得
1bitあたりのサンプルのうち，25%を超えたあたりで安定(経験則)するため，
そこを抽出し，bitのチャンクを生成
LTRS/FIGSの変換テーブルと照合し，decode
"""

def main():
	fname='./rtty3s.wav' # should be specify the filename.
	smp= 8000          # Sampling Rate
	baud_rate = 45.45   # rtty baud rate
	num_of_one_bit_smp = int(8000 / baud_rate) # number of 1bit sampling, 176
	stable_smp_start = int(num_of_one_bit_smp * 0.25) # 25%, 44
	FQm= smp/914.0     # Mark Frequency 914Hz
	FQs= smp/1086.0    # Space Frequency 1086Hz
	wind= 32           # windows size Integer()
	waveFile = wave.open(fname, 'r')

	# m: mark, s: space
	mq=[]
	mi=[]
	sq=[]
	si=[]

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

	# 最初の1 -> 0(mark -> space)に変わったとこを探す
	mark_to_space_index = find_mark_to_space_index(whole_smp)
	remove_first_noize_smp = whole_smp[mark_to_space_index:] # 変化点以降を抽出

	divide_one_bit = [] # 176個ずつに分けたbit列を格納
	bit_chunk = [] # 0/1の数から大小比較した結果
	start = 0 # break用
	for item in remove_first_noize_smp:
		bit_buf = remove_first_noize_smp[start:start+num_of_one_bit_smp:1] # 176個ずつ
		divide_one_bit.append(bit_buf)
		start += num_of_one_bit_smp
		if start >= len(remove_first_noize_smp): # 境界
			break

	# 25%をすぎたとこの先頭ビットを抽出
	for item in divide_one_bit:
		zero_one = item[stable_smp_start] # 25%すぎたとこ
		bit_chunk.append(zero_one)

	# start:0, stop:1となる7bitを抽出し, 間の5bitを返す
	data_bit_chunk = gen_bit_chunk(bit_chunk)

	mode = "Letters" # default
	baudot_result = []
	for item in data_bit_chunk:
		decode_result = decode_rtty(item, mode)
		# mode変換時
		if decode_result == "[Figures]" or decode_result == "[Letters]":
			mode = decode_result[1:len(decode_result)-1] #[]を除く
		else:
			baudot_result.append(decode_result)


	for item in baudot_result:
		print(item, end="")
	print("")

# mark -> space(1 -> 0)に移る瞬間のindex(space側)を返す
def find_mark_to_space_index(bit_buf):
	for i in range(len(bit_buf)):
		if bit_buf[i] == 1 and bit_buf[i + 1] == 0:
			i += 1 # space index
			return i
	return None

# 5bitのチャンクを生成
def gen_bit_chunk(bit_buf, start_bit=0, stop_bit=1):
	start_bit_index = None

	bit_index = 0		# 5個分かぞえるためのindex
	bit_chunk = []	# data bit(5bit)
	result = []

	for index in range(len(bit_buf)):
		# スタートビット
		if start_bit_index is None:
			if bit_buf[index] == start_bit:
				start_bit_index = index
		else:
			# 5bit分抽出(<=だと6bit取得)
			if bit_index < 5:
				bit_chunk.append(bit_buf[index])
				bit_index += 1
			else:
				# stop bitなら格納．それ以外なら7bit分を破棄
				if bit_buf[index] == stop_bit:
					result.append(bit_chunk)
				# 初期状態
				start_bit_index = None
				bit_index = 0
				bit_chunk = []
	return result

# baudt conversion
def decode_rtty(data, mode):
	data = ''.join(map(str,data)) #結合
	# modeに合わせた変換テーブルを使う
	if mode == "Figures":
		itr = decode_FIGS(data)
	else:
		itr = decode_LTRS(data)
	return itr

def decode_LTRS(data):
	return baudot.LTRS.get(data)

def decode_FIGS(data):
	return baudot.FIGS.get(data)

if __name__ == "__main__":
	main()
