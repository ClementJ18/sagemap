from dataclasses import dataclass

from sagemap.context import ParsingContext, Property


@dataclass
class WorldInfo:
    asset_name = "WorldInfo"

    version: int
    properties: dict[str, "Property"]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, _):
            properties = context.properties_to_dict(context.parse_properties())

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(version, properties)
