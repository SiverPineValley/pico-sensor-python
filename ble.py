import sys

sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth
from utility import Utility

# org.bluetooth.service.authorization_control
_AUTH_SVC_UUID = bluetooth.UUID(0x183D
)
_AUTH_CHA_UUID = bluetooth.UUID(0x2B33
)

async def connect_lock_control():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if _AUTH_SVC_UUID in result.services():
                return result.device
    return None

async def scan_lock_control(time_gap=1000):
    device = await connect_lock_control()
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
            lock_control = await connection.service(_AUTH_SVC_UUID)
            lock_control_data = await lock_control.characteristic(_AUTH_CHA_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering lock_control")
            return
    
        while True:
            lock = await lock_control_data.read()
            print("Lock code: {:.s}".format(lock))
            await asyncio.sleep_ms(time_gap)

#asyncio.run(scan_lock_control())
