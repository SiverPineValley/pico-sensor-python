import machine
import utime
import time
import uasyncio

class AT():
    def __init__(
        self, uart_port: int=0, uart_baute: int=115200, tx: int=0, rx: int=1, bits: int=8, timeout: int=1000
    ) -> None:
        # UART 세팅
        self.Pico_SIM7080G = machine.UART(uart_port, uart_baute, tx=machine.Pin(tx), rx=machine.Pin(rx))
        self.Pico_SIM7080G.init(baudrate=uart_baute, bits=bits, parity=None, stop=0, timeout=timeout)
        self.set_network()
        self.ip = self.check_network()
        
    def get_ip(self):
        return self.ip

    def set_network(self):
        print("Setting to CAT-M mode:\n")
        self.send_at("AT+CFUN=0", "OK")
        self.send_at("AT+CMEE=2;+CNMP=38;+CMNB=1;+CFUN=1", "OK")
        #self.send_at("AT+CNMP=38", "OK")
        #self.send_at("AT+CMNB=1", "OK")
        #self.send_at("AT+CFUN=1", "OK")
        utime.sleep(5)

    def check_network(self):
        if self.send_at("AT+CPIN?", "READY") != 1:
            print("------Please check whether the sim card has been inserted!------\n")
        for i in range(1, 10):
            if self.send_at("AT+CGATT?", "1"):
                print('------SIM7080G is online------\r\n')
                break
            else:
                print('------SIM7080G is offline, please wait...------\r\n')
                utime.sleep(5)
                continue
        self.send_at("AT+CSQ", "OK")
        self.send_at("AT+CPSI?", "OK")
        self.send_at("AT+COPS?", "OK")
        get_resp_info = str(self.send_at_wait_resp('AT+CGNAPN', 'OK'))
        getapn1 = get_resp_info[get_resp_info.find('\"')+1:get_resp_info.rfind('\"')]
        self.send_at("AT+CNCFG=0,1,\""+getapn1+"\"", "OK")
        self.send_at('AT+CNACT=0,1', 'OK')
        ip_resp_info = str(self.send_at_wait_resp('AT+CNACT?', 'OK'))
        ip = ip_resp_info[get_resp_info.find('\"')+2:get_resp_info.rfind('\"')].replace("\\r", "").replace("\"", "").replace("\\", "")
        return ip

    # Set HTTP body and head length
    def set_http_length(self, bodylen: int, headerlen: int):
        bodyLenCmd = 'AT+SHCONF=\"BODYLEN\",%d' % (bodylen)
        headerLenCmd = 'AT+SHCONF=\"HEADERLEN\",%d' % (headerlen)
        
        self.send_at(bodyLenCmd, 'OK')
        self.send_at(headerLenCmd, 'OK')


    # Set HTTP header content
    def set_http_content(self, contentType: str="application/x-www-form-urlencoded"):
        self.send_at('AT+SHCHEAD', 'OK')
        self.send_at('AT+SHAHEAD=\"Content-Type\",\"application/x-www-form-urlencoded\"', 'OK')
        self.send_at('AT+SHAHEAD=\"User-Agent\",\"curl/7.47.0\"', 'OK')
        self.send_at('AT+SHAHEAD=\"Cache-control\",\"no-cache\"', 'OK')
        self.send_at('AT+SHAHEAD=\"Connection\",\"keep-alive\"', 'OK')
        self.send_at('AT+SHAHEAD=\"Accept\",\"*/*\"', 'OK')
        self.send_at('AT+SHCHEAD', 'OK')

    # HTTP GET TEST
    def http_get(self, host: str, uri: str):
        self.send_at('AT+SHCONF="URL",\"'+host+'\"', 'OK')
        self.set_http_length(1024, 350)
        #self.send_at('AT+CGACT=1', 'OK')
        self.send_at('AT+SHCONN', 'OK', 3000)
        if self.send_at('AT+SHSTATE?', '1'):
            self.set_http_content()
            resp = str(self.send_at_wait_resp('AT+SHREQ=\"'+uri+'\",1', 'OK',8000))
            # print("resp is :", resp)
            try:
                get_pack_len = int(resp[resp.rfind(',')+1:-5])
                if get_pack_len > 0:
                    self.send_at_wait_resp('AT+SHREAD=0,'+str(get_pack_len), 'OK', 5000)
                    self.send_at('AT+SHDISC', 'OK')
                else:
                    print("HTTP Get failed!\n")
            except ValueError:
                print("ValueError!\n")
        else:
            print("HTTP connection disconnected, please check and try again\n")


    # HTTP POST TEST
    def http_post(self, host: str, uri: str, body: str):
        self.send_at('AT+SHCONF="URL",\"' + host + '\"', 'OK')
        self.set_http_length(1024, 350)
        #self.send_at('AT+CGACT=1', 'OK')
        self.send_at('AT+SHCONN', 'OK', 3000)
        if self.send_at('AT+SHSTATE?', '1'):
            self.set_http_content()
            self.send_at('AT+SHCPARA', 'OK')
            if self.send_at('AT+SHBOD=%d,10000' % len(body), '>', 1000) :
                self.send_at(body, 'OK')
                resp = str(self.send_at_wait_resp('AT+SHREQ=\"'+ uri +'\",3','OK', 8000))
                try:
                    get_pack = int(resp[resp.rfind(',')+1:-5])
                    print(get_pack)
                    if get_pack > 0:
                        self.send_at_wait_resp('AT+SHREAD=0,' + str(get_pack), 'OK', 3000)
                        self.send_at('AT+SHDISC', 'OK')
                    else:
                        print("HTTP Post failed!\n")
                except ValueError:
                    print("ValueError!\n")

            else:
                print("Send failed\n")

        else:
            print("HTTP connection disconnected, please check and try again\n")
            self.set_network()
            self.ip = self.check_network()

    # Send AT command
    def send_at(self, cmd, back, timeout=1500):
        rec_buff = b''
        self.Pico_SIM7080G.write((cmd + '\r\n').encode())
        prvmills = utime.ticks_ms()
        while (utime.ticks_ms() - prvmills) < timeout:
            if self.Pico_SIM7080G.any():
                rec_buff = b"".join([rec_buff, self.Pico_SIM7080G.read(1)])
        if rec_buff != '':
            if back not in rec_buff.decode():
                if 'ERROR' in rec_buff.decode():
                    print(cmd + ' back:\t' + rec_buff.decode())
                    return 0
                else:
                    # Resend cmd
                    rec_buff = b''
                    rec_buff = self.send_at_wait_resp(cmd, back, timeout)
                    if back not in rec_buff.decode():
                        print(cmd + ' back:\t' + rec_buff.decode())
                        return 0
                    else:
                        return 1
            else:
                print(rec_buff.decode())
                return 1
        else:
            print(cmd + ' no responce\n')
            # Resend cmd
            rec_buff = self.send_at_wait_resp(cmd, back, timeout)
            if back not in rec_buff.decode():
                print(cmd + ' back:\t' + rec_buff.decode())
                return 0
            else:
                return 1


    # Send AT command and return response information
    def send_at_wait_resp(self, cmd, back, timeout=2000):
        rec_buff = b''
        self.Pico_SIM7080G.write((cmd + '\r\n').encode())
        prvmills = utime.ticks_ms()
        while (utime.ticks_ms() - prvmills) < timeout:
            if self.Pico_SIM7080G.any():
                rec_buff = b"".join([rec_buff, self.Pico_SIM7080G.read(1)])
        if rec_buff != '':
            if back not in rec_buff.decode():
                print(cmd + ' back:\t' + rec_buff.decode())
            else:
                print(rec_buff.decode())
        else:
            print(cmd + ' no responce')
        # print("Response information is: ", rec_buff)
        return rec_buff
    
    def waitResp_info(self, info='',timeout=2000):
        prvMills = utime.ticks_ms()
        info = b""
        while (utime.ticks_ms()-prvMills)<timeout:
            if self.Pico_SIM7080G.any():
                info = b"".join([info, self.Pico_SIM7080G.read(1)])
        print(info.decode())
        return info
    
    async def getGpsInfo(self):
        print('Start GPS session...')
        self.send_at('AT+CGNSPWR=1','OK')
        utime.sleep(2)
        rec_buff = b''
        self.Pico_SIM7080G.write( 'AT+CGNSINF\r\n'.encode() )
        rec_buff = self.waitResp_info()
        gpsInfo = str(rec_buff.decode())
        self.send_at('AT+CGNSPWR=0','OK')
        utime.sleep(2)
        return gpsInfo
    
    def turnOffGps(self):
        self.send_at('AT+CGNSPWR=0','OK')



