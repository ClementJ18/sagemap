from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sagemap.assets.object_list import Object


class Severity:
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LintError:
    severity = Severity.ERROR
    message_template = "An unspecified lint error occurred."
    code = "MAP-000"
    extra: dict

    def __init__(self, *, code=None, message_template=None, severity=None, extra=None):
        self.code = code or self.code
        self.message_template = message_template or self.message_template
        self.severity = severity or self.severity
        self.extra = extra or {}

    @property
    def message(self):
        return self.message_template.format(**self.extra)

    def __str__(self):
        return f"[{self.code}] {self.message}"

    def __repr__(self):
        return f"LintError(code={self.code}, message={self.message}, severity={self.severity}, extra={self.extra})"


class ContainsExpansionFlagError(LintError):
    severity = Severity.ERROR
    message_template = "Map contains ExpansionFlag at position {position} which is not supported."
    code = "MAP-002"

    def __init__(self, obj: "Object"):
        super().__init__(extra={"position": obj.position, "id": obj.properties["uniqueID"]["value"]})


class StartWaypointForNonExistentPlayerError(LintError):
    severity = Severity.ERROR
    message_template = "Map has a start waypoint for non-existent {waypoint_name}."
    code = "MAP-003"

    def __init__(self, waypoint_name):
        super().__init__(extra={"waypoint_name": waypoint_name})


class SpawnWaypointForNonExistentPlayerError(LintError):
    severity = Severity.ERROR
    message_template = "Map has a spawn waypoint for non-existent {waypoint_name}."
    code = "MAP-004"

    def __init__(self, waypoint_name):
        super().__init__(extra={"waypoint_name": waypoint_name})


class RotatedPlotFlagError(LintError):
    severity = Severity.ERROR
    message_template = "Map contains PlotFlag at position {position} with non-zero angle which may cause issues."
    code = "MAP-005"

    def __init__(self, obj: "Object"):
        super().__init__(extra={"position": obj.position, "id": obj.properties["uniqueID"]["value"]})


class MissingFarmTemplateError(LintError):
    severity = Severity.ERROR
    message_template = "Map does not contain any FarmTemplate objects, which may cause issues with the AI."
    code = "MAP-006"


class MissingPlayerTypesError(LintError):
    severity = Severity.ERROR
    message_template = "Map is missing required player types for AI: {missing_players}"
    code = "MAP-007"

    def __init__(self, missing_players):
        super().__init__(extra={"missing_players": missing_players})


class MissingGollumSpawnScriptError(LintError):
    severity = Severity.ERROR
    message_template = (
        "Map does not contain any SkirmishGollum_Spawn script, which may cause issues with Gollum spawns."
    )
    code = "MAP-008"


class MissingGollumSpawnPointError(LintError):
    severity = Severity.ERROR
    message_template = "Map does not contain any Gollum spawn points, which may cause issues with Gollum spawns."
    code = "MAP-009"


class MissingSpawnWaypointError(LintError):
    severity = Severity.ERROR
    message_template = "Player {player_num} has a start waypoint but is missing a spawn waypoint, which may cause issues with player spawns."
    code = "MAP-010"

    def __init__(self, player_num):
        super().__init__(extra={"player_num": player_num})


class NonFlatPlotFlagError(LintError):
    severity = Severity.ERROR
    message_template = "{flag_type} at position {position} is placed on non-flat terrain (radius {radius}), which may cause building issues."
    code = "MAP-011"

    def __init__(self, obj: "Object", radius):
        super().__init__(
            extra={
                "flag_type": obj.type_name,
                "position": obj.position,
                "radius": radius,
                "id": obj.properties["uniqueID"]["value"],
            }
        )


class PlotFlagTooCloseToBoderError(LintError):
    severity = Severity.ERROR
    message_template = (
        "{flag_type} at position {position} is too close to the world border (minimum distance: 10 units)."
    )
    code = "MAP-012"

    def __init__(self, obj: "Object"):
        super().__init__(
            extra={"flag_type": obj.type_name, "position": obj.position, "id": obj.properties["uniqueID"]["value"]}
        )


class InsufficientTreesNearWirtschaftError(LintError):
    severity = Severity.WARNING
    message_template = "WirtschaftPlotFlag at position {position} has insufficient trees nearby (found {tree_count}, required 30 within 30 units)."
    code = "MAP-013"

    def __init__(self, obj: "Object", tree_count):
        super().__init__(
            extra={"position": obj.position, "tree_count": tree_count, "id": obj.properties["uniqueID"]["value"]}
        )


class UnevenFarmTemplateWarning(LintError):
    severity = Severity.WARNING
    message_template = (
        "FarmTemplate at position {position} is placed on uneven terrain ({flat_percentage:.1f}% flat, threshold 67%)."
    )
    code = "MAP-014"

    def __init__(self, obj: "Object", flat_percentage):
        super().__init__(
            extra={
                "position": obj.position,
                "flat_percentage": flat_percentage,
                "id": obj.properties["uniqueID"]["value"],
            }
        )


class ExcessiveObjectCountWarning(LintError):
    severity = Severity.WARNING
    message_template = "Map contains {object_count} objects, which exceeds the recommended limit of {limit} and may cause performance issues."
    code = "MAP-015"

    def __init__(self, object_count, limit):
        super().__init__(extra={"object_count": object_count, "limit": limit})


class LowExpansionPlotFlagCountInfo(LintError):
    severity = Severity.INFO
    message_template = "Map has {count} ExpansionPlotFlag object(s); recommended is more than 1."
    code = "MAP-016"

    def __init__(self, count):
        super().__init__(extra={"count": count})


class CameraMaxHeightTooLowError(LintError):
    severity = Severity.ERROR
    message_template = "Map cameraMaxHeight is {height}, which is below the minimum of 533."
    code = "MAP-017"

    def __init__(self, height):
        super().__init__(extra={"height": height})


class MapParsingError(LintError):
    severity = Severity.ERROR
    message_template = "Failed to parse map file: {original_exception}"
    code = "MAP-999"

    def __init__(self, original_exception):
        super().__init__(extra={"original_exception": str(original_exception)})
