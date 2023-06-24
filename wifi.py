from network import WLAN
import socket
import binascii
from time import sleep
import uasyncio
    
def connect(wlan: WLAN, ssid: str, password: str)->str:
    #Connect to WLAN
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

async def scan(wlan: WLAN)->str:
    try:
        scanned_wifi_rssi = ""
        networks = wlan.scan() # list with tupples with 6 fields ssid, bssid, channel, RSSI, security, hidden
        if len(networks) == 0:
            return scanned_wifi_rssi
        
        networks.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
        if len(networks) > 0:
            w = networks[0]
            scanned_wifi_rssi = w[0].decode()
            #Connection(ssid = w[0].decode(), bssid = binascii.hexlify(w[1]).decode(), channel = w[2], rssi = w[3], security = w[4], hidden = w[5])
    except:
        return scanned_wifi_rssi
    
    return scanned_wifi_rssi

#wifi = Wifi()
#try:
#    ip = wifi.connect("csg", None)
#    print(ip)
#except:
#    print(None)
# while True or KeyboardInterrupt or SerialException:
#       try:
#           r = wifi.scan()
#           print(r)
#           sleep(1)
#       except KeyboardInterrupt or SerialException:
#           continue
#       else:
#           continue



