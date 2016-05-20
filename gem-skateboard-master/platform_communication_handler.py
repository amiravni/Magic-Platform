import serial


COM_BAUDRATE = 9600

class platformCommunicationHandler:

    _ser_con = None

    def __init__(self,comPort):
        try:
            self._ser_con = serial.Serial(comPort,COM_BAUDRATE)
            ser.timeout = 0.01
        except:
            print 'Couldn\'t use %s port, Try using another one' % comPort

    def turn_leds_on(self):
        if self._ser_con is not None:
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,6,150,150,0))
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,6,150,150,0))
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,6,150,150,0))

    def move_forward(self):
        if self._ser_con is not None:
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
            self._ser_con.write(struct.pack('B'*8,255,254,100,1,1,150,150,0))
