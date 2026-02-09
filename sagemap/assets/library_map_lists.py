from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class LibraryMaps:
    asset_name = "LibraryMaps"

    version: int
    values: list[str]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            values_count = context.stream.readUInt32()
            values = []

            for _ in range(values_count):
                values.append(context.stream.readUInt16PrefixedAsciiString())

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(asset_ctx.version, values, asset_ctx.start_pos, asset_ctx.end_pos)


@dataclass
class LibraryMapLists:
    asset_name = "LibraryMapLists"

    version: int
    lists: list[LibraryMaps]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            lists = []
            while context.stream.tell() < asset_ctx.end_pos:
                asset_name = context.parse_asset_name()
                if asset_name != LibraryMaps.asset_name:
                    raise ValueError(f"Expected {LibraryMaps.asset_name} asset, got {asset_name}")

                lists.append(LibraryMaps.parse(context))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(asset_ctx.version, lists, asset_ctx.start_pos, asset_ctx.end_pos)
