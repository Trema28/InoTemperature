from time import sleep

import serial
from glob import glob

class InoTemperature(serial.Serial):
    ''' '''

    _CONN_REQ = b'A'
    _CMD_PING = b'p'
    _CMD_GETTEMP = b'g'

    def __init__(self, port=None, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None, **kwargs):
        if not timeout:
            timeout = 1
        super().__init__(port=port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout, xonxoff=xonxoff, rtscts=rtscts, write_timeout=write_timeout, dsrdtr=dsrdtr, inter_byte_timeout=inter_byte_timeout, exclusive=exclusive, **kwargs)

        if self.port:
            if not self._establish_contact():
                print('\ncannot establish a connection')
                exit(1)
        else:
            if not self._find_and_establish():
                print('\ncannot find a port')
                exit(1)

    def _establish_contact(self):
        self.readlines()
        for i in range(3):
            self.write(self._CONN_REQ)
            if self._CONN_REQ in self.readline():
                return True
            sleep(.3)
        return False

    def _find_and_establish(self):
        for port in glob('/dev/ttyUSB*'):
            print('trying ' + port, end='... ')

            if self.is_open:
                self.close()

            self.setPort(port)
            self.open()

            if self._establish_contact():
                print('succeeded')
                return True

            print('failed')
        return False

    def _rquest_data(self, cmd):
        self.write(cmd)
        return self.readlines()[-1]

    def ping(self):
        data = self._rquest_data(self._CMD_PING)
        return int(data)

    def get_temperatures(self):
        data = self._rquest_data(self._CMD_GETTEMP)
        data = data.decode().strip().split(' ')
        return [*map(float, data)]
