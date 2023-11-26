from machine import Pin, UART
from micropyGPS import MicropyGPS
from utility import Utility
from max17043 import max17043
from at import AT
import wifi
import network
from utime import sleep
import ble
import json
import uasyncio

import socket
import binascii

def pwrkey_on():
    pwrkey_pin = machine.Pin(8, machine.Pin.OUT)
    pwrkey_pin.value(1)
    uasyncio.sleep_ms(2000)
    pwrkey_pin.value(1)
    uasyncio.sleep_ms(2000)

async def lte_scan():
    TIMEZONE = 9
    speed = "0"
    ip = ""
    sid = ""
    wifi_scanned = ""
    gpsInfo = []
    host = "http://trailer-manager.com:1323"
    uri = "/api/v1/trm/log/gps"

    # MAX17043 초기화 (배터리 잔량 측정 모듈)
    m = max17043()
    print(m.__str__())

    # WLAN 초기화
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # LTE 모듈 초기화
    pwrkey_on()

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
    
    while True:
        # GPS 데이터 가져오기
        length = gps_module.any()
        if length>0:
           b = gps_module.read(length)
           for x in b:
               msg = my_gps.update(chr(x))
        
        latitude = utility.convert(my_gps.latitude) or ""
        longitude = utility.convert(my_gps.longitude) or ""
               
        wifi_scanned = await wifi.scan(wlan) or ""
        speed = "0"


        try:
            battery = m.getSoc()
            data = 'sid={sid}&lat={lat}&lon={lon}&speed={speed}&wifiLoc={wifiLoc}&battery={battery}'
            if (latitude == "" and longitude == ""):
                data = data.format(sid=sid, lat=latitude, lon=longitude, speed=speed, wifiLoc=wifi_scanned, battery=battery)
                at.http_post(host, uri, data)
                await uasyncio.sleep_ms(1800000)
                continue
            speed = my_gps.speed_string('kph')
            data = data.format(sid=sid, lat=latitude, lon=longitude, speed=speed, wifiLoc=wifi_scanned, battery=battery)
            at.http_post(host, uri, data)
            await uasyncio.sleep_ms(1800000)
        except Exception as e:
            print(e)
            pass

        except:
            print("err")
            pass

async def main():
    loop = uasyncio.get_event_loop()
    loop.create_task(ble.scan_lock_control(2000))   		# 첫 번째 코루틴을 생성하고 실행
    loop.create_task(lte_scan())  							# 두 번째 코루틴을 생성하고 실행
    loop.run_forever()
    loop.close()

uasyncio.run(main())
