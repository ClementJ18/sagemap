from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class HeightMapData:
    asset_name = "HeightMapData"

    version: int
    width: int
    height: int
    border_width: int
    borders: list[dict[str, tuple[int, int]]]
    area: int
    min_height: int
    max_height: int
    elevations: list[list[int]]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            width = context.stream.readUInt32()
            height = context.stream.readUInt32()
            border_width = context.stream.readUInt32()

            border_count = context.stream.readUInt32()
            borders = []
            for _ in range(border_count):
                if asset_ctx.version >= 6:
                    corner1X = context.stream.readUInt32()
                    corner1Y = context.stream.readUInt32()
                    x = context.stream.readUInt32()
                    y = context.stream.readUInt32()
                else:
                    corner1X = 0
                    corner1Y = 0
                    x = context.stream.readUInt32()
                    y = context.stream.readUInt32()

                borders.append({"corner1": (corner1X, corner1Y), "position": (x, y)})

            area = context.stream.readUInt32()
            if area != width * height:
                raise ValueError(f"Invalid area: {area}, expected: {width * height}")

            min_height = None
            max_height = None
            elevations = [[0 for _ in range(width)] for _ in range(height)]
            for y in range(height):
                for x in range(width):
                    if asset_ctx.version >= 5:
                        elevation = context.stream.readUInt16()
                    else:
                        elevation = context.stream.readUChar()
                    elevations[y][x] = elevation
                    if min_height is None or elevation < min_height:
                        min_height = elevation
                    if max_height is None or elevation > max_height:
                        max_height = elevation

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(
            asset_ctx.version,
            width,
            height,
            border_width,
            borders,
            area,
            min_height,
            max_height,
            elevations,
            asset_ctx.start_pos,
            asset_ctx.end_pos,
        )
