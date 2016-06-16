import serial
import sys, traceback
import struct

COM_BAUDRATE = 9600
PLATFORM_SPEED = 80
class platformCommunicationHandler:

    _ser_con = None

    def __init__(self,comPort):
        try:
            self._ser_con = serial.Serial(comPort,COM_BAUDRATE)
            self._ser_con.timeout = 0.01
        except:
            print 'Couldn\'t use %s port, Try using another one' % comPort
            traceback.print_exc(file=sys.stdout)
    def turn_leds_on(self):
        if self._ser_con is not None:
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,6,150,150,0))
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,6,150,150,0))
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,6,150,150,0))

    def move_forward(self):
        if self._ser_con is not None:
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,1,PLATFORM_SPEED,PLATFORM_SPEED,0))
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,1,PLATFORM_SPEED,PLATFORM_SPEED,0))
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,1,PLATFORM_SPEED,PLATFORM_SPEED,0))
