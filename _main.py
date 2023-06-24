from machine import Pin, UART
#from micropyGPS import MicropyGPS
from utility import Utility
from at import AT
import wifi
import network
from utime import sleep
#import mqtt
import json
import uasyncio

import socket
import binascii

async def main():
    #ssid = "csg"
    #password = None
    #TIMEZONE = 9
    speed = "0"
    ip = ""
    sid = ""
    wifi_scanned = ""
    gpsInfo = []

    # WLAN 초기화
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # GPS 모듈 초기화 - 미사용
    #gps_module = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
    #my_gps = MicropyGPS(TIMEZONE)

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

    # MQTT 초기 세팅 - 미사용
    #while True:
    #    try:
    #        client = mqtt.mqtt_connect(client_id, mqtt_server, mqtt_port, user, password)
    #        break
    #    except OSError as e:
    #        pass

    while True or KeyboardInterrupt:   
        # GPS 데이터 가져오기
        #gpsInfo = at.getGpsInfo().split(",")
        gpsInfo = uasyncio.run(at.getGpsInfo()).split(",")
        #length = gps_module.any()
        #if length>0:
        #    b = gps_module.read(length)
        #    for x in b:
        #        msg = my_gps.update(chr(x))
        
        #latitude = utility.convert(my_gps.latitude)
        #longitude = utility.convert(my_gps.longitude)
        
        wifi_scanned = uasyncio.run(wifi.scan(wlan))

        try:
            latitude = ""
            longitude = ""
            if len(gpsInfo) >= 5:
                latitude = gpsInfo[3]
                longitude = gpsInfo[4]
      
            if (latitude == "" and longitude == ""):
                data = {
                    "sid": sid,
                    "lat": latitude,
                    "lon": longitude,
                    "speed": speed,
                    "wifiLoc": [wifi_scanned],
                    "battery": 100
                }
                jsonData = json.dumps(data)
                print(jsonData)
                #client.publish(topic, msg=str(jsonData))
                sleep(10)
                continue
            
            if len(gpsInfo) >= 7:
                speed = gpsInfo[6]
            
            data = {
                "sid": sid,
                "lat": latitude,
                "lon": longitude,
                "speed": speed,
                "wifiLoc": [wifi_scanned],
                "battery": 100
            }
            jsonData = json.dumps(data)
            print(jsonData)
            #client.publish(topic, msg=str(jsonData))
            sleep(10)
        except Exception as e:
            print(e)
            pass

        except:
            print("err")
            pass

uasyncio.run(main())
