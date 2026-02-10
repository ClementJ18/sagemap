import logging
from contextlib import contextmanager
from dataclasses import dataclass
from enum import IntEnum
from typing import Iterator, TypedDict

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


@dataclass
class AssetContext:
    version: int
    datasize: int
    start_pos: int
    end_pos: int


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
    def read_asset(self) -> Iterator[AssetContext]:
        version, datasize = self.parse_asset_header()
        start_pos = self.stream.tell()

        asset_context = AssetContext(version, datasize, start_pos, start_pos + datasize)

        yield asset_context

        if asset_context.end_pos - asset_context.start_pos != asset_context.datasize:
            raise ValueError(
                f"Asset data size mismatch: expected {asset_context.datasize} bytes, read {asset_context.end_pos - asset_context.start_pos} bytes"
            )


class WritingContext:
    def __init__(self, stream: BinaryStream):
        self.stream = stream
        self.assets = {}
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        self.assets_by_index = {}
        self.index_by_asset = {}

    def set_asset_list(self, asset_list):
        self.assets_by_index = {i + 1: name for i, name in enumerate(asset_list)}
        self.index_by_asset = {name: i + 1 for i, name in enumerate(asset_list)}

    def add_asset(self, asset_name: str) -> int:
        if asset_name in self.index_by_asset:
            return self.index_by_asset[asset_name]
        
        index = len(self.assets_by_index) + 1
        self.assets_by_index[index] = asset_name
        self.index_by_asset[asset_name] = index

        return index
    
    def dict_to_properties(self, properties: dict[str, Property]) -> list[tuple[str, AssetPropertyType, str | int | float | bool]]:
        result = []
        for name, prop in properties.items():
            if name != prop["name"]:
                raise ValueError(f"Property name mismatch: key '{name}' does not match property name '{prop['name']}'")
            result.append((prop["name"], prop["type"], prop["value"]))
        return result
    
    def write_properties(self, properties: list[tuple[str, AssetPropertyType, str | int | float | bool]]):
        self.stream.writeUInt16(len(properties))
        for name, ptype, value in properties:
            asset_name_index = self.add_asset(name)
            self.stream.writeUChar(ptype.value)
            self.stream.writeUInt24(asset_name_index)

            if ptype == AssetPropertyType.Boolean:
                self.stream.writeBool(value)
            elif ptype == AssetPropertyType.Integer:
                self.stream.writeInt32(value)
            elif ptype == AssetPropertyType.RealNumber:
                self.stream.writeFloat(value)
            elif ptype in (AssetPropertyType.AsciiString, AssetPropertyType.Unknown):
                self.stream.writeUInt16PrefixedAsciiString(value)
            elif ptype == AssetPropertyType.UnicodeString:
                self.stream.writeUInt16PrefixedUnicodeString(value)
            else:
                raise ValueError(f"Unexpected property type: {ptype}")
            
    def write_asset_name(self, asset_name: str):
        asset_index = self.add_asset(asset_name)
        self.stream.writeUInt32(asset_index)

    def write_asset_property_key(self, property_key: tuple[AssetPropertyType, int, str]):
        property_key_type, property_key_name_index, _ = property_key
        self.stream.writeUChar(property_key_type.value)
        self.stream.writeUInt24(property_key_name_index)

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
