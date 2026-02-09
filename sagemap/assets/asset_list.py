from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class AssetListItem:
    type_id: int
    isntance_id: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        type_id = context.stream.readUInt32()
        instance_id = context.stream.readUInt32()

        context.logger.debug(f"Parsed AssetListItem: Type ID: {type_id}, Instance ID: {instance_id}")
        return cls(type_id, instance_id)


@dataclass
class AssetList:
    asset_name = "AssetList"

    version: int
    asset_names: list[AssetListItem]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            asset_count = context.stream.readUInt32()
            asset_names = [AssetListItem.parse(context) for _ in range(asset_count)]

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(asset_ctx.version, asset_names, asset_ctx.start_pos, asset_ctx.end_pos)
