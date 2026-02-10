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
    CastleTemplates,
    EnvironmentData,
    FogSettings,
    GlobalLighting,
    GlobalVersion,
    HeightMapData,
    LibraryMapLists,
    MissionHotSpots,
    MissionObjectives,
    MPPositionList,
    NamedCameras,
    ObjectsList,
    PlayerScriptsList,
    PolygonTriggers,
    PostEffectsChunk,
    RiverAreas,
    SidesList,
    SkyboxSettings,
    StandingWaterAreas,
    StandingWaveAreas,
    Teams,
    TriggerAreas,
    WaterSettings,
    WaypointsList,
    WorldInfo,
)
from .context import ParsingContext, WritingContext
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
    mp_positions_list: MPPositionList
    fog_settings: FogSettings
    mission_hotspots: MissionHotSpots
    mission_objectives: MissionObjectives
    castle_templates: CastleTemplates
    skybox_settings: SkyboxSettings

    def __init__(self):
        self.compression_bytes = None
        self.asset_count = None
        self.assets = {}
        self.ea_compression_header = None

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
        self.fog_settings = None
        self.mission_hotspots = None
        self.mission_objectives = None
        self.castle_templates = None
        self.skybox_settings = None

    def parse(self, context: ParsingContext):
        context = context
        
        context.parse_assets()
        self.assets = context.assets
        self.compression_bytes = context.compression_bytes

        while context.stream.tell() < len(context.stream.getvalue()):
            asset_name = context.parse_asset_name()
            context.logger.info(f"Processing asset: {asset_name}")
            self.parse_asset(asset_name, context)

        context = None

    def parse_asset(self, asset_name: str, context: ParsingContext):
        if asset_name == AssetList.asset_name:
            self.asset_list = AssetList.parse(context)
        elif asset_name == HeightMapData.asset_name:
            self.height_map_data = HeightMapData.parse(context)
        elif asset_name == WorldInfo.asset_name:
            self.world_info = WorldInfo.parse(context)
        elif asset_name == Teams.asset_name:
            self.teams = Teams.parse(context)
        elif asset_name == PlayerScriptsList.asset_name:
            self.player_scripts_list = PlayerScriptsList.parse(context)
        elif asset_name == ObjectsList.asset_name:
            self.objects_list = ObjectsList.parse(context)
        elif asset_name == GlobalVersion.asset_name:
            self.global_version = GlobalVersion.parse(context)
        elif asset_name == BlendTileData.asset_name:
            self.blend_tile_data = BlendTileData.parse(context, self.height_map_data)
        elif asset_name == MPPositionList.asset_name:
            self.mp_positions_list = MPPositionList.parse(context)
        elif asset_name == SidesList.asset_name:
            self.sides_list = SidesList.parse(context, self.asset_list is not None)
        elif asset_name == TriggerAreas.asset_name:
            self.trigger_areas = TriggerAreas.parse(context)
        elif asset_name == PolygonTriggers.asset_name:
            self.polygon_triggers = PolygonTriggers.parse(context)
        elif asset_name == WaypointsList.asset_name:
            self.waypoints_list = WaypointsList.parse(context)
        elif asset_name == WaterSettings.asset_name:
            self.water_settings = WaterSettings.parse(context)
        elif asset_name == BuildLists.asset_name:
            self.build_lists = BuildLists.parse(context, self.asset_list is not None)
        elif asset_name == StandingWaterAreas.asset_name:
            self.standing_water_areas = StandingWaterAreas.parse(context)
        elif asset_name == StandingWaveAreas.asset_name:
            self.standing_wave_areas = StandingWaveAreas.parse(context)
        elif asset_name == RiverAreas.asset_name:
            self.river_areas = RiverAreas.parse(context)
        elif asset_name == GlobalLighting.asset_name:
            self.global_lighting = GlobalLighting.parse(context)
        elif asset_name == EnvironmentData.asset_name:
            self.environment_data = EnvironmentData.parse(context)
        elif asset_name == PostEffectsChunk.asset_name:
            self.post_effects_chunk = PostEffectsChunk.parse(context)
        elif asset_name == NamedCameras.asset_name:
            self.named_cameras = NamedCameras.parse(context)
        elif asset_name == CameraAnimationList.asset_name:
            self.camera_animation_list = CameraAnimationList.parse(context)
        elif asset_name == LibraryMapLists.asset_name:
            self.library_map_lists = LibraryMapLists.parse(context)
        elif asset_name == FogSettings.asset_name:
            self.fog_settings = FogSettings.parse(context)
        elif asset_name == MissionHotSpots.asset_name:
            self.mission_hotspots = MissionHotSpots.parse(context)
        elif asset_name == MissionObjectives.asset_name:
            self.mission_objectives = MissionObjectives.parse(context)
        elif asset_name == CastleTemplates.asset_name:
            self.castle_templates = CastleTemplates.parse(context)
        elif asset_name == SkyboxSettings.asset_name:
            self.skybox_settings = SkyboxSettings.parse(context)
        else:
            raise ValueError(f"Unknown asset: {asset_name}")

    def to_dict(self):
        """Convert Map and all assets to a JSON-serializable dictionary"""
        result = {}

        for key, value in self.__dict__.items():
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
        
    def write(self, context: WritingContext) -> bytes:
        if self.assets:
            context.assets_by_index = self.assets.copy()
            context.index_by_asset = {name: idx for idx, name in self.assets.items()}
        
        if self.asset_list is not None:
            context.write_asset_name(AssetList.asset_name)
            self.asset_list.write(context)

        if self.global_version is not None:
            context.write_asset_name(GlobalVersion.asset_name)
            self.global_version.write(context)

        context.write_asset_name(HeightMapData.asset_name)
        self.height_map_data.write(context)

        context.write_asset_name(BlendTileData.asset_name)
        self.blend_tile_data.write(context)

        context.write_asset_name(WorldInfo.asset_name)
        self.world_info.write(context)

        if self.mp_positions_list is not None:
            context.write_asset_name(MPPositionList.asset_name)
            self.mp_positions_list.write(context)

        context.write_asset_name(SidesList.asset_name)
        self.sides_list.write(context, self.asset_list is not None)

        if self.library_map_lists is not None:
            context.write_asset_name(LibraryMapLists.asset_name)
            self.library_map_lists.write(context)

        if self.teams is not None:
            context.write_asset_name(Teams.asset_name)
            self.teams.write(context)

        if self.player_scripts_list is not None:
            context.write_asset_name(PlayerScriptsList.asset_name)
            self.player_scripts_list.write(context)

        if self.build_lists is not None:
            context.write_asset_name(BuildLists.asset_name)
            self.build_lists.write(context, self.asset_list is not None)

        context.write_asset_name(ObjectsList.asset_name)
        self.objects_list.write(context)

        if self.polygon_triggers is not None:
            context.write_asset_name(PolygonTriggers.asset_name)
            self.polygon_triggers.write(context)

        if self.trigger_areas is not None:
            context.write_asset_name(TriggerAreas.asset_name)
            self.trigger_areas.write(context)

        if self.water_settings is not None:
            context.write_asset_name(WaterSettings.asset_name)
            self.water_settings.write(context)

        if self.fog_settings is not None:
            context.write_asset_name(FogSettings.asset_name)
            self.fog_settings.write(context)

        if self.mission_hotspots is not None:
            context.write_asset_name(MissionHotSpots.asset_name)
            self.mission_hotspots.write(context)

        if self.mission_objectives is not None:
            context.write_asset_name(MissionObjectives.asset_name)
            self.mission_objectives.write(context)

        if self.standing_water_areas is not None:
            context.write_asset_name(StandingWaterAreas.asset_name)
            self.standing_water_areas.write(context)

        if self.river_areas is not None:
            context.write_asset_name(RiverAreas.asset_name)
            self.river_areas.write(context)

        if self.standing_wave_areas is not None:
            context.write_asset_name(StandingWaveAreas.asset_name)
            self.standing_wave_areas.write(context)

        context.write_asset_name(GlobalLighting.asset_name)
        self.global_lighting.write(context)

        if self.post_effects_chunk is not None:
            context.write_asset_name(PostEffectsChunk.asset_name)
            self.post_effects_chunk.write(context)

        if self.environment_data is not None:
            context.write_asset_name(EnvironmentData.asset_name)
            self.environment_data.write(context)

        if self.named_cameras is not None:
            context.write_asset_name(NamedCameras.asset_name)
            self.named_cameras.write(context)

        if self.camera_animation_list is not None:
            context.write_asset_name(CameraAnimationList.asset_name)
            self.camera_animation_list.write(context)

        if self.castle_templates is not None:
            context.write_asset_name(CastleTemplates.asset_name)
            self.castle_templates.write(context)

        context.write_asset_name(WaypointsList.asset_name)
        self.waypoints_list.write(context)

        if self.skybox_settings is not None:
            context.write_asset_name(SkyboxSettings.asset_name)
            self.skybox_settings.write(context)

        asset_data = context.stream.getvalue()
        header_stream = BinaryStream(io.BytesIO())
        
        compression_bytes = self.compression_bytes if self.compression_bytes else "    "
        header_stream.writeFourCc(compression_bytes)
        
        asset_count = len(context.assets_by_index)
        header_stream.writeUInt32(asset_count)
        
        for i in range(asset_count, 0, -1):
            asset_name = context.assets_by_index[i]
            header_stream.writeString(asset_name)
            header_stream.writeUInt32(i)

        return header_stream.getvalue() + asset_data


def parse_map(file: io.BufferedReader) -> Map:
    ea_compression = file.read(8)
    if not ea_compression.startswith(b"EAR"):
        file.seek(0)
        ea_compression = None

    compressed_data = file.read()

    try:
        decompressed_data = RefpackHandler().decompress_data(compressed_data)
    except Exception:
        decompressed_data = compressed_data

    logger = logging.getLogger("sagemap")

    stream = BinaryStream(io.BytesIO(decompressed_data))
    context = ParsingContext(stream)
    context.set_logger(logger)

    map = Map()
    map.ea_compression_header = ea_compression
    map.parse(context)

    return map

def write_map(map: Map, compress: bool) -> bytes:
    stream = BinaryStream(io.BytesIO())
    context = WritingContext(stream)
    uncompressed_data = map.write(context)
    
    if compress:
        compressed_data = RefpackHandler().compress_data(uncompressed_data)
        if map.ea_compression_header:
            header_stream = BinaryStream(io.BytesIO())
            header_stream.writeFourCc("EAR\0")
            header_stream.writeUInt32(len(uncompressed_data))
            data = header_stream.getvalue() + compressed_data
        else:
            data = compressed_data
        
        return data
        
    return uncompressed_data

def parse_map_from_path(path: str) -> Map:
    with open(path, "rb") as file:
        return parse_map(file)

def write_map_to_path(map: Map, path: str, compress: bool):
    data = write_map(map, compress)
    with open(path, "wb") as file:
        file.write(data)