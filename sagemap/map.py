import base64
import io
import logging
from dataclasses import asdict, is_dataclass
from enum import Enum

from reversebox.compression.compression_refpack import RefpackHandler

from .assets import (
    AssetList,
    BlendTileData,
    BuildLists,
    CameraAnimationList,
    EnvironmentData,
    GlobalLighting,
    GlobalVersion,
    HeightMapData,
    LibraryMapLists,
    MPPositionsList,
    NamedCameras,
    ObjectsList,
    PlayerScriptsList,
    PolygonTriggers,
    PostEffectsChunk,
    RiverAreas,
    SidesList,
    SkippedAsset,
    StandingWaterAreas,
    StandingWaveAreas,
    Teams,
    TriggerAreas,
    WaterSettings,
    WaypointsList,
    WorldInfo,
)
from .context import ParsingContext
from .stream import BinaryStream


class Map:
    global_version: GlobalVersion
    height_map_data: HeightMapData
    blend_tile_data: BlendTileData
    world_info: WorldInfo
    objects_list: ObjectsList
    waypoints_list: WaypointsList
    sides_list: SidesList
    player_scripts_list: PlayerScriptsList
    water_settings: WaterSettings
    asset_list: AssetList
    build_lists: BuildLists
    polygon_triggers: PolygonTriggers
    trigger_areas: TriggerAreas
    standing_water_areas: StandingWaterAreas
    standing_wave_areas: StandingWaveAreas
    river_areas: RiverAreas
    global_lighting: GlobalLighting
    environment_data: EnvironmentData
    post_effects_chunk: PostEffectsChunk
    named_cameras: NamedCameras
    camera_animation_list: CameraAnimationList
    library_map_lists: LibraryMapLists
    teams: Teams
    mp_positions_list: MPPositionsList

    skipped_assets: dict[str, SkippedAsset]

    def __init__(self, context: ParsingContext = None):
        self.context = context

        self.compression_bytes = None
        self.asset_count = None
        self.assets = {}

        # assets
        self.global_version = None
        self.height_map_data = None
        self.blend_tile_data = None
        self.world_info = None
        self.objects_list = None
        self.waypoints_list = None
        self.sides_list = None
        self.player_scripts_list = None
        self.water_settings = None
        self.asset_list = None
        self.build_lists = None
        self.polygon_triggers = None
        self.trigger_areas = None
        self.standing_water_areas = None
        self.standing_wave_areas = None
        self.river_areas = None
        self.global_lighting = None
        self.environment_data = None
        self.post_effects_chunk = None
        self.named_cameras = None
        self.camera_animation_list = None
        self.library_map_lists = None

        self.skipped_assets = {}

    def parse(self):
        self.assets = self.context.parse_assets()
        while self.context.stream.tell() < len(self.context.stream.getvalue()):
            asset_name = self.context.parse_asset_name()
            self.context.logger.info(f"Processing asset: {asset_name}")
            self.parse_asset(asset_name)

    def parse_asset(self, asset_name: str):
        if asset_name == AssetList.asset_name:
            self.asset_list = AssetList.parse(self.context)
        elif asset_name == HeightMapData.asset_name:
            self.height_map_data = HeightMapData.parse(self.context)
        elif asset_name == WorldInfo.asset_name:
            self.world_info = WorldInfo.parse(self.context)
        elif asset_name == Teams.asset_name:
            self.teams = Teams.parse(self.context)
        elif asset_name == PlayerScriptsList.asset_name:
            self.player_scripts_list = PlayerScriptsList.parse(self.context)
        elif asset_name == ObjectsList.asset_name:
            self.objects_list = ObjectsList.parse(self.context)
        elif asset_name == GlobalVersion.asset_name:
            self.global_version = GlobalVersion.parse(self.context)
        elif asset_name == BlendTileData.asset_name:
            self.blend_tile_data = BlendTileData.parse(self.context, self.height_map_data)
        elif asset_name == MPPositionsList.asset_name:
            self.mp_positions_list = MPPositionsList.parse(self.context)
        elif asset_name == SidesList.asset_name:
            self.sides_list = SidesList.parse(self.context, self.asset_list is not None)
        elif asset_name == TriggerAreas.asset_name:
            self.trigger_areas = TriggerAreas.parse(self.context)
        elif asset_name == PolygonTriggers.asset_name:
            self.polygon_triggers = PolygonTriggers.parse(self.context)
        elif asset_name == WaypointsList.asset_name:
            self.waypoints_list = WaypointsList.parse(self.context)
        elif asset_name == WaterSettings.asset_name:
            self.water_settings = WaterSettings.parse(self.context)
        elif asset_name == BuildLists.asset_name:
            self.build_lists = BuildLists.parse(self.context, self.asset_list is not None)
        elif asset_name == StandingWaterAreas.asset_name:
            self.standing_water_areas = StandingWaterAreas.parse(self.context)
        elif asset_name == StandingWaveAreas.asset_name:
            self.standing_wave_areas = StandingWaveAreas.parse(self.context)
        elif asset_name == RiverAreas.asset_name:
            self.river_areas = RiverAreas.parse(self.context)
        elif asset_name == GlobalLighting.asset_name:
            self.global_lighting = GlobalLighting.parse(self.context)
        elif asset_name == EnvironmentData.asset_name:
            self.environment_data = EnvironmentData.parse(self.context)
        elif asset_name == PostEffectsChunk.asset_name:
            self.post_effects_chunk = PostEffectsChunk.parse(self.context)
        elif asset_name == NamedCameras.asset_name:
            self.named_cameras = NamedCameras.parse(self.context)
        elif asset_name == CameraAnimationList.asset_name:
            self.camera_animation_list = CameraAnimationList.parse(self.context)
        elif asset_name == LibraryMapLists.asset_name:
            self.library_map_lists = LibraryMapLists.parse(self.context)
        else:
            self.context.logger.debug(f"Unknown asset: {asset_name}, skipping")
            self.skipped_assets[asset_name] = SkippedAsset.parse(self.context, asset_name)

    def to_dict(self):
        """Convert Map and all assets to a JSON-serializable dictionary"""
        result = {}

        for key, value in self.__dict__.items():
            if key == "context":  # Skip the parsing context
                continue
            result[key] = self._serialize(value)

        return result

    def _serialize(self, obj):
        """Recursively serialize objects to JSON-compatible types"""
        if obj is None:
            return None
        elif isinstance(obj, bytes):
            return base64.b64encode(obj).decode("ascii")
        elif isinstance(obj, Enum):
            return obj.value
        elif is_dataclass(obj):
            return {k: self._serialize(v) for k, v in asdict(obj).items()}
        elif isinstance(obj, dict):
            return {(k.name if isinstance(k, Enum) else k): self._serialize(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize(item) for item in obj]
        else:
            return obj


def parse_map(file: io.BufferedReader) -> Map:
    ea_compression = file.read(8)
    if not ea_compression.startswith(b"EAR"):
        file.seek(0)

    compressed_data = file.read()

    try:
        decompressed_data = RefpackHandler().decompress_data(compressed_data)
    except Exception:
        decompressed_data = compressed_data

    logger = logging.getLogger("sagemap")

    stream = BinaryStream(io.BytesIO(decompressed_data))
    context = ParsingContext(stream)
    context.set_logger(logger)

    map = Map(context)
    map.parse()

    return map


def parse_map_from_path(path: str) -> Map:
    with open(path, "rb") as file:
        return parse_map(file)
