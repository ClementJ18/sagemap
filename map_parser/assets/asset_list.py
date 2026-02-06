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

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()
        asset_count = context.stream.readUInt32()
        asset_names = [AssetListItem.parse(context) for _ in range(asset_count)]

        context.logger.debug(f"Parsed AssetList asset, version: {version}, Asset Count: {asset_count}")
        return cls(version, asset_names)
