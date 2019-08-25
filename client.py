#! -*- coding: utf-8 -*-

"""
  [client]
    python3 client.py --help
"""

#---------------------------------
# モジュールのインポート
#---------------------------------
import sys
import time
import argparse
import socket

import numpy as np
import cv2

#---------------------------------
# 定数定義
#---------------------------------

#---------------------------------
# 関数
#---------------------------------

"""
  関数名: ArgParser
  説明：引数を解析して値を取得する
"""
def ArgParser():
	parser = argparse.ArgumentParser(description='Socket通信でサーバへ画像を送信し，Canny法でエッジ検出した画像を受信するクライアント', \
					formatter_class=argparse.RawTextHelpFormatter)
	
	# --- 引数を追加 ---
	parser.add_argument('--server_ip', dest='server_ip', type=str, help='接続先のサーバのIPアドレス', required=True)
	parser.add_argument('--server_port', dest='server_port', type=int, help='接続先のサーバのPort番号', required=True)
	parser.add_argument('--dbg_camera_monitor', dest='dbg_camera_monitor', action='store_true', help='', required=False)
	
	args = parser.parse_args()
	
	return args

#---------------------------------
# メイン処理
#---------------------------------
if __name__ == '__main__':
	# --- 引数処理 ---
	args = ArgParser()

	# --- カメラから映像をキャプチャ ---
	cap = cv2.VideoCapture(0)
#	cv2.waitKey(1) & 0xFF
#	cv2.imwrite('frame.png', frame)

	if (args.dbg_camera_monitor):
		while (1):
			ret, frame = cap.read()
			cv2.imshow('camera', frame)

			key = cv2.waitKey(1) & 0xFF
			if (key == ord('q')):
				cap.release()
				cv2.destroyAllWindows()
				quit()
	else:
		ret, frame = cap.read()
	
#	print(frame.shape)
#	print(np.prod(frame.shape))
	
	# --- サーバへ接続 ---
	#   * AF_INET : IPv4
	#   * SOCK_STREAM : TCP/IP
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((args.server_ip, args.server_port))
	
		# --- サーバへ画像を送信 ---
		s.send(frame.tostring())
	
		# --- エッジ検出画像を受信 ---
		#   バイトデータで受信するので，ndarrayへ変換
		#   エッジ画像はグレースケールで帰ってくるので，バッファサイズはframe.shape[0] * frame.shape[1]
		data = None
		edge_img_hw = frame.shape[0:2]
		edge_img_data_size = np.prod(edge_img_hw)
		while (True):
			data_tmp = s.recv(edge_img_data_size)
			if (data is not None):
				data = np.hstack((data, np.fromstring(data_tmp, dtype=np.uint8)))
			else:
				data = np.fromstring(data_tmp, dtype=np.uint8)

			if (len(data) >= edge_img_data_size):
				break
			else:
				time.sleep(0.001)	# 1ms wait

#		print(data.shape)	# for Debug
		cv2.imwrite('frame.png', data.reshape(edge_img_hw))
	
	cap.release()
	cv2.destroyAllWindows()

