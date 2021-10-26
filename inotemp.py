import serial

class InoTemperature(serial.Serial):
    ''' '''

    _PROTO_SOT = 0x2
    _PROTO_EOT = 0x3

    _CMD_PING = ord('p')
    _CMD_GETTEMP = ord('g')

    def __init__(self, port=None, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None, **kwargs):
        super().__init__(port=port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout, xonxoff=xonxoff, rtscts=rtscts, write_timeout=write_timeout, dsrdtr=dsrdtr, inter_byte_timeout=inter_byte_timeout, exclusive=exclusive, **kwargs)

    def _decode(self, rec):
        data = rec[rec.index(self._PROTO_SOT) + 1:rec.index(self._PROTO_EOT)]
        return data.decode().split(',')

    def _encode(self, data):
        arr = [self._PROTO_SOT]

        for i, d in enumerate(data):
            arr.append(d)
            if i != len(data) - 1:
                arr.append(ord(','))

        arr.append(self._PROTO_EOT)

        return bytearray(arr)

    def _send(self, data):
        self.write(self._encode(data))

    def _receive(self):
        rec = self.read_until(chr(self._PROTO_EOT))
        return self._decode(rec)

    def ping(self):
        self._send([self._CMD_PING])
        return int(self._receive()[1])

    def getTemperature(self):
        self._send([self._CMD_GETTEMP])
        temp = self._receive()
        return (float(temp[1])/1023.0) * 5.0 * 1000/10


if __name__ == '__main__':
    ino = InoTemperature('/dev/ttyUSB0', timeout=.1)

    i = input('--> ')
    while i != ' ':
        if i == 'p':
            print(ino.ping())

        if i == 'g':
            print(ino.getTemperature())

        i = input('--> ')
