from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext

@dataclass
class LibraryMaps:
    asset_name = "LibraryMaps"

    version: int
    values: list[str]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()
        
        values_count = context.stream.readUInt32()
        values = []

        for _ in range(values_count):
            values.append(context.stream.readUInt16PrefixedAsciiString())

        context.logger.debug(f"Parsed LibraryMaps with {len(values)} values")
        return cls(version, values)


@dataclass
class LibraryMapLists:
    asset_name = "LibraryMapLists"

    version: int
    lists: list[LibraryMaps]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, datasize = context.parse_asset_header()
        end_pos = context.stream.base_stream.tell() + datasize

        lists = []
        while context.stream.base_stream.tell() < end_pos:
            asset_name = context.parse_asset_name()
            if asset_name != LibraryMaps.asset_name:
                raise ValueError(f"Expected {LibraryMaps.asset_name} asset, got {asset_name}")

            lists.append(LibraryMaps.parse(context))

        context.logger.debug(f"Parsed LibraryMapLists with {len(lists)} items")
        return cls(version, lists)
