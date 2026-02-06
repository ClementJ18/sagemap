from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext, Property


@dataclass
class WorldInfo:
    asset_name = "WorldInfo"

    version: int
    properties: dict[str, "Property"]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()

        context.logger.debug(f"Parsing WorldInfo asset, version: {version}")
        return cls(version, context.properties_to_dict(context.parse_properties()))


@dataclass
class SkippedAsset:
    asset_name = "SkippedAsset"

    version: int
    datasize: int
    data: bytes
    name: str

    @classmethod
    def parse(cls, context: "ParsingContext", name: str):
        version = context.stream.readUInt16()
        datasize = context.stream.readUInt32()
        data = context.stream.readBytes(datasize)

        context.logger.debug(f"Skipped asset: {name}, Version: {version}, Data Size: {datasize} bytes")
        return cls(version, datasize, data, name)


@dataclass
class BlendTileData(SkippedAsset):
    asset_name = "BlendTileData"


@dataclass
class GlobalVersion(SkippedAsset):
    asset_name = "GlobalVersion"


@dataclass
class WaypointsList:
    asset_name = "WaypointsList"

    version: int
    waypoint_paths: list[tuple[int, int]]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()
        waypoint_paths = []
        waypoint_count = context.stream.readUInt32()
        for _ in range(waypoint_count):
            start_waypoint_id = context.stream.readUInt32()
            end_waypoint_id = context.stream.readUInt32()

            waypoint_paths.append((start_waypoint_id, end_waypoint_id))

        return cls(version, waypoint_paths)


@dataclass
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
