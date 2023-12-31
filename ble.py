import sys

sys.path.append("")

from micropython import const

import uasyncio
import aioble
import bluetooth
from utility import Utility
from servo import Servo

# org.bluetooth.service.authorization_control
_AUTH_SVC_UUID = bluetooth.UUID(0x183D
)
_AUTH_CHA_UUID = bluetooth.UUID(0x2B33
)

_ALERT_SVC_UUID = bluetooth.UUID(0x1811
)
_ALERT_CHA_UUID = bluetooth.UUID(0x2A46
)

svm = Servo(15, 50)
async def connect_lock_control():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if _ALERT_SVC_UUID in result.services():
                return result.device
    return None

async def scan_lock_control(time_sleep=2000):
    while True:
        restart = False
        while True:
            try:
                device = await connect_lock_control()
                if not device:
                    print("Lock control not found")
                    await uasyncio.sleep_ms(time_sleep)
                else:
                    break
            except Exception as e:
                print(f"Error when device searching: {e}")
                await uasyncio.sleep_ms(2000)
        
        while True:
            try:
                print("Connecting to", device)
                connection = await device.connect()
                break
            except uasyncio.TimeoutError:
                print("Timeout during connection")
                await uasyncio.sleep_ms(time_sleep)
                restart = True
                break
            except Exception as e:
                print(f"Error when device connecting: {e}")
                await uasyncio.sleep_ms(time_sleep)
                restart = True
                break
        
        if restart:
            continue
        
        async with connection:
            while True:
                try:
                    lock_control = await connection.service(_ALERT_SVC_UUID)
                    lock_control_data = await lock_control.characteristic(_ALERT_CHA_UUID)
                    break
                except uasyncio.TimeoutError:
                    print("Timeout discovering lock_control")
                    uasyncio.sleep_ms(time_sleep)
                    restart = True
                    break
                except Exception as e:
                    print(f"Error when connecting to svc/char: {e}")
                    uasyncio.sleep_ms(time_sleep)
                    restart = True
                    break
        
            if restart:
                continue
            
            while True:
                try:
                    # 서보모터 열기
                    svm.move(3.5)
                    lock = await lock_control_data.read()
                    print("Lock code: {:.s}".format(lock))
                    await uasyncio.sleep_ms(time_sleep)
                except:
                    # 서보모터 잠그기
                    svm.move(1.5)
                    print("scan failed!!")
                    await uasyncio.sleep_ms(time_sleep)
                    restart = True
                    break
                

