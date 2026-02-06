from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class EnvironmentData:
    asset_name = "EnvironmentData"

    version: int
    water_max_alpha_depth: float | None
    deep_water_alpha: float | None
    is_macro_texture_stretched: bool | None
    macro_texture: str
    cloud_texture: str
    unknown_texture: str | None
    unknown_texture2: str | None

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, datasize = context.parse_asset_header()
        end_pos = context.stream.base_stream.tell() + datasize

        water_max_alpha_depth = None
        deep_water_alpha = None
        if version >= 3:
            water_max_alpha_depth = context.stream.readFloat()
            deep_water_alpha = context.stream.readFloat()

        is_macro_texture_stretched = None
        if version < 5:
            is_macro_texture_stretched = context.stream.readBool()

        macro_texture = context.stream.readUInt16PrefixedAsciiString()
        cloud_texture = context.stream.readUInt16PrefixedAsciiString()

        unknown_texture = None
        if version >= 4:
            unknown_texture = context.stream.readUInt16PrefixedAsciiString()

        unknown_texture2 = None
        if version >= 6 and context.stream.base_stream.tell() < end_pos:
            unknown_texture2 = context.stream.readUInt16PrefixedAsciiString()

        return cls(
            version,
            water_max_alpha_depth,
            deep_water_alpha,
            is_macro_texture_stretched,
            macro_texture,
            cloud_texture,
            unknown_texture,
            unknown_texture2,
        )
