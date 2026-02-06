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
            points.append((context.stream.readFloat(), context.stream.readFloat()))

        unknown2 = context.stream.readUInt32()
        if unknown2 != 0:
            raise ValueError("Invalid data in 'unknown2'")

        return cls(name, layer_name, area_id, points)


@dataclass
class TriggerAreas:
    asset_name = "TriggerAreas"

    version: int
    trigger_areas: list[TriggerArea]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()
        trigger_areas = []
        area_count = context.stream.readUInt32()
        for _ in range(area_count):
            trigger_areas.append(TriggerArea.parse(context))

        return cls(version, trigger_areas)
