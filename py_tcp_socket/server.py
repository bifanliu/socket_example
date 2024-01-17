#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import threading

HOST = '0.0.0.0'
PORT = 7000

def job(conn):
    while True:
        # receive client data
        indata = conn.recv(1024)

        # decode
        indata_decode = indata.decode()

        # if input data content doesn't exit then keep loop
        if indata_decode.lower() == "exit":
            break

        # print write back client content
        upperstring = indata_decode.upper()
        print("Server Message is " + upperstring)

        # write back to client
        conn.send(upperstring.encode("utf-8"))
    
    # close conn
    conn.close()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

print('server start at: %s:%s' % (HOST, PORT))
print('wait for connection...')

while True:
    conn, addr = s.accept()
    t = threading.Thread(target=job, args=(conn,))
    t.start()

s.close()