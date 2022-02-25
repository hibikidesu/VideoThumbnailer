import ffmpeg
import subprocess
import argparse
import os
from pathlib import Path


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


def _generate_individual_thumb(save_name: str, video_p: str, ts: str, mon: bool):
    """Generates an individual thumbnail with a given name, video path, timestamp"""
    stream = ffmpeg.input(video_p, ss=ts)
    if mon:
        stream = ffmpeg.filter(stream, "scale", 320, -1)
    stream = ffmpeg.output(stream, save_name, vframes=1).overwrite_output()
    ffmpeg.run(stream)


def _get_video_duration(video_p: str) -> str:
    """Get a video duration based off of file path"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", "-sexagesimal",
         video_p
         ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return result.stdout.decode()


def generate_thumbnails(amount: int, video_path: str, force_slow: bool,
                        out_dir: str, file_format: str = "png", montage: bool = False) -> int:
    """
    Generates thumbnails based with the amount of thumbnails to generate
    and the video path

    In:
        amount - Amount of images to create
        video_path - Direct path to video
        force_slow - Force slower method if video over 30min
        out_dir - Output directory
        file_format - Image file format to output

    Out:
        Error codes can either be:
            0 = Success
            1 = Unknown location
            2 = Unknown duration (can't get video duration
    """
    if not os.path.exists(video_path):
        return 1

    if not os.path.exists(out_dir):
        Path(out_dir).mkdir(parents=True, exist_ok=True)

    duration = _get_video_duration(video_path)
    if not duration:
        return 2

    video_time = timestamp_to_seconds(duration)
    time_split = video_time / amount

    video_name = video_path.partition(".")[0]

    # Will take a megu long time if run 2nd option so get each individual frame at each point here
    if not force_slow:
        for x in range(amount):
            timestamp = seconds_to_timestamp(int(time_split * (x + 1)))
            _generate_individual_thumb(
                os.path.join(out_dir, "s{:02d}.{}".format(x+1, file_format)),
                video_path,
                timestamp,
                montage
            )
    else:
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.filter(stream, "fps", fps=1 / time_split)
        if montage:
            ffmpeg.filter(stream, "scale", 320, -1)
        stream = ffmpeg.output(
            stream, os.path.join(out_dir, "s%d.{}".format(file_format))
        ).overwrite_output()
        ffmpeg.run(stream)

    return 0


def main():
    parser = argparse.ArgumentParser(description="Creates x amount of thumbnails based video length")
    parser.add_argument("video_path", help="Video to process")
    parser.add_argument("amount", type=int, help="Amount of thumbnails to generate")
    parser.add_argument("-file_format", type=str, help="Video to process", default="png")
    parser.add_argument("-slow", help="Force slower method on videos over 30min long", action="store_true")
    parser.add_argument("-montage", help="Montage mode, lower res", action="store_true")
    parser.add_argument("-output", "-o", type=str, help="Image output directory", default=".")
    args = parser.parse_args()

    code = generate_thumbnails(args.amount, args.video_path, args.slow, args.output, args.file_format, args.montage)
    print([
        "Generated thumbnails",
        "Invalid video path!",
        "Invalid video duration!"
    ][code])
