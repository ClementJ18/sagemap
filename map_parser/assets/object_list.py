from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext, Property


@dataclass
class Object:
    asset_name = "Object"

    version: int
    position: tuple[float, float, float]
    angle: float
    road_type: int
    type_name: str
    properties: dict[str, "Property"]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()
        position = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())
        angle = context.stream.readFloat()
        road_type = context.stream.readUInt32()
        type_name = context.stream.readUInt16PrefixedAsciiString()
        properties = context.properties_to_dict(context.parse_properties())

        context.logger.debug(
            f"Object: Position: {position}, Angle: {angle}, Road Type: {road_type}, Type Name: {type_name}, Properties: {properties}"
        )
        return cls(version, position, angle, road_type, type_name, properties)


@dataclass
class ObjectsList:
    asset_name = "ObjectsList"

    version: int
    object_list: list[Object]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, datasize = context.parse_asset_header()
        object_list = []
        end_pos = context.stream.tell() + datasize
        while context.stream.tell() < end_pos:
            asset_name = context.parse_asset_name()
            if asset_name != Object.asset_name:
                raise ValueError(f"Expected {Object.asset_name} asset, got {asset_name}")

            object_list.append(Object.parse(context))

        context.logger.debug(f"Parsed {len(object_list)} objects in ObjectsList asset")
        return cls(version, object_list)
