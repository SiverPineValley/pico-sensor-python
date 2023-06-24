"""
Raspberry Pi Pico (MicroPython) exercise:
work with SIM7080G Cat-M/NBIoT Module
"""
import machine
import utime
import binascii

# uart setting
uart_port = 0
uart_baute = 115200
Pico_SIM7080G = machine.UART(uart_port, uart_baute)

def RemoveNonAsciiBytes(s):
    o = b""
    for b in s:
      if b < 0x7F:
        o += bytes(chr(b), "ascii")
    return o

def RemoveAsciiBytes(s):
    o = b""
    for b in s:
      if b < 0x7F:
        continue
      else:
        o += bytes(chr(b), "ascii")
    return o

# Send AT command
def send_at_new(cmd, back="OK", timeout=1000):
    rec_buff = b''
    Pico_SIM7080G.write((cmd + '\r\n').encode())
    prvmills = utime.ticks_ms()
    while (utime.ticks_ms() - prvmills) < timeout:
        if Pico_SIM7080G.any():
            rec_buff = b"".join([rec_buff, Pico_SIM7080G.read(1)])
    if rec_buff != '':
        print(rec_buff)
        print(RemoveAsciiBytes(rec_buff).decode())
        print(RemoveNonAsciiBytes(rec_buff))
        try:
            print("Response: " + RemoveNonAsciiBytes(rec_buff).decode())
        except:
            print("\r\n")
    else:
        print(cmd + ' no responce')


##########################################################
# Send an AT command - return True if we got an expected
# response ('back'), otherwise False
##########################################################
def send_at(cmd, back="OK", timeout=500):
    # Send the command and get the response (until timeout)
    buffer = send_at_get_resp(cmd, timeout)
    if len(buffer) > 0: return (back in buffer)
    return False

##########################################################
# Send an AT command - just return the response
##########################################################
def send_at_get_resp(cmd, timeout=500):
    # Send the AT command
    Pico_SIM7080G.write((cmd + "\r\n").encode())

    # Read and return the response (until timeout)
    return read_buffer(timeout)

##########################################################
# Read in the buffer by sampling the UART until timeout
##########################################################
def read_buffer(timeout):
    buffer = bytes()
    now = utime.ticks_ms()
    while (utime.ticks_ms() - now) < timeout and len(buffer) < 1025:
        if Pico_SIM7080G.any():
            buffer += Pico_SIM7080G.read(1)
    return buffer.decode()

##########################################################
# Module startup detection
# Send a command to see if the modem is powered up
##########################################################
def boot_modem():
    state = False
    count = 0
    while count < 5:
        if send_at("ATE1"):
            print("The modem is ready")
            return True
        if not state:
            print("Powering the modem")
            power_module()
            state = True
        utime.sleep(4)
        count += 1
    return False

##########################################################
#Power the module on/off
##########################################################
def power_module():
    pwr_key = machine.Pin(14, machine.Pin.OUT)
    pwr_key.value(1)
    utime.sleep(1.5)
    pwr_key.value(0)


def set_network():
    print("Setting to NB-IoT mode:\n")
    send_at("AT+CFUN=0", "OK")
    send_at("AT+CNMP=38", "OK")  # Select LTE mode
    send_at("AT+CMNB=2", "OK")  # Select NB-IoT mode,if Cat-M，please set to 1
    send_at("AT+CFUN=1", "OK")
    utime.sleep(5)


# Check the network status
def check_network():
    if send_at("AT+CPIN?", "READY") != 1:
        print("------Please check whether the sim card has been inserted!------\n")
    for i in range(1, 10):
        if send_at("AT+CGATT?", "1"):
            print('------SIM7080G is online------\r\n')
            break
        else:
            print('------SIM7080G is offline, please wait...------\r\n')
            utime.sleep(5)
            continue
    send_at("AT+CSQ", "OK")
    send_at("AT+CPSI?", "OK")
    send_at("AT+COPS?", "OK")
    get_resp_info = str(send_at_wait_resp("AT+CGNAPN", "OK"))
    # getapn = get_resp_info.split('\"')
    # print(getapn[1])
    getapn1 = get_resp_info[get_resp_info.find('\"')+1:get_resp_info.rfind('\"')]
    print(getapn1)
    send_at("AT+CNCFG=0,1,\""+getapn1+"\"", "OK")
    send_at('AT+CNACT=0,1', 'OK')
    send_at('AT+CNACT?', 'OK')


def at_test():
    print("---------------------------SIM7080G AT TEST---------------------------")
    while True:
        try:
            command_input = str(input('Please input the AT command,press Ctrl+C to exit:\000'))
            send_at_new(command_input, 'OK', 2000)
        except KeyboardInterrupt:
            print('\n------Exit AT Command Test!------\r\n')
            power_module()
            print("------The module is power off!------\n")
            break


# Start the modem
#boot_modem()
at_test()
