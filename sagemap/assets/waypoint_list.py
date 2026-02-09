from dataclasses import dataclass

from sagemap.context import ParsingContext


@dataclass
class WaypointsList:
    asset_name = "WaypointsList"

    version: int
    waypoint_paths: list[tuple[int, int]]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            waypoint_paths = []
            waypoint_count = context.stream.readUInt32()
            for _ in range(waypoint_count):
                start_waypoint_id = context.stream.readUInt32()
                end_waypoint_id = context.stream.readUInt32()

                waypoint_paths.append((start_waypoint_id, end_waypoint_id))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(asset_ctx.version, waypoint_paths, start_pos=asset_ctx.start_pos, end_pos=asset_ctx.end_pos)
