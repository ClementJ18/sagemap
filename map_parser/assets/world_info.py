from map_parser.context import ParsingContext, Property


from dataclasses import dataclass


@dataclass
class WorldInfo:
    asset_name = "WorldInfo"

    version: int
    properties: dict[str, "Property"]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, _):
            properties = context.properties_to_dict(context.parse_properties())

        context.logger.debug(f"Parsed WorldInfo asset, version: {version}")
        return cls(version, properties)
    