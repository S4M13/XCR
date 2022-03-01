import struct
from enum import Enum
from math import floor, sin

from bitarray import bitarray


def rotate_left(x, n):
    return (x << n) | (x >> (32 - n))

def modular_add(a, b):
    return (a + b) % pow(2, 32)


class MD5:

    initial_buffers = {
        'A': 0x67452301,
        'B': 0xEFCDAB89,
        'C': 0x98BADCFE,
        'D': 0x10325476,
    }


    def __init__(self, message: str):
        self.message = message

        self.buffers = {
            'A': None,
            'B': None,
            'C': None,
            'D': None,
        }

        self.preprocessed = MD5._preparation(message)
        self._load_buffers()
        self._digest_buffers()
        self._compute_digest()



    @classmethod
    def _preparation(cls, message):
        padded = bitarray(endian="big")
        padded.frombytes(message.encode("utf-8"))

        padded.append(1)
        while len(padded) % 512 != 448:
            padded.append(0)

        padded = bitarray(padded, endian="little")

        length = (len(message) * 8) % (2**64)
        length_padded = bitarray(endian="little")
        length_padded.frombytes(struct.pack("<Q", length))

        padded.extend(length_padded)

        return padded


    def _load_buffers(self):
        self.buffers = MD5.initial_buffers.copy()


    def _digest_buffers(self):
        F = lambda x, y, z: (x & y) | (~x & z)
        G = lambda x, y, z: (x & z) | (y & ~z)
        H = lambda x, y, z: x ^ y ^ z
        I = lambda x, y, z: y ^ (x | ~z)

        T = [floor(pow(2, 32) * abs(sin(i + 1))) for i in range(64)]

        number = len(self.preprocessed) // 32

        A = self.buffers['A']
        B = self.buffers['B']
        C = self.buffers['C']
        D = self.buffers['D']

        for chunk_index in range(number // 16):
            st = chunk_index * 512

            M = [self.preprocessed[st + (x*32) : st + (x*32) + 32] for x in range(16)]
            M = [int.from_bytes(word.tobytes(), byteorder="little") for word in M]

            for i in range(4 * 16):
                if 0 <= i <= 15:
                    s = [7, 12, 17, 22]
                    _ = F(B, C, D)

                    k = i
                elif 16 <= i <= 31:
                    s = [5, 9, 14, 20]
                    _ = G(B, C, D)

                    k = ((5 * i) + 1) % 16
                elif 32 <= i <= 47:
                    s = [4, 11, 16, 23]
                    _ = H(B, C, D)

                    k = ((3*i) + 5) % 16
                elif 48 <= i <= 63:
                    s = [6, 10, 15, 21]
                    _ = I(B, C, D)

                    k = (7*i) % 16

                temp = modular_add(_, M[k])
                temp = modular_add(temp, T[i])
                temp = modular_add(temp, A)
                temp = rotate_left(temp, s[i%4])
                temp = modular_add(temp, B)

                A = D
                D = C
                C = B
                B = temp

            self.buffers['A'] = modular_add(self.buffers['A'], A)
            self.buffers['B'] = modular_add(self.buffers['B'], B)
            self.buffers['C'] = modular_add(self.buffers['C'], C)
            self.buffers['D'] = modular_add(self.buffers['D'], D)


    def _compute_digest(self):
        A = struct.unpack("<I", struct.pack(">I", self.buffers['A']))[0]
        B = struct.unpack("<I", struct.pack(">I", self.buffers['B']))[0]
        C = struct.unpack("<I", struct.pack(">I", self.buffers['C']))[0]
        D = struct.unpack("<I", struct.pack(">I", self.buffers['D']))[0]

        self.digest = format(A, '08x') + format(B, '08x') + format(C, '08x') + format(D, '08x')
