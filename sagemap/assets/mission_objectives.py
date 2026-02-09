from dataclasses import dataclass
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext

class MissionObjectiveType(enum.IntEnum):
    Attack = 0
    Unknown1 = 1
    Unknown2 = 2
    Build = 3
    Capture = 4
    Protect = 5

@dataclass
class MissionObjective:
    id: str
    text: str
    description: str
    is_bonus_objective: bool
    objective_type: MissionObjectiveType

    @classmethod
    def parse(cls, context: "ParsingContext"):
        id = context.stream.readUInt16PrefixedAsciiString()
        text = context.stream.readUInt16PrefixedAsciiString()
        description = context.stream.readUInt16PrefixedAsciiString()
        is_bonus_objective = context.stream.readBool()
        objective_type = MissionObjectiveType(context.stream.readUInt32())

        return cls(id=id, text=text, description=description, is_bonus_objective=is_bonus_objective, objective_type=objective_type)

@dataclass
class MissionObjectives:
    asset_name = "MissionObjectives"

    version: int
    objectives: list[MissionObjective]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            objective_count = context.stream.readUInt32()
            objectives = []
            for _ in range(objective_count):
                objectives.append(MissionObjective.parse(context))

            return cls(version=asset_ctx.version, objectives=objectives,
                       start_pos=asset_ctx.start_pos, end_pos=asset_ctx.end_pos)
