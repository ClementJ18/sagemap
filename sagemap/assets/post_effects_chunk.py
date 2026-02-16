from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext, WritingContext


@dataclass
class PostEffectParameter:
    name: str
    type: str
    value: float | tuple[float, float, float, float] | int | str

    @classmethod
    def parse(cls, context: "ParsingContext"):
        param_name = context.stream.readUInt16PrefixedAsciiString()
        param_type = context.stream.readUInt16PrefixedAsciiString()

        if param_type == "Float":
            data = context.stream.readFloat()
        elif param_type == "Float4":
            data = (
                context.stream.readFloat(),
                context.stream.readFloat(),
                context.stream.readFloat(),
                context.stream.readFloat(),
            )
        elif param_type == "Int":
            data = context.stream.readInt32()
        elif param_type == "Texture":
            data = context.stream.readUInt16PrefixedAsciiString()
        else:
            raise ValueError(f"Unknown effect parameter type '{param_type}' for parameter name '{param_name}'.")

        return cls(
            name=param_name,
            type=param_type,
            value=data,
        )

    def write(self, context: "WritingContext"):
        context.stream.writeUInt16PrefixedAsciiString(self.name)
        context.stream.writeUInt16PrefixedAsciiString(self.type)

        if self.type == "Float":
            context.stream.writeFloat(self.value)
        elif self.type == "Float4":
            context.stream.writeFloat(self.value[0])
            context.stream.writeFloat(self.value[1])
            context.stream.writeFloat(self.value[2])
            context.stream.writeFloat(self.value[3])
        elif self.type == "Int":
            context.stream.writeInt32(self.value)
        elif self.type == "Texture":
            context.stream.writeUInt16PrefixedAsciiString(self.value)
        else:
            raise ValueError(f"Unknown effect parameter type '{self.type}' for parameter name '{self.name}'.")


@dataclass
class PostEffect:
    name: str
    parameters: list[PostEffectParameter] | None
    blend_factor: float | None
    lookup_image: str | None

    @classmethod
    def parse(cls, context: "ParsingContext", version: int):
        name = context.stream.readUInt16PrefixedAsciiString()

        parameters = []
        blend_factor = None
        lookup_image = None
        if version >= 2:
            parameter_count = context.stream.readUInt32()
            for _ in range(parameter_count):
                parameters.append(PostEffectParameter.parse(context))
        else:
            blend_factor = context.stream.readFloat()
            lookup_image = context.stream.readUInt16PrefixedAsciiString()

        return cls(
            name=name,
            parameters=parameters if parameters else None,
            blend_factor=blend_factor,
            lookup_image=lookup_image,
        )

    def write(self, context: "WritingContext", version: int):
        context.stream.writeUInt16PrefixedAsciiString(self.name)

        if version >= 2:
            context.stream.writeUInt32(len(self.parameters) if self.parameters else 0)
            if self.parameters:
                for param in self.parameters:
                    param.write(context)
        else:
            context.stream.writeFloat(self.blend_factor)
            context.stream.writeUInt16PrefixedAsciiString(self.lookup_image)


@dataclass
class PostEffectsChunk:
    asset_name = "PostEffectsChunk"

    version: int
    post_effects: list[PostEffect]
    start_pos: int
    end_pos: int

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as asset_ctx:
            post_effects_count = context.stream.readUInt32() if asset_ctx.version >= 2 else context.stream.readUChar()
            post_effects = []
            for _ in range(post_effects_count):
                post_effects.append(PostEffect.parse(context, asset_ctx.version))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(
            version=asset_ctx.version,
            post_effects=post_effects,
            start_pos=asset_ctx.start_pos,
            end_pos=asset_ctx.end_pos,
        )

    def write(self, context: "WritingContext"):
        with context.write_asset(self.asset_name, self.version):
            if self.version >= 2:
                context.stream.writeUInt32(len(self.post_effects))
            else:
                context.stream.writeUChar(len(self.post_effects))

            for effect in self.post_effects:
                effect.write(context, self.version)
