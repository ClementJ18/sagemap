from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class StandingWaterArea:
    asset_name = "StandingWaterArea"

    unique_id: int
    name: str
    layer_name: str | None
    uv_scroll_speed: float
    use_adaptive_blending: bool
    bump_map_texture: str
    sky_texture: str
    points: list[tuple[float, float]]
    water_height: int
    fx_shader: str
    depth_color: str

    @classmethod
    def parse(cls, context: "ParsingContext"):
        unique_id = context.stream.readUInt32()
        name = context.stream.readUInt16PrefixedAsciiString()
        layer_name = context.stream.readUInt16PrefixedAsciiString()
        uv_scroll_speed = context.stream.readFloat()
        use_adaptive_blending = context.stream.readBool()
        bump_map_texture = context.stream.readUInt16PrefixedAsciiString()
        sky_texture = context.stream.readUInt16PrefixedAsciiString()

        point_count = context.stream.readUInt32()
        points = []
        for _ in range(point_count):
            points.append(context.stream.readVector2())

        water_height = context.stream.readUInt32()
        fx_shader = context.stream.readUInt16PrefixedAsciiString()
        depth_color = context.stream.readUInt16PrefixedAsciiString()

        return cls(
            unique_id=unique_id,
            name=name,
            layer_name=layer_name,
            uv_scroll_speed=uv_scroll_speed,
            use_adaptive_blending=use_adaptive_blending,
            bump_map_texture=bump_map_texture,
            sky_texture=sky_texture,
            points=points,
            water_height=water_height,
            fx_shader=fx_shader,
            depth_color=depth_color,
        )


@dataclass
class StandingWaterAreas:
    asset_name = "StandingWaterAreas"

    version: int
    areas: list[StandingWaterArea]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            area_count = context.stream.readUInt32()
            areas = []

            for _ in range(area_count):
                areas.append(StandingWaterArea.parse(context))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(asset_ctx.version, areas, start_pos=asset_ctx.start_pos, end_pos=asset_ctx.end_pos)
