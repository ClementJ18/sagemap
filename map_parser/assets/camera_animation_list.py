from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ParsingContext


@dataclass
class FreeCameraAnimationCameraFrame:
    frame_index: int
    interpolation_type: str
    position: tuple[float, float, float]
    rotation: tuple[float, float, float, float]
    fov: float

    @classmethod
    def parse(cls, context: "ParsingContext"):
        frame_index = context.stream.readUInt32()
        interpolation_type = context.stream.readFourCc()[::-1]  # Big endian, so reverse
        if interpolation_type not in ["catm", "line"]:
            raise ValueError(f"Invalid interpolation type: {interpolation_type}")

        position = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())
        rotation = (
            context.stream.readFloat(),
            context.stream.readFloat(),
            context.stream.readFloat(),
            context.stream.readFloat(),
        )
        fov = context.stream.readFloat()

        return cls(
            frame_index=frame_index,
            interpolation_type=interpolation_type,
            position=position,
            rotation=rotation,
            fov=fov,
        )


@dataclass
class FreeCameraAnimationFrameData:
    frames: list[FreeCameraAnimationCameraFrame]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        camera_frames_count = context.stream.readUInt32()
        camera_frames = []
        for _ in range(camera_frames_count):
            camera_frames.append(FreeCameraAnimationCameraFrame.parse(context))

        return cls(frames=camera_frames)


@dataclass
class LookAtCameraAnimationLookAtFrame:
    frame_index: int
    interpolation_type: str
    look_at_point: tuple[float, float, float]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        frame_index = context.stream.readUInt32()
        interpolation_type = context.stream.readFourCc()[::-1]
        if interpolation_type not in ["catm", "line"]:
            raise ValueError(f"Invalid interpolation type: {interpolation_type}")

        look_at = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())

        return cls(frame_index=frame_index, interpolation_type=interpolation_type, look_at_point=look_at)


@dataclass
class LookAtCameraAnimationCameraFrame:
    frame_index: int
    interpolation_type: str
    position: tuple[float, float, float]
    roll: float
    fov: float

    @classmethod
    def parse(cls, context: "ParsingContext"):
        frame_index = context.stream.readUInt32()
        interpolation_type = context.stream.readFourCc()[::-1]
        if interpolation_type not in ["catm", "line"]:
            raise ValueError(f"Invalid interpolation type: {interpolation_type}")

        position = (context.stream.readFloat(), context.stream.readFloat(), context.stream.readFloat())
        roll = context.stream.readFloat()
        fov = context.stream.readFloat()

        return cls(
            frame_index=frame_index,
            interpolation_type=interpolation_type,
            position=position,
            roll=roll,
            fov=fov,
        )


@dataclass
class LookAtCameraAnimationFrameData:
    camera_frames: list[LookAtCameraAnimationCameraFrame]
    look_at_frames: list[LookAtCameraAnimationLookAtFrame]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        camera_frames_count = context.stream.readUInt32()
        camera_frames = []
        for _ in range(camera_frames_count):
            camera_frames.append(LookAtCameraAnimationCameraFrame.parse(context))

        look_at_frames_count = context.stream.readUInt32()
        look_at_frames = []
        for _ in range(look_at_frames_count):
            look_at_frames.append(LookAtCameraAnimationLookAtFrame.parse(context))

        return cls(camera_frames=camera_frames, look_at_frames=look_at_frames)


@dataclass
class CameraAnimation:
    animation_type: str
    name: str
    num_frames: int
    start_offset: int
    frame_data: FreeCameraAnimationFrameData | LookAtCameraAnimationFrameData

    @classmethod
    def parse(cls, context: "ParsingContext"):
        animation_type = context.stream.readFourCc()[::-1]
        if animation_type not in ["free", "look"]:
            raise ValueError(f"Unknown camera animation type: {animation_type}")

        name = context.stream.readUInt16PrefixedAsciiString()
        num_frames = context.stream.readUInt32()
        start_offset = context.stream.readUInt32()

        if animation_type == "free":
            frame_data = FreeCameraAnimationFrameData.parse(context)
        elif animation_type == "look":
            frame_data = LookAtCameraAnimationFrameData.parse(context)
        else:
            raise ValueError(f"Unhandled camera animation type: {animation_type}")

        context.logger.debug(
            f"CameraAnimation: {name}, Type: {animation_type}, Frames: {num_frames}, StartOffset: {start_offset}"
        )
        return cls(
            animation_type=animation_type,
            name=name,
            num_frames=num_frames,
            start_offset=start_offset,
            frame_data=frame_data,
        )


@dataclass
class CameraAnimationList:
    asset_name = "CameraAnimationList"

    version: int
    animations: list[CameraAnimation]

    @classmethod
    def parse(cls, context: "ParsingContext"):
        with context.read_asset() as (version, _):
            animations = []
            animation_count = context.stream.readUInt32()
            for _ in range(animation_count):
                animations.append(CameraAnimation.parse(context))

        context.logger.debug(f"Finished parsing {cls.asset_name}")
        return cls(version=version, animations=animations)
