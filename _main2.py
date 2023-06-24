from machine import Pin, UART
from utility import Utility
import wifi
import network
from utime import sleep
import json
from at import AT

import socket
import binascii

speed1 = "0"
ip = ""
sid = ""

# WLAN 초기화
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# utility 클래스 초기화
utility = Utility()
sid = utility.getUniqueDeivcieId()
print("Device ID: " + sid)


# LTE 모듈 초기화
at = AT()
ip = at.get_ip()
print("IP Address: " + ip)

gpsInfo = []
gpsInfo = at.getGpsInfo().split(",")
print(gpsInfo)
