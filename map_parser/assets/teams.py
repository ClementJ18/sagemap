from map_parser.context import ParsingContext, Property


from dataclasses import dataclass


@dataclass
class Team:
    properties: dict[str, "Property"]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        properties = context.properties_to_dict(context.parse_properties())
        context.logger.debug(f"Parsed Team with properties: {properties}")
        return cls(properties=properties)


@dataclass
class Teams:
    asset_name = "Teams"

    version: int
    teams: list[Team]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, _):
            teams = []
            team_count = context.stream.readUInt32()
            for _ in range(team_count):
                teams.append(Team.parse(context))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(version=version, teams=teams)