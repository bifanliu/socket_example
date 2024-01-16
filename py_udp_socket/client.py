#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket

HOST = '0.0.0.0'
PORT = 7000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((HOST, PORT))

while True:
    # read user input
    user_input = input("Please input yout messae: ")

    print(user_input)

    # send to server
    s.sendto(user_input.encode("utf-8"), (HOST, PORT))

    # if string is exit then over
    if user_input.lower() == "exit":
        break

    # server writeback data
    indata, addr = s.recvfrom(1024)

    # decode
    indata_decode = indata.decode("utf-8")

    # print writeback data
    print("Write Back Message content is " + indata_decode)

print("client is over")

s.close()