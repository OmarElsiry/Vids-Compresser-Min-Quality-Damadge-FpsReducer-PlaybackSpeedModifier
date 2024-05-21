from moviepy.video.fx.all import speedx
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
import time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor


def process_segment(segment):
    return segment.fx(speedx, 1.285).set_fps(21)


def main():
    start_time = time.perf_counter()

    # Load the original video file
    video = VideoFileClip("11223.mp4")

    # Ask the user if they want to adjust the FPS
    adjust_fps = input("Do you want to adjust the FPS? (y/n): ").lower()
    if adjust_fps == "y":
        fps = int(input("Enter the desired FPS: "))
    else:
        fps = 21  # Default FPS

    # Adjust the FPS globally if needed
    video = video.set_duration(video.duration).subclip(0, video.duration).set_fps(fps)

    # Ask the user if they want to cut scenes
    cut_scenes = input("Do you want to cut scenes? (y/n): ").lower()
    if cut_scenes == "y":
        # Cut scene for part1
        part1_start = float(input("Enter the start time for part1 (HH:MM:SS): "))
        part1_end = float(input("Enter the end time for part1 (HH:MM:SS): "))
        part1 = video.subclip(part1_start, part1_end)

        # Cut scene for part2
        part2_start = float(input("Enter the start time for part2 (HH:MM:SS): "))
        part2_end = float(input("Enter the end time for part2 (HH:MM:SS): "))
        part2 = video.subclip(part2_start, part2_end)
    else:
        # Use full video without cutting
        # Calculate the midpoint of the video duration
        midpoint = video.duration / 2
        # Extract the first half of the video
        part1 = video.subclip(0, midpoint)
        # Extract the second half of the video
        part2 = video.subclip(midpoint, video.duration)

    # Ask the user if they want the video to be muted
    mute_video = input("Do you want the video to be muted? (y/n): ").lower()
    if mute_video == "y":
        # Mute the video by setting the audio track to None
        part1 = part1.without_audio()
        part2 = part2.without_audio()

    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        # Process the first part
        future_list_part1 = [
            executor.submit(
                process_segment,
                part1.subclip(
                    i * int(part1.duration / multiprocessing.cpu_count()),
                    min(
                        (i + 1) * int(part1.duration / multiprocessing.cpu_count()),
                        part1.duration,
                    ),
                ),
            )
            for i in range(multiprocessing.cpu_count())
        ]

        # Process the second part
        future_list_part2 = [
            executor.submit(
                process_segment,
                part2.subclip(
                    j * int(part2.duration / multiprocessing.cpu_count()),
                    min(
                        (j + 1) * int(part2.duration / multiprocessing.cpu_count()),
                        part2.duration,
                    ),
                ),
            )
            for j in range(multiprocessing.cpu_count())
        ]

    # Collect results from futures
    segments_part1 = [future.result() for future in future_list_part1]
    segments_part2 = [future.result() for future in future_list_part2]

    # Concatenate the processed segments from both parts
    final_video = concatenate_videoclips(segments_part1 + segments_part2)

    # Write the result to a new file
    final_video.write_videofile("44553comp.mp4", codec="libx265", audio_codec="aac")

    end_time = time.perf_counter()
    print(f"Processing completed in {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
