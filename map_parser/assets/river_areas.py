from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class RiverArea:
    asset_name = "RiverArea"

    unique_id: int
    name: str
    layer_name: str
    uv_scroll_speed: float
    use_additive_blending: bool
    river_texture: str
    noise_texture: str
    alpha_edge_texture: str
    sparkle_texture: str
    color: tuple[int, int, int]
    alpha: float
    water_height: int
    river_type: str | None
    minimum_water_lod: str
    lines: list[tuple[tuple[float, float], tuple[float, float]]]

    @classmethod
    def parse(cls, context: "ParsingContext", version: int):
        unique_id = context.stream.readUInt32()
        name = context.stream.readUInt16PrefixedAsciiString()
        layer_name = context.stream.readUInt16PrefixedAsciiString()
        uv_scroll_speed = context.stream.readSingle()
        use_additive_blending = context.stream.readBool()
        river_texture = context.stream.readUInt16PrefixedAsciiString()
        noise_texture = context.stream.readUInt16PrefixedAsciiString()
        alpha_edge_texture = context.stream.readUInt16PrefixedAsciiString()
        sparkle_texture = context.stream.readUInt16PrefixedAsciiString()
        color = (context.stream.readUChar(), context.stream.readUChar(), context.stream.readUChar())

        unused_color_a = context.stream.readUChar()
        if unused_color_a != 0:
            raise ValueError(f"Expected unused color alpha to be 0, got {unused_color_a}")

        alpha = context.stream.readSingle()
        water_height = context.stream.readUInt32()

        river_type = None
        if version >= 3:
            river_type = context.stream.readUInt16PrefixedAsciiString()

        minimum_water_lod = context.stream.readUInt16PrefixedAsciiString()

        lines_count = context.stream.readUInt32()
        lines = []

        for _ in range(lines_count):
            lines.append((context.stream.readVector2(), context.stream.readVector2()))

        return cls(
            unique_id=unique_id,
            name=name,
            layer_name=layer_name,
            uv_scroll_speed=uv_scroll_speed,
            use_additive_blending=use_additive_blending,
            river_texture=river_texture,
            noise_texture=noise_texture,
            alpha_edge_texture=alpha_edge_texture,
            sparkle_texture=sparkle_texture,
            color=color,
            alpha=alpha,
            water_height=water_height,
            river_type=river_type,
            minimum_water_lod=minimum_water_lod,
            lines=lines,
        )


@dataclass
class RiverAreas:
    asset_name = "RiverAreas"

    version: int
    areas: list[RiverArea]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, _):
            river_area_count = context.stream.readUInt32()
            areas = []
            for _ in range(river_area_count):
                areas.append(RiverArea.parse(context, version))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(version, areas)
