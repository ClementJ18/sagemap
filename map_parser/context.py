import logging
from contextlib import contextmanager
from enum import IntEnum
from typing import TypedDict

from .stream import BinaryStream


class AssetPropertyType(IntEnum):
    Boolean = 0
    Integer = 1
    RealNumber = 2
    AsciiString = 3
    UnicodeString = 4
    Unknown = 5


class Property(TypedDict):
    name: str
    type: AssetPropertyType
    value: str | int | float | bool


class ParsingContext:
    def __init__(self, stream: BinaryStream):
        self.stream = stream
        self.assets = {}

        self.compression_bytes = None
        self.asset_count = None

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    def set_logger(self, logger):
        self.logger = logger

    def parse_properties(self):
        properties = []
        property_count = self.stream.readUInt16()
        for _ in range(property_count):
            properties.append(self.parse_asset_property())

        return properties

    def parse_asset_property_key(self):
        property_key_byte = self.stream.readUChar()
        property_key_type = AssetPropertyType(property_key_byte)
        property_key_name_index = self.stream.readUInt24()
        property_key_name = self.assets.get(property_key_name_index)

        return property_key_type, property_key_name_index, property_key_name

    def properties_to_dict(self, properties) -> dict[str, Property]:
        result = {}
        for name, ptype, value in properties:
            if name in result:
                raise ValueError(f"Duplicate property name detected: {name}")
            result[name] = Property(name=name, type=ptype, value=value)
        return result

    def parse_asset_property(self):
        property_key_type, property_key_name_index, property_key_name = self.parse_asset_property_key()
        if property_key_type == AssetPropertyType.Boolean:
            value = self.stream.readBool()
        elif property_key_type == AssetPropertyType.Integer:
            value = self.stream.readInt32()
        elif property_key_type == AssetPropertyType.RealNumber:
            value = self.stream.readFloat()
        elif property_key_type in (AssetPropertyType.AsciiString, AssetPropertyType.Unknown):
            value = self.stream.readUInt16PrefixedAsciiString()
        elif property_key_type == AssetPropertyType.UnicodeString:
            value = self.stream.readUInt16PrefixedUnicodeString()
        else:
            raise ValueError(f"Unexpected property type: {property_key_type}")

        self.logger.debug(
            f"Property: {property_key_name} (Index: {property_key_name_index}), Type: {property_key_type.name}, Value: {value}"
        )
        return (property_key_name, property_key_type, value)

    def parse_assets(self):
        self.compression_bytes = self.stream.readFourCc()
        self.asset_count = self.stream.readUInt32()

        self.assets = {}
        for i in range(self.asset_count, 0, -1):
            asset_name = self.stream.readString()
            asset_index = self.stream.readUInt32()
            if asset_index != i:
                raise ValueError(f"Invalid asset index: expected {i}, got {asset_index}")

            self.assets[asset_index] = asset_name

        return self.assets

    def parse_asset_name(self):
        asset_index = self.stream.readUInt32()
        asset_name = self.assets[asset_index]
        self.logger.debug(f"Parsing asset: {asset_name} (Index: {asset_index})")
        return asset_name

    def parse_asset_header(self):
        asset_version = self.stream.readUInt16()
        datasize = self.stream.readUInt32()
        return asset_version, datasize
    
    @contextmanager
    def read_asset(self):
        version, datasize = self.parse_asset_header()
        start_pos = self.stream.tell()

        yield version, datasize

        end_pos = self.stream.tell()
        if end_pos - start_pos != datasize:
            raise ValueError(f"Asset data size mismatch: expected {datasize} bytes, read {end_pos - start_pos} bytes")
        
    
    
class WritingContext:
    def __init__(self, stream: BinaryStream):
        self.stream = stream
        self.assets = {}
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    @contextmanager
    def write_asset(self, asset_name: str, version: int):
        self.logger.debug(f"Writing asset: {asset_name}, Version: {version}")
        self.stream.writeUInt16(version)
        data_size_position = self.stream.tell()
        self.stream.writeUInt32(0)
        data_position = self.stream.tell()

        yield

        end_position = self.stream.tell()
        data_size = end_position - data_position
        self.stream.seek(data_size_position)
        self.stream.writeUInt32(data_size)
        self.stream.seek(end_position)