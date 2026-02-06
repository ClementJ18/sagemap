from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext

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
            data = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())
        elif param_type == "Int":
            data = context.stream.readInt32()
        elif param_type == "Texture":
            data = context.stream.readUInt16PrefixedAsciiString()
        else:
            raise ValueError(f"Unknown effect parameter type '{param_type}' for parameter name '{param_name}'.")
        
        return cls(name=param_name, type=param_type, value=data)

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

        return cls(name=name, parameters=parameters if parameters else None, blend_factor=blend_factor, lookup_image=lookup_image)

@dataclass
class PostEffectsChunk:
    asset_name = "PostEffectsChunk"

    version: int
    post_effects: list[PostEffect]
    
    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()

        post_effects_count = context.stream.readUInt32() if version >= 2 else context.stream.readUChar()
        post_effects = []
        for _ in range(post_effects_count):
            post_effects.append(PostEffect.parse(context, version))

        return cls(version=version, post_effects=post_effects)

