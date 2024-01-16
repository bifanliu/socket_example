#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import threading

HOST = '0.0.0.0'
PORT = 7000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

print('server start at: %s:%s' % (HOST, PORT))
print('wait for connection...')

while True:
    # receive data
    indata, addr = s.recvfrom(1024)

    # decode
    indata_decode = indata.decode()

    # if input data content doesn't exit then keep loop
    if indata_decode.lower() == "exit":
        break

    # print write back client content
    upperstring = indata_decode.upper()
    print("Server Message is " + upperstring)

    # write back to client
    s.sendto(upperstring.encode("utf-8"), addr)

s.close()