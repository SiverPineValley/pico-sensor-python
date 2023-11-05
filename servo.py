from machine import Pin, PWM

class Servo(object):
    
    def __init__(self, pin=15, freq=50):
        self.servo = PWM(Pin(pin), freq)     # the Pico PWM pin
        self.move(1.5)
 
    # 1.5가 0도일 때, 90도: 5.2, 180도: 8.2, 270도: 11
    def move(self, duty_cycle = 1.5):
        self.servo.duty_u16(int(65535 * duty_cycle / 100))
 
    def deinit(self):
        self.servo.deinit()
         
         
#m = Servo(15, 50)
#m.move()
#m.deinit()
