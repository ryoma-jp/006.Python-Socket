# 006.Python-Socket

Socket通信でクライアントから画像を受け取り，Canny法でエッジ検出した画像を返すサーバと，
Socket通信でサーバへ画像を送信し，Canny法でエッジ検出した画像を受信するクライアント

## サーバ

	python server.py --server_ip [IPアドレス] --server_port [サーバのポート]

## クライアント

	python client.py --server_ip [IPアドレス] --server_port [サーバのポート]

