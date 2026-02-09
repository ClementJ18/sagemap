from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext

@dataclass
class CastleTemplate:
    name: str
    template_name: str
    offset: tuple[float, float, float]
    angle: float
    priority: int | None
    phase: int | None

    @classmethod
    def parse(cls, context: "ParsingContext", version: int):
        name = context.stream.readUInt16PrefixedAsciiString()
        template_name = context.stream.readUInt16PrefixedAsciiString()
        offset = context.stream.readVector3()
        angle = context.stream.readFloat()

        priority = None
        phase = None
        if version >= 4:
            priority = context.stream.readUInt32()
            phase = context.stream.readUInt32()

        return cls(name=name, template_name=template_name, offset=offset, angle=angle, priority=priority, phase=phase)

@dataclass
class PerimeterPoint:
    x: float
    y: float
    z: float

    @classmethod
    def parse(cls, context: "ParsingContext", version: int):
        if version >= 3:
            x = context.stream.readFloat()
            y = context.stream.readFloat()
            z = 0.0
        else:
            x = context.stream.readInt32()
            y = context.stream.readInt32()
            z = context.stream.readInt32()

        return cls(x=x, y=y, z=z)

@dataclass
class CastlePerimeter:
    has_perimeter: bool
    name: str | None
    perimeter_points: list[PerimeterPoint]

    @classmethod
    def parse(cls, context: "ParsingContext", version: int):
        stream_pos_before = context.stream.tell()
        has_perimeter = context.stream.readBoolUInt32Checked()
        context.logger.debug(f"CastlePerimeter: has_perimeter={has_perimeter}, position before={stream_pos_before}, after bool={context.stream.tell()}")
        
        name = None
        perimeter_points = []

        if has_perimeter:
            name = context.stream.readUInt16PrefixedAsciiString()
            perimeter_point_count = context.stream.readUInt32()
            
            for _ in range(perimeter_point_count):
                perimeter_points.append(PerimeterPoint.parse(context, version))

        return cls(has_perimeter=has_perimeter, name=name, perimeter_points=perimeter_points)


@dataclass
class CastleTemplates:
    asset_name = "CastleTemplates"

    version: int
    property_key: tuple
    templates: list[CastleTemplate]
    perimeter: CastlePerimeter | None
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            context.logger.debug(f"CastleTemplates: version={asset_ctx.version}, datasize={asset_ctx.datasize}, start_pos={asset_ctx.start_pos}")
            
            property_key = context.parse_asset_property_key()
            pos_after_key = context.stream.tell()
            context.logger.debug(f"After property key: position={pos_after_key}, bytes consumed={pos_after_key - asset_ctx.start_pos}")

            template_count = context.stream.readUInt32()
            pos_after_count = context.stream.tell()
            context.logger.debug(f"Template count={template_count}, position={pos_after_count}, bytes consumed={pos_after_count - asset_ctx.start_pos}")
            
            templates = []
            for i in range(template_count):
                templates.append(CastleTemplate.parse(context, asset_ctx.version))
                if i < 3 or i >= template_count - 2:  # Log first 3 and last 2
                    pos = context.stream.tell()
                    context.logger.debug(f"After template {i+1}/{template_count}: position={pos}, total consumed={pos - asset_ctx.start_pos}")
            
            pos_before_perimeter = context.stream.tell()
            bytes_consumed = pos_before_perimeter - asset_ctx.start_pos
            remaining = asset_ctx.datasize - bytes_consumed
            context.logger.debug(f"Before perimeter: position={pos_before_perimeter}, consumed={bytes_consumed}/{asset_ctx.datasize}, remaining={remaining}")
            
            # Peek at the next 20 bytes without consuming
            peek_bytes = context.stream.readBytes(20)
            context.stream.seek(pos_before_perimeter)
            context.logger.debug(f"Next 20 bytes at perimeter start: {peek_bytes.hex(' ')}")

            perimeter = None
            if asset_ctx.version >= 2:
                perimeter = CastlePerimeter.parse(context, asset_ctx.version)


        return cls(version=asset_ctx.version, property_key=property_key, templates=templates, perimeter=perimeter,
                   start_pos=asset_ctx.start_pos, end_pos=asset_ctx.end_pos)
