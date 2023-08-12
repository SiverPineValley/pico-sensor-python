import sys

sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth
from utility import Utility

#import random
#import struct

# org.bluetooth.service.authorization_control
_AUTH_CONT_UUID = bluetooth.UUID(0x183D
)
_CUST_SVC_UUID = bluetooth.UUID(0x1811
)
_CUST_CHA_UUID = bluetooth.UUID(0x2A46
)

async def scan_lock_control(sid):
    # Scan for 5 seconds, in active mode, with very low interval/window (to maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            #print(result, result.name(), result.rssi, result.services())
            if result.name() == "Alert Notification" and _CUST_SVC_UUID in result.services():
                return result.device
    return None


async def main():
    utility = Utility()
    sid = utility.getUniqueDeivcieId()
    print(sid)
    device = await scan_lock_control(sid)
    if not device:
        print("Lock control not found")
        return
    
    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return
    
    async with connection:
        try:
            lock_control = await connection.service(_CUST_SVC_UUID)
            lock_control_data = await lock_control.characteristic(_CUST_CHA_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/authurization_control")
            return
    
        #lock = await lock_control_data.read()
        #print("Lock code: {:.2f}".format(lock))
        while True:
            lock = await lock_control_data.read()
            print("Lock code: {:.s}".format(lock))
            await asyncio.sleep_ms(1000)

asyncio.run(main())
