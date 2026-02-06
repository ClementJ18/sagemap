import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


class TimeOfTheDay(enum.Enum):
    Morning = 1
    Afternoon = 2
    Evening = 3
    Night = 4

    def map_to_str(self) -> str:
        times = {
            TimeOfTheDay.Morning: "MORNING",
            TimeOfTheDay.Afternoon: "AFTERNOON",
            TimeOfTheDay.Evening: "EVENING",
            TimeOfTheDay.Night: "NIGHT",
        }

        return times[self]


@dataclass
class MapColorArgb:
    a: int
    r: int
    g: int
    b: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        value = context.stream.readUInt32()
        a = (value >> 24) & 0xFF
        r = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        b = value & 0xFF

        return cls(a=a, r=r, g=g, b=b)


@dataclass
class GlobalLight:
    ambient: tuple[float, float, float]
    color: tuple[float, float, float]
    direction: tuple[float, float, float]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        ambient = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())
        color = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())
        direction = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())

        return cls(ambient, color, direction)


@dataclass
class GlobalLightingConfiguration:
    terrain_sun: GlobalLight
    object_sun: GlobalLight | None
    infantry_sun: GlobalLight | None
    terrain_accent1: GlobalLight
    object_accent1: GlobalLight | None
    infantry_accent1: GlobalLight | None
    terrain_accent2: GlobalLight
    object_accent2: GlobalLight | None
    infantry_accent2: GlobalLight | None

    @classmethod
    def parse(cls, context: "ParsingContext", version: int):
        terrain_sun = GlobalLight.parse(context)

        object_sun = None
        infantry_sun = None
        if version < 10:
            object_sun = GlobalLight.parse(context)

            if version >= 7:
                infantry_sun = GlobalLight.parse(context)

        terrain_accent1 = GlobalLight.parse(context)

        object_accent1 = None
        infantry_accent1 = None
        if version < 10:
            object_accent1 = GlobalLight.parse(context)

            if version >= 7:
                infantry_accent1 = GlobalLight.parse(context)

        terrain_accent2 = GlobalLight.parse(context)

        object_accent2 = None
        infantry_accent2 = None
        if version < 10:
            object_accent2 = GlobalLight.parse(context)

            if version >= 7:
                infantry_accent2 = GlobalLight.parse(context)

        return cls(
            terrain_sun=terrain_sun,
            object_sun=object_sun,
            infantry_sun=infantry_sun,
            terrain_accent1=terrain_accent1,
            object_accent1=object_accent1,
            infantry_accent1=infantry_accent1,
            terrain_accent2=terrain_accent2,
            object_accent2=object_accent2,
            infantry_accent2=infantry_accent2,
        )


@dataclass
class GlobalLighting:
    asset_name = "GlobalLighting"

    time_of_the_day: TimeOfTheDay
    lighting_configurations: dict[TimeOfTheDay, GlobalLightingConfiguration]
    shadow_color: MapColorArgb
    unknown: bytes | None
    unknown2: tuple[float, float, float] | None
    unknown3: MapColorArgb | None
    no_cloud_factor: tuple[float, float, float] | None

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()

        time = TimeOfTheDay(context.stream.readUInt32())
        lighting_configurations = {}

        for member in TimeOfTheDay:
            lighting_configurations[member] = GlobalLightingConfiguration.parse(context, version)

        shadow_color = MapColorArgb.parse(context)

        unknown = None
        if version >= 7 and version < 11:
            unknown = context.stream.readBytes(4 if version >= 9 else 44)

        unknown2 = None
        unknown3 = None
        if version >= 12:
            unknown2 = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())
            unknown3 = MapColorArgb.parse(context)

        no_cloud_factor = None
        if version >= 8:
            no_cloud_factor = (
                context.stream.readFloat(),
                context.stream.readFloat(),
                context.stream.readFloat(),
            )

        return cls(
            time_of_the_day=time,
            lighting_configurations=lighting_configurations,
            shadow_color=shadow_color,
            unknown=unknown,
            unknown2=unknown2,
            unknown3=unknown3,
            no_cloud_factor=no_cloud_factor,
        )
