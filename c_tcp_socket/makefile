.PHONY: all

all: c_tcp_client c_tcp_server

c__tcp_client: 
	gcc -o c_tcp_client c_tcp_client.c
c_tcp_server: 
	gcc -o c_tcp_server c_tcp_server.c -lpthread
clean:
	rm -f c_tcp_client c_tcp_server