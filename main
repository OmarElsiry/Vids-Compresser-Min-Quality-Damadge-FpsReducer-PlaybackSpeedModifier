from moviepy.editor import VideoFileClip, concatenate_videoclips
import time
import multiprocessing

def process_segment(segment):
    return segment.fx(speedx, 1.29).set_fps(19)

if __name__ == "__main__":
    start_time = time.perf_counter()

    # Load the video file
    video = VideoFileClip('11223.mp4')

    # Get the total number of cores
    num_cores = multiprocessing.cpu_count()

    # Calculate 75% of the cores
    target_cores = int(num_cores * 0.75)

    # Calculate the number of segments based on the target cores
    segment_duration = int(video.duration / target_cores)
    
    # Create a list to hold the processed segments
    segments = []

    # Process each segment sequentially
    for i in range(target_cores):
        start = i * segment_duration
        end = min((i + 1) * segment_duration, video.duration)
        segment = video.subclip(start, end)
        processed_segment = process_segment(segment)
        segments.append(processed_segment)

    # Concatenate the processed segments
    final_video = concatenate_videoclips(segments)

    # Write the result to a new file
    final_video.write_videofile('445531111comp.mp4', codec='libx265', audio_codec='aac')

    end_time = time.perf_counter()
    print(f"Processing completed in {end_time - start_time:.2f} seconds")
