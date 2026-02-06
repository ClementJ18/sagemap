from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class StandingWaveArea:
    asset_name = "StandingWaveArea"

    unique_id: int
    name: str
    layer_name: str | None
    uv_scroll_speed: float
    use_adaptive_blending: bool
    points: list[tuple[float, float]]
    final_width: int | None
    final_height: int | None
    initial_width_fraction: int | None
    initial_height_fraction: int | None
    initial_velocity: int | None
    time_to_fade: int | None
    time_to_compress: int | None
    time_offset_2nd_wave: int | None
    distance_from_shore: int | None
    texture: str | None
    enable_pca_wave: bool | None
    wave_particle_fx_name: str | None


    @classmethod
    def parse(cls, context: "ParsingContext", version: int):
        unique_id = context.stream.readUInt32()
        name = context.stream.readUInt16PrefixedAsciiString()
        layer_name = context.stream.readUInt16PrefixedAsciiString()
        uv_scroll_speed = context.stream.readSingle()
        use_adaptive_blending = context.stream.readBool()

        point_count = context.stream.readUInt32()
        points = []
        for _ in range(point_count):
            points.append((context.stream.readSingle(), context.stream.readSingle()))

        unknown = context.stream.readUInt32()
        if unknown != 0:
            raise ValueError(f"Expected unknown field to be 0, got {unknown}")
        
        final_width = None
        final_height = None
        initial_width_fraction = None
        initial_height_fraction = None
        initial_velocity = None
        time_to_fade = None
        time_to_compress = None
        time_offset_2nd_wave = None
        distance_from_shore = None
        texture = None
        if version < 3:
            final_width = context.stream.readUInt32()
            final_height = context.stream.readUInt32()
            initial_width_fraction = context.stream.readUInt32()
            initial_height_fraction = context.stream.readUInt32()
            initial_velocity = context.stream.readUInt32()
            time_to_fade = context.stream.readUInt32()
            time_to_compress = context.stream.readUInt32()
            time_offset_2nd_wave = context.stream.readUInt32()
            distance_from_shore = context.stream.readUInt32()
            texture = context.stream.readUInt16PrefixedAsciiString()


        enable_pca_wave = None
        if version == 2:
            enable_pca_wave = context.stream.readBool()

        wave_particle_fx_name = None
        if version >= 4:
            wave_particle_fx_name = context.stream.readUInt16PrefixedAsciiString()

        return cls(
            unique_id=unique_id,
            name=name,
            layer_name=layer_name,
            uv_scroll_speed=uv_scroll_speed,
            use_adaptive_blending=use_adaptive_blending,
            points=points,
            final_width=final_width,
            final_height=final_height,
            initial_width_fraction=initial_width_fraction,
            initial_height_fraction=initial_height_fraction,
            initial_velocity=initial_velocity,
            time_to_fade=time_to_fade,
            time_to_compress=time_to_compress,
            time_offset_2nd_wave=time_offset_2nd_wave,
            distance_from_shore=distance_from_shore,
            texture=texture,
            enable_pca_wave=enable_pca_wave,
            wave_particle_fx_name=wave_particle_fx_name
        )



@dataclass
class StandingWaveAreas:
    asset_name = "StandingWaveAreas"

    version: int
    areas: list[StandingWaveArea]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()
        area_count = context.stream.readUInt32()
        areas = []
        
        for _ in range(area_count):
            areas.append(StandingWaveArea.parse(context, version))

        context.logger.debug(f"Parsed StandingWaveAreas with {len(areas)} areas")
        return cls(version=version, areas=areas)