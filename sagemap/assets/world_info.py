from dataclasses import dataclass

from sagemap.context import ParsingContext, Property


@dataclass
class WorldInfo:
    asset_name = "WorldInfo"

    version: int
    properties: dict[str, "Property"]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            properties = context.properties_to_dict(context.parse_properties())

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(asset_ctx.version, properties, start_pos=asset_ctx.start_pos, end_pos=asset_ctx.end_pos)
