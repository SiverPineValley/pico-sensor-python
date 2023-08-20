import sys

sys.path.append("")

from micropython import const

import uasyncio
import aioble
import bluetooth
from utility import Utility

# org.bluetooth.service.authorization_control
_AUTH_SVC_UUID = bluetooth.UUID(0x183D
)
_AUTH_CHA_UUID = bluetooth.UUID(0x2B33
)

_ALERT_SVC_UUID = bluetooth.UUID(0x1811
)
_ALERT_CHA_UUID = bluetooth.UUID(0x2A46
)

async def connect_lock_control():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if _ALERT_SVC_UUID in result.services():
                return result.device
    return None

async def scan_lock_control(time_sleep=2000):
    while True:
        try:
            device = await connect_lock_control()
            if not device:
                print("Lock control not found")
                await uasyncio.sleep_ms(time_sleep)
            break
        except:
            await uasyncio.sleep_ms(time_sleep)
        
    while True:
        try:
            print("Connecting to", device)
            connection = await device.connect()
            break
        except uasyncio.TimeoutError:
            print("Timeout during connection")
            await uasyncio.sleep_ms(time_sleep)
    
    async with connection:
        while True:
            try:
                lock_control = await connection.service(_ALERT_SVC_UUID)
                lock_control_data = await lock_control.characteristic(_ALERT_CHA_UUID)
                break
            except asyncio.TimeoutError:
                print("Timeout discovering lock_control")
                sleep(2)
            except:
                print("Failed to connect BLE")
                sleep(2)
    
        while True:
            try:
                lock = await lock_control_data.read()
                print("Lock code: {:.s}".format(lock))
                await uasyncio.sleep_ms(time_sleep)
            except:
                print("scan failed!!")
                await uasyncio.sleep_ms(time_sleep)

async def ble_aync_test():
    while True:
        print("Something scanned...")
