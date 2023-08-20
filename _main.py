from machine import Pin, UART
from micropyGPS import MicropyGPS
from utility import Utility
from at import AT
import wifi
import network
from utime import sleep
import ble
import json
import uasyncio

import socket
import binascii

async def main_job():
    TIMEZONE = 9
    speed = "0"
    ip = ""
    sid = ""
    wifi_scanned = ""
    gpsInfo = []
    host = "http://34.64.74.23:1323"
    uri = "/api/v1/trm/log/gps"

    # WLAN 초기화
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # GPS 모듈 초기화 - 미사용
    gps_module = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
    my_gps = MicropyGPS(TIMEZONE)

    # utility 클래스 초기화
    utility = Utility()
    sid = utility.getUniqueDeivcieId()
    print("Device ID: " + sid)

    # LTE 모듈 초기화
    at = AT()
    ip = at.get_ip()
    print("IP Address: " + ip)

    # WIFI 연결 - 미사용
    #try:
    #    ip = wifi.connect(wlan, ssid, password)
    #except KeyboardInterrupt:
    #    print("Wifi connection error...")
    
    while True or KeyboardInterrupt:   
        # GPS 데이터 가져오기
        length = gps_module.any()
        if length>0:
           b = gps_module.read(length)
           for x in b:
               msg = my_gps.update(chr(x))
        
        latitude = utility.convert(my_gps.latitude) or ""
        longitude = utility.convert(my_gps.longitude) or ""
        
        wifi_scanned = uasyncio.run(wifi.scan(wlan)) or ""
        speed = "0"

        try:
            data = 'sid={sid}&lat={lat}&lon={lon}&speed={speed}&wifiLoc={wifiLoc}&battery={battery}'
            if (latitude == "" and longitude == ""):
                data = data.format(sid=sid, lat=latitude, lon=longitude, speed=speed, wifiLoc=wifi_scanned, battery=100)
                at.http_post(host, uri, data)
                await uasyncio.sleep_ms(10000)
                continue
            
            speed = my_gps.speed_string('kph')
            data = data.format(sid=sid, lat=latitude, lon=longitude, speed=speed, wifiLoc=wifi_scanned, battery=100)
            at.http_post(host, uri, data)
            await uasyncio.sleep_ms(10000)
        except Exception as e:
            print(e)
            pass

        except:
            print("err")
            pass

async def main():
    await uasyncio.gather(ble.scan_lock_control(), main_job())

uasyncio.run(main())

