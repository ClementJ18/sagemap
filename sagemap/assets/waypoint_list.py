from dataclasses import dataclass

from sagemap.context import ParsingContext


@dataclass
class WaypointsList:
    asset_name = "WaypointsList"

    version: int
    waypoint_paths: list[tuple[int, int]]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, _):
            waypoint_paths = []
            waypoint_count = context.stream.readUInt32()
            for _ in range(waypoint_count):
                start_waypoint_id = context.stream.readUInt32()
                end_waypoint_id = context.stream.readUInt32()

                waypoint_paths.append((start_waypoint_id, end_waypoint_id))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(version, waypoint_paths)
