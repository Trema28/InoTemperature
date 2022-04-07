from time import sleep

from serial import Serial
from glob import glob

class InoTemperature(Serial):
    ''' '''

    _CONN_REQ = b'A'
    _CMD_PING = b'p'
    _CMD_GETTEMP = b'g'

    def __init__(self, timeout=1, **kwargs):
        super().__init__(timeout=timeout, **kwargs)

        if self.port:
            assert self._establish_contact(), 'can not establish connection'
        else:
            assert self._find_and_establish(), 'can not find a port'

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
