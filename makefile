.PHONY: all

c: c_udp_client c_udp_server

c__udp_client: 
	gcc -o c_udp_client c_udp_client.c
c_udp_server: 
	gcc -o c_udp_server c_udp_server.c -lpthread
clean:
	rm -f c_udp_client c_udp_server