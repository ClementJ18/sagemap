import io
import struct


class BinaryStream:
    def __init__(self, base_stream, encoding='latin-1'):
        self.base_stream: io.BytesIO = base_stream
        self.encoding = encoding

    def readByte(self) -> bytes:
        return self.base_stream.read(1)
    
    def writeByte(self, value: int):
        self.base_stream.write(bytes([value]))

    def readBytes(self, length) -> bytes:
        return self.base_stream.read(length)
    
    def writeBytes(self, value: bytes):
        self.base_stream.write(value)

    def readChar(self) -> int:
        return self.unpack('b')
    
    def writeChar(self, value: bytes):
        self.pack('c', value)

    def readUChar(self) -> int:
        return self.unpack('B')
    
    def writeUChar(self, value: int):
        self.pack('C', value)

    def readBool(self) -> bool:
        return self.unpack('?')
    
    def writeBool(self, value: bool):
        self.pack('?', value)
    
    def readBoolUInt32(self) -> bool:
        result = self.readBool()
        unused = self.readUInt24()  # padding

        if unused != 0:
            raise ValueError("Expected padding bytes to be zero")
        
        return result
    
    def writeBoolUInt32(self, value: bool):
        self.writeBool(value)
        self.writeUInt24(0)

    def readInt16(self) -> int:
        return self.unpack('h', 2)
    
    def writeInt16(self, value: int):
        self.pack('h', value)

    def readUInt16(self) -> int:
        return self.unpack('H', 2)
    
    def writeUInt16(self, value: int):
        self.pack('H', value)

    def readInt32(self) -> int:
        return self.unpack('i', 4)
    
    def writeInt32(self, value: int):
        self.pack('i', value)

    def readUInt32(self) -> int:
        return self.unpack('I', 4)
    
    def writeUInt32(self, value: int):
        self.pack('I', value)

    def readInt64(self) -> int:
        return self.unpack('q', 8)
    
    def writeInt64(self, value: int):
        self.pack('q', value)

    def readUInt64(self) -> int:
        return self.unpack('Q', 8)
    
    def writeUInt64(self, value: int):
        self.pack('Q', value)

    def readFloat(self) -> float:
        return self.unpack('f', 4)
    
    def writeFloat(self, value: float):
        self.pack('f', value)

    def readDouble(self) -> float:
        return self.unpack('d', 8)
    
    def writeDouble(self, value: float):
        self.pack('d', value)

    def readString(self) -> str:
        length = self.readUChar()
        return self.unpack(str(length) + 's', length).decode(self.encoding)
    
    def writeString(self, value: str):
        length = len(value)
        self.writeUChar(length)
        self.pack(str(length) + 's', value.encode(self.encoding))
    
    def readUInt16PrefixedAsciiString(self) -> str:
        lenght = self.readUInt16()
        return self.readBytes(lenght).decode(self.encoding)
    
    def writeUInt16PrefixedAsciiString(self, value: str):
        lenght = len(value)
        self.writeUInt16(lenght)
        self.writeBytes(value.encode(self.encoding))
    
    def readFourCc(self) -> str:
        return self.readBytes(4).decode(self.encoding)
    
    def writeFourCc(self, value: str):
        if len(value) != 4:
            raise ValueError("FourCC must be exactly 4 characters")
        self.writeBytes(value.encode(self.encoding))
    
    def readUInt24(self) -> int:
        b = self.readBytes(3)
        return int.from_bytes(b, "little", signed=False)
    
    def writeUInt24(self, value: int):
        if not (0 <= value <= 0xFFFFFF):
            raise ValueError("Value out of range for UInt24 (0..16777215)")
        b = value.to_bytes(3, "little")
        self.writeBytes(b)

    
    def readUInt16PrefixedUnicodeString(self) -> str:
        length = self.readUInt16()
        return self.readBytes(length * 2).decode("utf-16-le")
    
    def writeUInt16PrefixedUnicodeString(self, value: str):
        encoded = value.encode("utf-16-le")
        self.writeUInt16(len(value))
        self.writeBytes(encoded)
    
    def readUInt16Array2D(self, width: int, height: int) -> list[list[int]]:
        result = [[0] * height for _ in range(width)]
        for y in range(height):
            for x in range(width):
                result[x][y] = self.readUInt16()
        return result
    
    def writeUInt16Array2D(self, array2d: list[list[int]], width: int, height: int):
        for y in range(height):
            for x in range(width):
                self.writeUInt16(array2d[x][y])

    def readSingle(self):
        return self.unpack('f', 4)
    
    def writeSingle(self, value: float):
        self.pack('f', value)

    def pack(self, fmt, data):
        return self.writeBytes(struct.pack(fmt, data))

    def unpack(self, fmt, length = 1):
        return struct.unpack(fmt, self.readBytes(length))[0] 
