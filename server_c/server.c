/**
 * @file server.c
 * @brief クライアントから画像を受信してエッジ画像を送信するサンプルコード
 */

#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/** @def ARG_NUM
 * 変数の数
 *  - argv[0] : プログラム名
 *  - argv[1] : サーバのIPアドレス
 *  - argv[2] : サーバのポート番号
 */
#define ARG_NUM		(3)

/** @def CAMERA_DATA_SIZE
 * カメラ画像のデータサイズ
 */
#define CAMERA_DATA_SIZE	(200 * 320 * 3)

/**
 * @fn unsigned long int convert_ipaddr_v4_to_ul(char* ipaddr)
 * @brief 文字列で指定されたIPアドレスをunsigned long int型へ変換する
 * @param[in] IPアドレス
 * @return IPアドレス
 */
unsigned long int convert_ipaddr_v4_to_ul(char* ipaddr)
{
	unsigned long int ret = 0;
	unsigned long int val = 0;

	if (ipaddr == NULL) {
		return 0;
	}

	while (*ipaddr) {
		val = 0;
		while ((*ipaddr != '.') && (*ipaddr)) {
			val = val * 10 + ((*ipaddr++) - '0');
		}

		ret = (ret << 8) | (val & 0xFF);

		if (*ipaddr == '.') {
			ipaddr++;
		}
	}

	return ret;
}


/**
 * @fn int main(int argc, char* argv[])
 * @brief クライアントから受信した画像をエッジ画像に変換して送信するメイン関数
 * @param[in] argc 引数の数
 * @param[in] argv 引数
 * @return なし
 */
int main(int argc, char* argv[])
{
	int server_sock;
	int client_sock;
	int recv_size;
	int send_size;
	int i;
	struct sockaddr_in server_sockaddr;
	struct sockaddr_in client_sockaddr;
	unsigned short server_port;
	unsigned long int server_ip;
	unsigned int client_len;
	char recv_buf[CAMERA_DATA_SIZE];	// カラー画像
	char send_buf[CAMERA_DATA_SIZE / 3];	// グレースケール画像

	int flg_disconnect;	// 0:connect, 1:disconnect

	if (argc < ARG_NUM) {
		fprintf(stderr, "[ERROR] Invalid arguments\n");
		exit(0);
	}

//	printf("[DEBUG] ipaddr : 0x%x\n", convert_ipaddr_v4_to_ul(argv[1]));
//	printf("[DEBUG] port : %d\n", atoi(argv[2]));

	// --- socket()にPF_INET, bind()にAF_INETを使うべきらしい ---
	//   https://qiita.com/progrunner17/items/bdc37d407514addde1f9
	//   https://stackoverflow.com/questions/6729366/what-is-the-difference-between-af-inet-and-pf-inet-in-socket-programming
	//   https://linuxjm.osdn.jp/html/LDP_man-pages/man2/socket.2.html
	if ((server_sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0) {
		fprintf(stderr, "[ERROR] Invalid port number\n");
		exit(0);
	}
	if ((server_ip = convert_ipaddr_v4_to_ul(argv[1])) == 0) {
		fprintf(stderr, "[ERROR] Invalid IP address\n");
		exit(0);
	}
	if ((server_port = (unsigned short)atoi(argv[2])) == 0) {
		fprintf(stderr, "[ERROR] Invalid port number\n");
		exit(0);
	}

	// --- bind() ---
	//   https://linuxjm.osdn.jp/html/LDP_man-pages/man2/bind.2.html
	memset(&server_sockaddr, 0, sizeof(server_sockaddr));
	server_sockaddr.sin_family = AF_INET;
	server_sockaddr.sin_addr.s_addr = htonl(server_ip);
	server_sockaddr.sin_port = htons(server_port);
	if (bind(server_sock, (struct sockaddr*)&server_sockaddr, sizeof(server_sockaddr)) < 0) {
		fprintf(stderr, "[ERROR] bind() failed\n");
		exit(0);
	}

	// --- listen() ---
	//   https://linuxjm.osdn.jp/html/LDP_man-pages/man2/listen.2.html
	if (listen(server_sock, 1) < 0) {
		fprintf(stderr, "[ERROR] listen() failed\n");
		exit(0);
	}

	client_len = sizeof(client_sockaddr);
	if ((client_sock = accept(server_sock, (struct sockaddr*)&client_sockaddr, &client_len)) < 0) {
		fprintf(stderr, "[ERROR] accept() failed\n");
		exit(0);
	}
	printf("[INFO] connected from %s\n", inet_ntoa(client_sockaddr.sin_addr));

	while (1) {
		recv_size = recv(client_sock, recv_buf, CAMERA_DATA_SIZE, MSG_WAITALL);
//		printf("[DEBUG] recv_size = %d\n", recv_size);

		if (strcmp(recv_buf, "disconnect") == 0) {
			break;
		}

		for (i = 0; i < CAMERA_DATA_SIZE/3; i++) {
			send_buf[i] = (char)((recv_buf[i] + recv_buf[i+(320*200)] + recv_buf[i+(320*200*2)]) / 3);
		}

		send_size = send(client_sock, send_buf, CAMERA_DATA_SIZE / 3, 0);
//		printf("[DEBUG] send_size = %d\n", send_size);
	}

	close(client_sock);

	return 0;
}



