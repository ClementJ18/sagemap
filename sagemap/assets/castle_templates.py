from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext, WritingContext

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

        return cls(
            name=name,
            template_name=template_name,
            offset=offset,
            angle=angle,
            priority=priority,
            phase=phase,
        )
    
    def write(self, context: "WritingContext", version: int):
        context.stream.writeUInt16PrefixedAsciiString(self.name)
        context.stream.writeUInt16PrefixedAsciiString(self.template_name)
        context.stream.writeVector3(self.offset)
        context.stream.writeFloat(self.angle)

        if version >= 4:
            context.stream.writeUInt32(self.priority)
            context.stream.writeUInt32(self.phase)

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

        return cls(
            x=x,
            y=y,
            z=z,
        )
    
    def write(self, context: "WritingContext", version: int):
        if version >= 3:
            context.stream.writeFloat(self.x)
            context.stream.writeFloat(self.y)
        else:
            context.stream.writeInt32(int(self.x))
            context.stream.writeInt32(int(self.y))
            context.stream.writeInt32(int(self.z))

@dataclass
class CastlePerimeter:
    has_perimeter: bool
    name: str | None
    perimeter_points: list[PerimeterPoint]

    @classmethod
    def parse(cls, context: "ParsingContext", version: int):
        has_perimeter = context.stream.readBoolUInt32Checked()
        
        name = None
        perimeter_points = []

        if has_perimeter:
            name = context.stream.readUInt16PrefixedAsciiString()
            perimeter_point_count = context.stream.readUInt32()
            
            for _ in range(perimeter_point_count):
                perimeter_points.append(PerimeterPoint.parse(context, version))

        return cls(
            has_perimeter=has_perimeter,
            name=name,
            perimeter_points=perimeter_points,
        )
    
    def write(self, context: "WritingContext", version: int):
        context.stream.writeBoolUInt32Checked(self.has_perimeter)
        if self.has_perimeter:
            context.stream.writeUInt16PrefixedAsciiString(self.name if self.name else "")
            context.stream.writeUInt32(len(self.perimeter_points))
            for point in self.perimeter_points:
                point.write(context, version)


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
            property_key = context.parse_asset_property_key()
            template_count = context.stream.readUInt32()
            
            templates = []
            for _ in range(template_count):
                templates.append(CastleTemplate.parse(context, asset_ctx.version))

            perimeter = None
            if asset_ctx.version >= 2:
                perimeter = CastlePerimeter.parse(context, asset_ctx.version)


        return cls(
            version=asset_ctx.version, 
            property_key=property_key, 
            templates=templates, 
            perimeter=perimeter,
            start_pos=asset_ctx.start_pos, 
            end_pos=asset_ctx.end_pos
        )
    
    def write(self, context: "WritingContext"):
        with context.write_asset(self.asset_name, self.version):
            context.write_asset_property_key(self.property_key)
            context.stream.writeUInt32(len(self.templates))
            for template in self.templates:
                template.write(context, self.version)

            if self.version >= 2:
                self.perimeter.write(context, self.version)
    

