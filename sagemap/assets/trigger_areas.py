from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class TriggerArea:
    asset_name = "TriggerArea"

    name: str
    layer_name: str
    area_id: int
    points: list[tuple[float, float]]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        name = context.stream.readUInt16PrefixedAsciiString()
        layer_name = context.stream.readUInt16PrefixedAsciiString()
        area_id = context.stream.readUInt32()

        point_count = context.stream.readUInt32()
        points = []
        for _ in range(point_count):
            points.append(context.stream.readVector2())

        unknown2 = context.stream.readUInt32()
        if unknown2 != 0:
            raise ValueError("Invalid data in 'unknown2'")

        return cls(name, layer_name, area_id, points)


@dataclass
class TriggerAreas:
    asset_name = "TriggerAreas"

    version: int
    trigger_areas: list[TriggerArea]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            trigger_areas = []
            area_count = context.stream.readUInt32()
            for _ in range(area_count):
                trigger_areas.append(TriggerArea.parse(context))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(asset_ctx.version, trigger_areas, start_pos=asset_ctx.start_pos, end_pos=asset_ctx.end_pos)
