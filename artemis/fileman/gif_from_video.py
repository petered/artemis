import subprocess
import os
import argparse


def extract_frames(video_path, time_points, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, time_point in enumerate(time_points):
        output_frame = os.path.join(output_dir, f"frame_{i:04d}.png")
        print(f"Extracting frame at time point {time_point} to {output_frame}...")
        ffmpeg_command = [
            "ffmpeg", "-i", video_path, "-ss", time_point, "-vframes", "1", output_frame
        ]
        subprocess.run(ffmpeg_command)


def create_gif(frames_dir, output_gif, fps):
    palette = os.path.join(frames_dir, "palette.png")
    output_gif = os.path.expanduser(output_gif)

    # Generate the palette
    ffmpeg_palette_command = [
        "ffmpeg", "-framerate", str(fps), "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-vf", "scale=500:-1:flags=lanczos,palettegen", "-y", palette
    ]
    subprocess.run(ffmpeg_palette_command)

    # Create the GIF using the palette
    ffmpeg_gif_command = [
        "ffmpeg", "-framerate", str(fps), "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-i", palette, "-lavfi", "scale=500:-1:flags=lanczos [x]; [x][1:v] paletteuse",
        output_gif
    ]
    subprocess.run(ffmpeg_gif_command)


def main():
    """
    Exapmle usage:
    python gif_from_video.py video.mp4 0:43,1:25,3:14 --fps 1
    """
    parser = argparse.ArgumentParser(description="Create a GIF from selected time points in a video.")
    parser.add_argument("video_path", type=str, help="Path to the input video file.")
    parser.add_argument("time_points", type=str, help="Comma-separated list of time points (e.g., '0:43,1:25,3:14').")
    parser.add_argument("--fps", type=int, default=1, help="Frames per second for the GIF.")
    # Output file
    parser.add_argument("--output_gif", type=str, default="output.gif", help="Path to the output GIF file.")

    args = parser.parse_args()

    video_path = args.video_path
    time_points = args.time_points.split(',')
    fps = args.fps

    output_dir = "frames"
    # output_gif = "output.gif"

    extract_frames(video_path, time_points, output_dir)
    create_gif(output_dir, args.output_gif, fps)


if __name__ == "__main__":

    main()
