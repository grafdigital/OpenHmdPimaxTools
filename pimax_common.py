import struct
import bitstring

class BufferPointer():
    def __init__(self, data):
        self.data = data
        self.c = 0

    def skip_byte(self, s=1):
        self.c += s

    def read8(self):
        v = self.data[self.c:self.c+1]
        self.c += 1
        return struct.unpack('<B', v)[0]

    def read16(self):
        v = self.data[self.c:self.c+2]
        self.c += 2
        return struct.unpack('<H', v)[0]

    def read16i(self):
        v = self.data[self.c:self.c+2]
        self.c += 2
        return struct.unpack('<h', v)[0]

    def read32(self):
        v = self.data[self.c:self.c+4]
        self.c += 4
        return struct.unpack('<I', v)[0]

    def raw(self):
        return self.data[self.c:]

# BBBBBBBB BBBBBBBB BBBBBBBB BBBBBBBB BBBBBBBB BBBBBBBB BBBBBBBB BBBBBBBB
# XXXXXXXX XXXXXXXX XXXXX
#                        YYY YYYYYYYY YYYYYYYY YY
#                                                ZZZZZZ ZZZZZZZZ ZZZZZZZZ

def decode_sample(buffer):
    s = bitstring.BitString(buffer[:8])
    return s.unpack('int:21,int:21,int:21')

def decode_frame(frame):
    buffer = BufferPointer(frame)
    msg = {}

    buffer.skip_byte()
    msg['last_command_id'] = buffer.read16()
    msg['num_samples'] = buffer.read8()

    # Next is the number of samples since start, excluding the samples contained in this packet
    # nb_samples_since_start
    buffer.skip_byte(2)
    msg['temperature'] = buffer.read16()
    msg['timestamp'] = buffer.read32()

    # Second sample value is junk (outdated/uninitialized) value if num_samples < 2. */ LOGI("samples %02X", msg['num_samples'])
    msg['num_samples'] = min(msg['num_samples'], 2)

    msg['samples'] = []
    for i in range(msg['num_samples']):
        sample = {}

        sample['accel'] = decode_sample(buffer.raw())
        buffer.skip_byte(8)

        sample['gyro'] = decode_sample(buffer.raw())
        buffer.skip_byte(8)

        msg['samples'].append(sample)

    # Skip empty samples
    buffer.skip_byte((2 - msg['num_samples']) * 16)

    msg['mag'] = (buffer.read16i(), buffer.read16i(), buffer.read16i())

    return msg
