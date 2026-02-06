from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class NamedCamera:
    look_at_point: tuple[float, float, float]
    name: str
    pitch: float
    roll: float
    yaw: float
    zoom: float
    fov: float
    unknown: float

    @classmethod
    def parse(cls, context: "ParsingContext"):
        look_at_point = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())
        name = context.stream.readUInt16PrefixedAsciiString()
        pitch = context.stream.readFloat()
        roll = context.stream.readFloat()
        yaw = context.stream.readFloat()
        zoom = context.stream.readFloat()
        fov = context.stream.readFloat()
        unknown = context.stream.readFloat()

        context.logger.debug(f"NamedCamera: {name}, LookAt: {look_at_point}, Pitch: {pitch}, Roll: {roll}, Yaw: {yaw}, Zoom: {zoom}, FOV: {fov}")
        return cls(
            look_at_point=look_at_point,
            name=name,
            pitch=pitch,
            roll=roll,
            yaw=yaw,
            zoom=zoom,
            fov=fov,
            unknown=unknown
        )

@dataclass
class NamedCameras:
    asset_name = "NamedCameras"

    version: int
    cameras: list[NamedCamera]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        version, _ = context.parse_asset_header()

        cameras = []
        camera_count = context.stream.readUInt32()
        for _ in range(camera_count):
            cameras.append(NamedCamera.parse(context))

        return cls(version=version, cameras=cameras)