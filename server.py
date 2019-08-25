#! -*- coding: utf-8 -*-

"""
  [server]
    python3 server.py --help
"""

#---------------------------------
# モジュールのインポート
#---------------------------------

import argparse
import time
import cv2
import numpy as np
import socket


#---------------------------------
# 定数定義
#---------------------------------

# --- カメラ画像のサイズ ---
CAMERA_IMG_SHAPE = (200, 320, 3)
CAMERA_DATA_SIZE = np.prod(CAMERA_IMG_SHAPE)

#---------------------------------
# 関数
#---------------------------------

"""
  関数名: ArgParser
  説明：引数を解析して値を取得する
"""
def ArgParser():
	parser = argparse.ArgumentParser(description='Socket通信でクライアントから画像を受け取り，Canny法でエッジ検出した画像を返すサーバ', \
		formatter_class=argparse.RawTextHelpFormatter)

	# --- 引数を追加 ---
	parser.add_argument('--server_ip', dest='server_ip', type=str, help='サーバのIPアドレス', required=True)
	parser.add_argument('--server_port', dest='server_port', type=int, help='Socket通信で利用するサーバのポート', required=True)

	args = parser.parse_args()

	return args

#---------------------------------
# メイン処理
#---------------------------------
if __name__ == '__main__':
	# --- 引数処理 ---
	args = ArgParser()

	# --- Socket通信 ---
	#   * AF_INET : IPv4
	#   * SOCK_STREAM : TCP/IP
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((args.server_ip, args.server_port))
		s.listen(1)
		
		while (True):
			# --- クライアントからの接続を検出 ---
			conn, addr = s.accept()
			
			# --- データ受信 ---
			#   バイトデータで受信されるのでndarrayに変換する
			data = None
			while (True):
				data_tmp = conn.recv(CAMERA_DATA_SIZE)
				if (data is not None):
					data = np.hstack((data, np.fromstring(data_tmp, dtype=np.uint8)))
				else:
					data = np.fromstring(data_tmp, dtype=np.uint8)
				
				if (len(data) >= CAMERA_DATA_SIZE):
					break
				else:
#					print(len(data))	# for Debug
					time.sleep(0.001)	# wait 1ms
			
			# --- 受信したデータを(Height, Width, Channel)にReshape ---
#			print(data)			# for Debug
#			print(data.shape)	# for Debug
			data = data.reshape(CAMERA_IMG_SHAPE)
#			cv2.imwrite('frame.png', data)	# for Debug
			
			# --- エッジ検出 ---
			edges = cv2.Canny(data, 100, 200)
#			print(edges.shape)				# for Debug
#			cv2.imwrite('edges.png', edges)	# for Debug
			
			# --- エッジ検出した画像を送信 ---
			conn.send(edges.tostring())
			
			break


