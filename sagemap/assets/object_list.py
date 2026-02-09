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
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            position = context.stream.readVector3()
            angle = context.stream.readFloat()
            road_type = context.stream.readUInt32()
            type_name = context.stream.readUInt16PrefixedAsciiString()
            properties = context.properties_to_dict(context.parse_properties())

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(
            asset_ctx.version,
            position,
            angle,
            road_type,
            type_name,
            properties,
            start_pos=asset_ctx.start_pos,
            end_pos=asset_ctx.end_pos,
        )


@dataclass
class ObjectsList:
    asset_name = "ObjectsList"

    version: int
    object_list: list[Object]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            object_list = []
            while context.stream.tell() < asset_ctx.end_pos:
                asset_name = context.parse_asset_name()
                if asset_name != Object.asset_name:
                    raise ValueError(f"Expected {Object.asset_name} asset, got {asset_name}")

                object_list.append(Object.parse(context))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(asset_ctx.version, object_list, start_pos=asset_ctx.start_pos, end_pos=asset_ctx.end_pos)
