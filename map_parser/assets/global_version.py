from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext, WritingContext


@dataclass
class GlobalVersion:
    asset_name = "GlobalVersion"

    version: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, _):
            pass

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(version=version)

    def write(self, context: "WritingContext"):
        with context.write_asset(self.asset_name, self.version):
            pass
