from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class ScriptArgument:
    type: int
    int_value: int | None = None
    float_value: float | None = None
    string_value: str | None = None
    position_value: tuple[float, float, float] | None = None

    @classmethod
    def parse(cls, context: "ParsingContext"):
        argument_type = context.stream.readUInt32()
        int_value = None
        float_value = None
        string_value = None
        position_value = None

        if argument_type == 16:  # Coordinate
            position_value = (
                context.stream.readFloat(),
                context.stream.readFloat(),
                context.stream.readFloat(),
            )
        else:
            int_value = context.stream.readInt32()
            float_value = context.stream.readFloat()
            string_value = context.stream.readUInt16PrefixedAsciiString()

        return cls(
            type=argument_type,
            int_value=int_value,
            float_value=float_value,
            string_value=string_value,
            position_value=position_value,
        )


@dataclass
class ScriptDerived:
    """Base class for ScriptAction and Condition"""

    content_type: int
    internal_name: str | None
    arguments: list[ScriptArgument]
    is_enabled: bool | None
    is_inverted: bool | None

    @classmethod
    def parse(
        cls,
        context: "ParsingContext",
        has_internal_name_version: int,
        has_is_enabled_version: int,
        has_is_inverted: bool,
    ):
        with context.read_asset() as (asset_version, _):
            content_type = context.stream.readUInt32()

            internal_name = None
            if asset_version >= has_internal_name_version:
                internal_name = context.parse_asset_property_key()

            num_arguments = context.stream.readUInt32()
            arguments = []
            for _ in range(num_arguments):
                arguments.append(ScriptArgument.parse(context))

            is_enabled = None
            is_inverted = None
            if asset_version >= has_is_enabled_version:
                is_enabled = context.stream.readBoolUInt32()

                if has_is_inverted:
                    is_inverted = context.stream.readBoolUInt32()

        context.logger.debug("Finished parsing ScriptDerived")
        return cls(
            content_type=content_type,
            internal_name=internal_name,
            arguments=arguments,
            is_enabled=is_enabled,
            is_inverted=is_inverted,
        )


@dataclass
class OrCondition:
    version: int
    conditions: list[ScriptDerived]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, datasize):
            conditions = []
            condition_end_pos = context.stream.tell() + datasize

            while context.stream.tell() < condition_end_pos:
                asset_name = context.parse_asset_name()
                if asset_name != "Condition":
                    raise ValueError(f"Expected Condition asset, got {asset_name}")

                condition = ScriptDerived.parse(context, 4, 5, True)
                conditions.append(condition)

        context.logger.debug("Finished parsing OrCondition")
        return cls(version=version, conditions=conditions)


@dataclass
class Script:
    name: str
    comment: str
    conditions_comment: str
    actions_comment: str
    is_active: bool
    deactivate_upon_success: bool
    active_in_easy: bool
    active_in_medium: bool
    active_in_hard: bool
    is_subroutine: bool
    evaluation_interval: int | None = None
    uses_evaluation_interval_type: bool = False
    evaluation_interval_type: int = 6
    actions_fire_sequentially: bool | None = None
    loop_actions: bool | None = None
    loop_count: int | None = None
    sequential_target_type: bool | None = None
    sequential_target_name: str | None = None
    unknown: str | None = None
    unknown2: int | None = None
    unknown3: int | None = None
    or_conditions: list[OrCondition] = field(default_factory=list)
    actions_if_true: list[ScriptDerived] = field(default_factory=list)
    actions_if_false: list[ScriptDerived] = field(default_factory=list)

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (asset_version, datasize):
            script_end_pos = context.stream.tell() + datasize

            name = context.stream.readUInt16PrefixedAsciiString()
            context.logger.info(f"Parsing script: {name}")
            comment = context.stream.readUInt16PrefixedAsciiString()
            conditions_comment = context.stream.readUInt16PrefixedAsciiString()
            actions_comment = context.stream.readUInt16PrefixedAsciiString()

            is_active = context.stream.readBool()
            deactivate_upon_success = context.stream.readBool()

            active_in_easy = context.stream.readBool()
            active_in_medium = context.stream.readBool()
            active_in_hard = context.stream.readBool()

            is_subroutine = context.stream.readBool()

            evaluation_interval = None
            uses_evaluation_interval_type = False
            evaluation_interval_type = 6
            if asset_version >= 2:
                evaluation_interval = context.stream.readUInt32()

                if asset_version == 5:
                    uses_evaluation_interval_type = context.stream.readBool()
                    evaluation_interval_type = context.stream.readUInt32()

            actions_fire_sequentially = None
            loop_actions = None
            loop_count = None
            sequential_target_type = None
            sequential_target_name = None
            if asset_version >= 3:
                actions_fire_sequentially = context.stream.readBool()
                loop_actions = context.stream.readBool()
                loop_count = context.stream.readInt32()
                sequential_target_type = context.stream.readBool()
                sequential_target_name = context.stream.readUInt16PrefixedAsciiString()

            unknown = None
            unknown2 = None
            unknown3 = None
            if asset_version >= 4:
                unknown = context.stream.readUInt16PrefixedAsciiString()
                if unknown not in ("ALL", "Planning", "X"):
                    raise ValueError("Invalid data in 'unknown'")

            if asset_version >= 6:
                unknown2 = context.stream.readInt32()
                unknown3 = context.stream.readUInt16()
                if unknown3 != 0:
                    raise ValueError("Invalid data in 'unknown3'")

            or_conditions = []
            actions_if_true = []
            actions_if_false = []
            while context.stream.tell() < script_end_pos:
                asset_name = context.parse_asset_name()
                if asset_name == "OrCondition":
                    or_conditions.append(OrCondition.parse(context))
                elif asset_name == "ScriptAction":
                    actions_if_true.append(ScriptDerived.parse(context, 2, 3, False))
                elif asset_name == "ScriptActionFalse":
                    actions_if_false.append(ScriptDerived.parse(context, 2, 3, False))
                else:
                    raise ValueError(f"Unexpected asset in script: {asset_name}")

        context.logger.debug("Finished parsing Script")
        return cls(
            name=name,
            comment=comment,
            conditions_comment=conditions_comment,
            actions_comment=actions_comment,
            is_active=is_active,
            deactivate_upon_success=deactivate_upon_success,
            active_in_easy=active_in_easy,
            active_in_medium=active_in_medium,
            active_in_hard=active_in_hard,
            is_subroutine=is_subroutine,
            evaluation_interval=evaluation_interval,
            uses_evaluation_interval_type=uses_evaluation_interval_type,
            evaluation_interval_type=evaluation_interval_type,
            actions_fire_sequentially=actions_fire_sequentially,
            loop_actions=loop_actions,
            loop_count=loop_count,
            sequential_target_type=sequential_target_type,
            sequential_target_name=sequential_target_name,
            unknown=unknown,
            unknown2=unknown2,
            unknown3=unknown3,
            or_conditions=or_conditions,
            actions_if_true=actions_if_true,
            actions_if_false=actions_if_false,
        )


@dataclass
class ScriptGroup:
    version: int
    name: str
    is_active: bool
    is_subroutine: bool
    script_groups: dict[str, "ScriptGroup"] = field(default_factory=dict)
    scripts: dict[str, Script] = field(default_factory=dict)

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, datasize):
            group_end_pos = context.stream.tell() + datasize
            name = context.stream.readUInt16PrefixedAsciiString()
            is_active = context.stream.readBool()
            is_subroutine = context.stream.readBool()

            script_groups = {}
            scripts = {}

            while context.stream.tell() < group_end_pos:
                nested_groups, nested_scripts = ScriptGroup.parse_script_list(context)
                script_groups.update(nested_groups)
                scripts.update(nested_scripts)

        context.logger.debug("Finished parsing ScriptGroup")
        return cls(
            version=version,
            name=name,
            is_active=is_active,
            is_subroutine=is_subroutine,
            script_groups=script_groups,
            scripts=scripts,
        )

    @staticmethod
    def parse_script_list(
        context: "ParsingContext",
    ) -> tuple[dict[str, "ScriptGroup"], dict[str, Script]]:
        script_groups = {}
        scripts = {}
        asset_name = context.parse_asset_name()

        if asset_name == "ScriptGroup":
            group = ScriptGroup.parse(context)
            script_groups[group.name] = group
        elif asset_name == "Script":
            script = Script.parse(context)
            scripts[script.name] = script
        else:
            raise ValueError(f"Expected ScriptGroup or Script asset, got {asset_name}")

        return script_groups, scripts


@dataclass
class ScriptList:
    script_groups: dict[str, ScriptGroup]
    scripts: dict[str, Script]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (asset_version, datasize):
            script_list_end_pos = context.stream.tell() + datasize

            if asset_version != 1:
                raise ValueError(f"Unexpected ScriptList version: {asset_version}")

            script_groups = {}
            scripts = {}

            while context.stream.tell() < script_list_end_pos:
                nested_groups, nested_scripts = ScriptGroup.parse_script_list(context)
                script_groups.update(nested_groups)
                scripts.update(nested_scripts)

        context.logger.debug("Finished parsing ScriptList")
        return cls(script_groups=script_groups, scripts=scripts)


@dataclass
class PlayerScriptsList:
    asset_name = "PlayerScriptsList"

    version: int
    script_lists: list[ScriptList]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, datasize):
            player_script_list_end_pos = context.stream.tell() + datasize

            script_lists = []
            while context.stream.tell() < player_script_list_end_pos:
                asset_name = context.parse_asset_name()
                if asset_name != "ScriptList":
                    raise ValueError(f"Expected ScriptList asset, got {asset_name}")

                script_lists.append(ScriptList.parse(context))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(version=version, script_lists=script_lists)
