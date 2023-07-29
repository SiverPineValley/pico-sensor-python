"""
Raspberry Pi Pico (MicroPython) exercise:
work with SIM7080G Cat-M/NBIoT Module
"""
import machine
import utime
import time

# using pin defined
pwr_en = 14  # pin to control the power of the module
wakeup_en = 17  # pin to control the power of the module

# uart setting
uart_port = 0
uart_baute = 115200
Pico_SIM7080G = machine.UART(uart_port, uart_baute, tx=machine.Pin(0), rx=machine.Pin(1))
Pico_SIM7080G.init(baudrate=uart_baute, bits=8, parity=None, stop=0, timeout=1000)

# power on/off the module
def module_power():
    pwr_key = machine.Pin(pwr_en, machine.Pin.OUT)
    utime.sleep(0.1)
    pwr_key.high()
    utime.sleep(1)
    pwr_key.low()
    utime.sleep(1)

def wakeup_module():
    pwr_key = machine.Pin(wakeup_en, machine.Pin.OUT)
    pwr_key.high()
    utime.sleep(2)
    pwr_key.low()

def send_cmd_new(command_to_send="", timeout=10, success="OK", failure=None, echo_cmd=False):
    byte_command = f"{command_to_send}\r\n".encode()
    print("command: " + str(byte_command))
    Pico_SIM7080G.write(byte_command)
    t_start = time.time()
    reply = list()
    while True:
        if Pico_SIM7080G.any():
            line = Pico_SIM7080G.readline()
            print("reply: " + str(line))
            echo = False
            if echo_cmd:
                
                echo = line.decode('utf-8').strip()
                return ("Success", reply, time.time()-t_start)
            if (line != b"\r\n"):
                line = line.decode('utf-8').strip()
                reply.append(line)
                if success in line:
                    return ("Success", reply, time.time()-t_start)
                if failure and line.startswith(failure):
                    return ("Error", reply, time.time()-t_start)
        if (time.time()-t_start) > timeout:
            return ("Timeout", reply, time.time()-t_start)
        time.sleep(0.01)

# Send AT command
def send_at(cmd, back, timeout=1000):
    rec_buff = b''
    Pico_SIM7080G.write((cmd + '\r\n').encode())
    prvmills = utime.ticks_ms()
    while (utime.ticks_ms() - prvmills) < timeout:
        if Pico_SIM7080G.any():
            rec_buff = b''.join([rec_buff, Pico_SIM7080G.read(1)])
    if rec_buff != b'':
        if back not in rec_buff.decode():
            print(cmd + ' back:\t' + rec_buff.decode())
            return 0
        else:
            print(rec_buff.decode())
            return 1
    else:
        print(cmd + ' no responce')

def at_test():
    print("---------------------------SIM7080G AT TEST---------------------------")
    while True:
        try:
            command_input = str(input('Please input the AT command,press Ctrl+C to exit:\000'))
            send_cmd_new(command_to_send=command_input, timeout=2, success="OK", failure=None, echo_cmd=False)
            #send_at(command_input, 'OK', 2000)
        except KeyboardInterrupt:
            print('\n------Exit AT Command Test!------\r\n')
            module_power()
            print("------The module is power off!------\n")
            break

def AT(cmd="", timeout=10, success="OK", failure="ERROR"):
    cmd = 'AT' + cmd
    fileTools.debug_log(f"----------- {cmd} -----------")
    if config.verbose: print(f"verbose --- {cmd} ----")
    response = send_serial_cmd(command_to_send=cmd, timeout=timeout, success=success, failure=failure, echo_cmd=False)
    return response

def start_sim7080g_module():
    # from libs.sim7080_cmd import restart_board
    # restart_board(_timeout=10)
    AT(timeout=4)
    AT(timeout=4)
    response = AT(timeout=10) # test if its on
    if "Timeout" in response[0]: # if off
        fileTools.debug_log("[!] no resp. power cycle module")
        power_on()  # toggle PWR pin
        time.sleep(5)
        index = 0
        while True: # wait for ready response
            response = AT(success="OK", timeout=5)
            if "Success" in response[0]:
                break
            if index > 6:
                fileTools.debug_log("[!] failed to start")
                return False
            index += 1
    fileTools.debug_log("[*] module started")
    if config.verbose: print("[*] module started")
    return True

# SIM7080G main program
#wakeup_module()
module_power()
at_test()
