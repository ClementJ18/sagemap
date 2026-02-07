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
        version, _ = context.parse_asset_header()

        teams = []
        team_count = context.stream.readUInt32()
        for _ in range(team_count):
            teams.append(Team.parse(context))

        context.logger.debug(f"Parsed {len(teams)} teams in Teams asset (v{version})")
        return cls(version=version, teams=teams)