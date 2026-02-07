from map_parser.context import ParsingContext


from dataclasses import dataclass


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