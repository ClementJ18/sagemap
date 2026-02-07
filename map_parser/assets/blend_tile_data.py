from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext
    from .height_map import HeightMapData


class TileFlammability(IntEnum):
    """Enum for tile flammability values."""
    FIRE_RESISTANT = 0
    GRASS = 1
    HIGHLY_FLAMMABLE = 2
    UNDEFINED = 3


@dataclass
class BlendTileTexture:
    """Represents a blend tile texture (inline data structure, not an asset)."""
    cell_start: int
    cell_count: int
    cell_size: int
    magic_value: int
    name: str

    @classmethod
    def parse(cls, context: 'ParsingContext'):
        """Parse inline (no asset header)."""
        cell_start = context.stream.readUInt32()
        cell_count = context.stream.readUInt32()
        cell_size = context.stream.readUInt32()
        
        if cell_size * cell_size != cell_count:
            raise ValueError(f"Invalid cell_size: {cell_size}^2 != {cell_count}")
        
        magic_value = context.stream.readUInt32()
        if magic_value != 0:
            raise ValueError(f"Expected magic_value to be 0, got: {magic_value}")
        
        name = context.stream.readUInt16PrefixedAsciiString()
        
        return cls(cell_start=cell_start, cell_count=cell_count, cell_size=cell_size, 
                   magic_value=magic_value, name=name)


@dataclass
class BlendDescription:
    """Represents a blend description (inline data structure, not an asset)."""
    secondary_texture_tile: int
    raw_blend_direction: bytes
    flags: int
    two_sided: bool
    magic_value1: int

    @classmethod
    def parse(cls, context: 'ParsingContext', version: int):
        """Parse inline (no asset header)."""
        secondary_texture_tile = context.stream.readUInt32()
        raw_blend_direction = context.stream.readBytes(4)
        flags = context.stream.readUChar()
        two_sided = context.stream.readBool()
        
        magic_value1 = context.stream.readUInt32()
        # MagicValue1 can be 0xFFFFFFFF or 24
        
        magic_value2 = context.stream.readUInt32()
        if magic_value2 != 0x7ADA0000:
            raise ValueError(f"Expected magic_value2 to be 0x7ADA0000, got: {magic_value2:#x}")
        
        return cls(secondary_texture_tile=secondary_texture_tile, 
                   raw_blend_direction=raw_blend_direction,
                   flags=flags, two_sided=two_sided, magic_value1=magic_value1)


@dataclass
class CliffTextureMapping:
    """Represents a cliff texture mapping (inline data structure, not an asset)."""
    texture_tile: int
    bottom_left_coords: tuple[float, float]
    bottom_right_coords: tuple[float, float]
    top_right_coords: tuple[float, float]
    top_left_coords: tuple[float, float]
    unknown2: int

    @classmethod
    def parse(cls, context: 'ParsingContext'):
        """Parse inline (no asset header)."""
        texture_tile = context.stream.readUInt32()
        
        # Read 4 Vector2s (each is 2 floats)
        bottom_left_coords = context.stream.readVector2()
        bottom_right_coords = context.stream.readVector2()
        top_right_coords = context.stream.readVector2()
        top_left_coords = context.stream.readVector2()
        
        unknown2 = context.stream.readUInt16()
        
        return cls(texture_tile=texture_tile, 
                   bottom_left_coords=bottom_left_coords,
                   bottom_right_coords=bottom_right_coords,
                   top_right_coords=top_right_coords,
                   top_left_coords=top_left_coords,
                   unknown2=unknown2)


def get_blend_bit_size(version: int) -> int:
    """Get the blend bit size based on version.
    Returns 32 for versions 14-23, otherwise 16.
    """
    if version >= 14 and version < 24:
        return 32
    else:
        return 16


@dataclass
class BlendTileData:
    asset_name = "BlendTileData"
    
    tiles: list[list[int]]
    blends: list[list[int]]
    three_way_blends: list[list[int]]
    cliff_textures: list[list[int]]
    impassability: list[list[bool]] | None
    impassability_to_players: list[list[bool]] | None
    passage_widths: list[list[bool]] | None
    taintability: list[list[bool]] | None
    extra_passability: list[list[bool]] | None
    flammability: list[list[TileFlammability]] | None
    visibility: list[list[bool]] | None
    buildability: list[list[bool]] | None
    impassability_to_air_units: list[list[bool]] | None
    tiberium_growability: list[list[bool]] | None
    dynamic_shrubbery_density: list[list[int]] | None
    texture_cell_count: int
    parsed_cliff_texture_mappings_count: int
    textures: list[BlendTileTexture]
    magic_value1: int
    magic_value2: int
    blend_descriptions: list[BlendDescription]
    cliff_texture_mappings: list[CliffTextureMapping]
    unparsed_data: bytes
    
    @classmethod
    def parse(cls, context: 'ParsingContext', height_map_data: 'HeightMapData'):
        with context.read_asset() as (version, datasize):
            start_pos = context.stream.tell()
            end_pos = start_pos + datasize

            if version < 6:
                raise ValueError(f"Unsupported BlendTileData version: {version}")
        
            if height_map_data is None:
                raise ValueError("Expected HeightMapData asset before BlendTileData asset.")
            
            width = height_map_data.width
            height = height_map_data.height
            
            tiles_count = context.stream.readUInt32()
            if tiles_count != width * height:
                raise ValueError(f"Invalid tiles_count: {tiles_count}, expected: {width * height}")

            tiles = context.stream.readUInt16Array2D(width, height)

            blend_bit_size = get_blend_bit_size(version)
            blends = context.stream.readUIntArray2D(width, height, blend_bit_size)
            three_way_blends = context.stream.readUIntArray2D(width, height, blend_bit_size)
            cliff_textures = context.stream.readUIntArray2D(width, height, blend_bit_size)

            impassability = None
            if version > 6:
                passability_width = height_map_data.width
                if version == 7:
                    # C&C Generals clips partial bytes from each row of passability data
                    passability_width = ((passability_width + 1) // 8) * 8

                # If terrain is passable, there's a 0 in the data file.
                impassability = context.stream.readSingleBitBooleanArray2D(passability_width, height_map_data.height)

            impassability_to_players = None
            if version >= 10:
                impassability_to_players = context.stream.readSingleBitBooleanArray2D(height_map_data.width, height_map_data.height)

            passage_widths = None
            if version >= 11:
                passage_widths = context.stream.readSingleBitBooleanArray2D(height_map_data.width, height_map_data.height)

            taintability = None
            if version >= 14 and version < 25:
                taintability = context.stream.readSingleBitBooleanArray2D(height_map_data.width, height_map_data.height)

            extra_passability = None
            if version >= 15:
                extra_passability = context.stream.readSingleBitBooleanArray2D(height_map_data.width, height_map_data.height)

            flammability = None
            if version >= 16 and version < 25:
                flammability = context.stream.readByteArray2DAsEnum(height_map_data.width, height_map_data.height, TileFlammability)

            visibility = None
            if version >= 17:
                # Visibility uses row-based byte alignment (padValue: 0xFF in C# WriteTo)
                visibility = context.stream.readSingleBitBooleanArray2D(height_map_data.width, height_map_data.height, row_byte_aligned=True)

            buildability = None
            impassability_to_air_units = None
            tiberium_growability = None
            if version >= 24:
                # TODO: Are these in the right order?
                buildability = context.stream.readSingleBitBooleanArray2D(height_map_data.width, height_map_data.height)
                impassability_to_air_units = context.stream.readSingleBitBooleanArray2D(height_map_data.width, height_map_data.height)
                tiberium_growability = context.stream.readSingleBitBooleanArray2D(height_map_data.width, height_map_data.height)

            dynamic_shrubbery_density = None
            if version >= 25:
                dynamic_shrubbery_density = context.stream.readByteArray2D(height_map_data.width, height_map_data.height)

            texture_cell_count = context.stream.readUInt32()

            blends_count_raw = context.stream.readUInt32()
            blends_count = blends_count_raw
            if blends_count > 0:
                # Usually minimum value is 1, but some files (perhaps Generals, not Zero Hour?) have 0.
                blends_count -= 1

            parsed_cliff_texture_mappings_count = context.stream.readUInt32()
            cliff_blends_count = parsed_cliff_texture_mappings_count
            if cliff_blends_count > 0:
                # Usually minimum value is 1, but some files (perhaps Generals, not Zero Hour?) have 0.
                cliff_blends_count -= 1
            
            texture_count = context.stream.readUInt32()
            textures = []
            for i in range(texture_count):
                textures.append(BlendTileTexture.parse(context))
                

            # Can be a variety of values, don't know what it means.
            magic_value1 = context.stream.readUInt32()

            magic_value2 = context.stream.readUInt32()
            if magic_value2 != 0:
                raise ValueError(f"Expected magic_value2 to be 0, got: {magic_value2}")

            blend_descriptions = []
            for _ in range(blends_count):
                blend_descriptions.append(BlendDescription.parse(context, version))

            cliff_texture_mappings = []
            for _ in range(cliff_blends_count):
                cliff_texture_mappings.append(CliffTextureMapping.parse(context))

            unparsed_data = context.stream.base_stream.read(end_pos - context.stream.tell())
            if len(unparsed_data) > 0:
                context.logger.warning(f"BlendTileData: {len(unparsed_data)} bytes of unparsed data at the end of the asset")

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(
            tiles=tiles,
            blends=blends,
            three_way_blends=three_way_blends,
            cliff_textures=cliff_textures,
            impassability=impassability,
            impassability_to_players=impassability_to_players,
            passage_widths=passage_widths,
            taintability=taintability,
            extra_passability=extra_passability,
            flammability=flammability,
            visibility=visibility,
            buildability=buildability,
            impassability_to_air_units=impassability_to_air_units,
            tiberium_growability=tiberium_growability,
            dynamic_shrubbery_density=dynamic_shrubbery_density,
            texture_cell_count=texture_cell_count,
            parsed_cliff_texture_mappings_count=parsed_cliff_texture_mappings_count,
            textures=textures,
            magic_value1=magic_value1,
            magic_value2=magic_value2,
            blend_descriptions=blend_descriptions,
            cliff_texture_mappings=cliff_texture_mappings,
            unparsed_data=unparsed_data
        )

