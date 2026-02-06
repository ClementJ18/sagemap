from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class WaterSettings:
    asset_name = "GlobalWaterSettings"

    version: int
    reflection_on: bool
    reflection_plane_z: float

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()
        reflection_on = context.stream.readBool()
        reflection_plane_z = context.stream.readSingle()

        context.logger.debug(
            f"Parsed GlobalWaterSettings asset, version: {version}, Reflection On: {reflection_on}, Reflection Plane Z: {reflection_plane_z}"
        )
        return cls(version, reflection_on, reflection_plane_z)
