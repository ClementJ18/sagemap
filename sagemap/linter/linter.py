from typing import TYPE_CHECKING

from .errors import (
    CameraMaxHeightTooLowError,
    ContainsExpansionFlagError,
    ExcessiveObjectCountWarning,
    InsufficientTreesNearWirtschaftError,
    LintError,
    LowExpansionPlotFlagCountInfo,
    MapParsingError,
    MissingFarmTemplateError,
    MissingGollumSpawnPointError,
    MissingGollumSpawnScriptError,
    MissingPlayerTypesError,
    MissingSpawnWaypointError,
    NonFlatPlotFlagError,
    PlotFlagTooCloseToBoderError,
    RotatedPlotFlagError,
    SpawnWaypointForNonExistentPlayerError,
    StartWaypointForNonExistentPlayerError,
    UnevenFarmTemplateWarning,
)
from .height_utils import get_flatness_percentage, is_flat_at_position

if TYPE_CHECKING:
    from ..map import Map

REQUIRED_PLAYERS = [
    "SkirmishMen",
    "SkirmishRohan",
    "SkirmishElves",
    "SkirmishDwarves",
    "SkirmishIsengard",
    "SkirmishMordor",
    "SkirmishImladris",
    "SkirmishWild",
    "SkirmishAngmar",
    "SkirmishEvilmen",
]

FLATNESS_RADIUS = {
    "FestungPlotFlag": 50,
    "LagerPlotFlag": 40,
    "HalfCastlePlotFlag": 40,
    "ExpansionPlotFlag": 30,
    "WirtschaftPlotFlag": 10,
}


def lint_map_validation(map_obj: "Map") -> list[LintError]:
    errors = []

    try:
        player_points = {str(x): {"exists": False, "has_spawn": False} for x in range(1, 9)}
        expansion_plot_flag_count = 0
        is_wotr = not any(
            obj.type_name.startswith(("FestungPlotFlag", "LagerPlotFlag", "HalfCastlePlotFlag"))
            for obj in map_obj.objects_list.object_list
        )
        gollum = has_farm_templates = has_gollum_spawn = is_wotr

        for obj in map_obj.objects_list.object_list:
            obj_type = obj.type_name

            if obj_type == "ExpansionFlag":
                errors.append(ContainsExpansionFlagError(obj))
            elif obj_type == "ExpansionPlotFlag":
                expansion_plot_flag_count += 1
                if obj.angle != 0:
                    errors.append(RotatedPlotFlagError(obj))
            elif obj_type == "FarmTemplate":
                has_farm_templates = True
            elif obj_type == "*Waypoints/Waypoint":
                waypoint_name = obj.properties["waypointName"]["value"]
                paths = [
                    obj.properties[f"waypointPathLabel{x}"]["value"]
                    for x in range(1, 4)
                    if f"waypointPathLabel{x}" in obj.properties
                ]

                if waypoint_name.startswith("Player_") and waypoint_name.endswith("_Start"):
                    player_num = waypoint_name[7:-6]
                    try:
                        player_points[player_num]["exists"] = True
                    except KeyError:
                        errors.append(StartWaypointForNonExistentPlayerError(waypoint_name))
                    continue

                if waypoint_name.startswith("Player_") and waypoint_name.endswith("_Spawn") and "Player_Path" in paths:
                    player_num = waypoint_name[7:-6]
                    try:
                        player_points[player_num]["has_spawn"] = True
                    except KeyError:
                        errors.append(SpawnWaypointForNonExistentPlayerError(waypoint_name))
                    continue

                if waypoint_name.startswith("SpawnPoint_SkirmishGollum_"):
                    gollum = True
            elif obj.type_name.startswith(("FestungPlotFlag", "LagerPlotFlag", "HalfCastlePlotFlag")):
                if obj.angle != 0:
                    errors.append(RotatedPlotFlagError(obj))

        if expansion_plot_flag_count <= 1:
            errors.append(LowExpansionPlotFlagCountInfo(expansion_plot_flag_count))

        camera_max_height = map_obj.world_info.properties.get("cameraMaxHeight", {}).get("value")
        if camera_max_height is not None and camera_max_height < 533:
            errors.append(CameraMaxHeightTooLowError(camera_max_height))

        if not has_farm_templates:
            errors.append(MissingFarmTemplateError())

        if not gollum:
            errors.append(MissingGollumSpawnPointError())

        missing_spawns = [num for num, p in player_points.items() if p["exists"] and not p["has_spawn"]]
        if missing_spawns:
            errors.extend(MissingSpawnWaypointError(num) for num in missing_spawns)

        players = {player.properties["playerName"]["value"] for player in map_obj.sides_list.players}
        missing_players = [p for p in REQUIRED_PLAYERS if p not in players]
        if missing_players:
            errors.append(MissingPlayerTypesError(missing_players))

        if not is_wotr:
            for script_list in map_obj.player_scripts_list.script_lists:
                if any(script.name == "SkirmishGollum_Spawn" for script in script_list.items):
                    has_gollum_spawn = True
                    break

            if not has_gollum_spawn:
                for library in map_obj.library_map_lists.lists:
                    if any("Lib_GollumSpawn" in script for script in library.values):
                        has_gollum_spawn = True
                        break

            if not has_gollum_spawn:
                errors.append(MissingGollumSpawnScriptError())
    except Exception as e:
        errors.append(MapParsingError(e))

    return errors


def lint_map_flatness(map_obj: "Map") -> list[LintError]:
    errors = []

    height_map = map_obj.height_map_data
    border_width = height_map.border_width
    world_width = height_map.width - 2 * border_width
    world_height = height_map.height - 2 * border_width
    min_border_distance = 10

    flags = [
        obj
        for obj in map_obj.objects_list.object_list
        if any(obj.type_name.startswith(prefix) for prefix in FLATNESS_RADIUS)
    ]
    for flag in flags:
        radius = next(FLATNESS_RADIUS[prefix] for prefix in FLATNESS_RADIUS if flag.type_name.startswith(prefix))

        flag_x, flag_y, _ = flag.position
        flag_x = flag_x / 10.0
        flag_y = flag_y / 10.0

        if (
            flag_x < min_border_distance
            or flag_y < min_border_distance
            or flag_x > world_width - min_border_distance
            or flag_y > world_height - min_border_distance
        ):
            errors.append(PlotFlagTooCloseToBoderError(flag))

        if not is_flat_at_position(map_obj, flag_x, flag_y, radius):
            errors.append(NonFlatPlotFlagError(flag, radius))

    farm_templates = [obj for obj in map_obj.objects_list.object_list if obj.type_name == "FarmTemplate"]
    farm_check_radius = 30
    flatness_threshold = 0.67

    for farm in farm_templates:
        farm_x, farm_y, _ = farm.position
        farm_x = farm_x / 10.0
        farm_y = farm_y / 10.0

        flat_percentage = get_flatness_percentage(map_obj, farm_x, farm_y, farm_check_radius)

        if flat_percentage < flatness_threshold:
            errors.append(UnevenFarmTemplateWarning(obj=farm, flat_percentage=flat_percentage * 100))

    return errors


def lint_map_resources(map_obj: "Map") -> list[LintError]:
    errors = []

    wirtschaft_flags = [
        obj for obj in map_obj.objects_list.object_list if obj.type_name.startswith("WirtschaftPlotFlag")
    ]
    tree_objects = [obj for obj in map_obj.objects_list.object_list if "tree" in obj.type_name.lower()]

    required_trees = 30
    search_radius = 30

    for flag in wirtschaft_flags:
        flag_x, flag_y, _ = flag.position
        flag_x = flag_x / 10.0
        flag_y = flag_y / 10.0

        tree_count = 0
        for tree in tree_objects:
            tree_x, tree_y, _ = tree.position
            tree_x = tree_x / 10.0
            tree_y = tree_y / 10.0

            distance = ((flag_x - tree_x) ** 2 + (flag_y - tree_y) ** 2) ** 0.5

            if distance <= search_radius:
                tree_count += 1

        if tree_count < required_trees:
            errors.append(InsufficientTreesNearWirtschaftError(obj=flag, tree_count=tree_count))

    return errors


def lint_map_performance(map_obj: "Map") -> list[LintError]:
    errors = []

    object_count = len(map_obj.objects_list.object_list)
    max_recommended_objects = 2000

    if object_count > max_recommended_objects:
        errors.append(ExcessiveObjectCountWarning(object_count=object_count, limit=max_recommended_objects))

    return errors


def lint_map(map_obj: "Map", exclude_codes: list[str] | None = None) -> list[LintError]:
    errors: list[LintError] = []

    errors.extend(lint_map_validation(map_obj))
    errors.extend(lint_map_flatness(map_obj))
    errors.extend(lint_map_resources(map_obj))
    errors.extend(lint_map_performance(map_obj))

    if exclude_codes:
        exclude_set = set(exclude_codes)
        errors = [err for err in errors if err.code not in exclude_set]

    return errors
