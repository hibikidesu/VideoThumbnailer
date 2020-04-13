import ffmpeg
from ffprobe import FFProbe
import argparse
import os
from datetime import timedelta


def timestamp_to_seconds(video_time: str) -> int:
    """Gets a video timestamp and returns it as an integer in seconds"""
    h, m, s = video_time.split(":")
    hours = (int(h) * 3600)
    minutes = int(m) * 60
    seconds = float(s)
    return int(hours + minutes + seconds)


def seconds_to_timestamp(video_time: int) -> str:
    """Reverse of timestamp_to_seconds"""
    hours, remainder = divmod(video_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}:{:02}:{:02}.00".format(hours, minutes, seconds)


def _generate_individual_thumb(save_name: str, video_p: str, ts: str):
    """Generates an individual thumbnail with a given name, video path, timestamp"""
    stream = ffmpeg.input(video_p, ss=ts)
    stream = ffmpeg.output(stream, save_name, vframes=1)
    ffmpeg.run(stream)


def generate_thumbnails(amount: int, video_path: str, file_format: str = "png") -> int:
    """
    Generates thumbnails based with the amount of thumbnails to generate
    and the video path

    In:
        amount - Amount of images to create
        video_path - Direct path to video

    Out:
        Error codes can either be:
            0 = Success
            1 = Unknown location
            2 = Unknown duration (can't get video duration
    """
    if not os.path.exists(video_path):
        return 1

    probe = FFProbe(video_path)
    duration = probe.metadata.get("Duration")
    if not duration:
        return 2

    video_time = timestamp_to_seconds(duration)
    time_split = video_time / amount

    video_name = video_path.partition(".")[0]

    # Will take a megu long time if run 2nd option so get each individual frame at each point here
    if video_time >= 1800:
        for x in range(amount):
            timestamp = seconds_to_timestamp(int(time_split * x))
            _generate_individual_thumb(
                "{}_{}.{}".format(video_name, x, file_format),
                video_path,
                timestamp
            )
    else:
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.filter(stream, "fps", fps=1 / time_split)
        stream = ffmpeg.output(stream, "{}_%d.{}".format(video_name, file_format))
        ffmpeg.run(stream)

    return 0


def main():
    parser = argparse.ArgumentParser(description="Creates x amount of thumbnails based video length")
    parser.add_argument("amount", type=int, help="Amount of thumbnails to generate")
    parser.add_argument("video_path", help="Video to process")
    parser.add_argument("-file_format", type=str, help="Video to process", default="png")
    args = parser.parse_args()

    code = generate_thumbnails(args.amount, args.video_path, args.file_format)
    print([
        "Generated thumbnails",
        "Invalid video path!",
        "Invalid video duration!"
    ][code])
