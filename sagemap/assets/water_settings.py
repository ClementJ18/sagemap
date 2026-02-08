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
        with context.read_asset() as (version, _):
            reflection_on = context.stream.readBool()
            reflection_plane_z = context.stream.readSingle()

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(version, reflection_on, reflection_plane_z)
