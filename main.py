from moviepy.video.fx.all import speedx
from moviepy.editor import VideoFileClip, concatenate_videoclips
import time
from concurrent.futures import ThreadPoolExecutor
import customtkinter as ctk
from datetime import datetime
from tkinter import filedialog, END, messagebox
import os

def process_segment(segment, speed, fps):
    return segment.fx(speedx, speed).set_fps(fps)

def select_file():
    file_path = filedialog.askopenfilename(
        title="Select the input video file",
        filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.gif"), ("All files", "*.*")]
    )
    if file_path:
        entry_file_path.delete(0, END)
        entry_file_path.insert(0, file_path)

def toggle_cut_scenes():
    if checkbox_cut_scenes_var.get():
        frame_cut_scenes.pack(pady=(10, 10))
    else:
        frame_cut_scenes.pack_forget()

def toggle_speed():
    if checkbox_speed_var.get():
        frame_speed.pack(pady=(10, 10))
    else:
        frame_speed.pack_forget()

def reset_gui():
    entry_file_path.delete(0, END)
    entry_fps.delete(0, END)
    checkbox_speed_var.set(False)
    checkbox_cut_scenes_var.set(False)
    checkbox_mute_video_var.set(False)
    toggle_speed()
    toggle_cut_scenes()
    processing_time_label.configure(text="")

def start_processing():
    input_file_path = entry_file_path.get()

    if not input_file_path:
        messagebox.showerror("Error", "No file selected. Exiting.")
        return

    start_time = time.perf_counter()

    video = VideoFileClip(input_file_path)
    fps = int(entry_fps.get()) if entry_fps.get() else 21
    speed = float(entry_speed.get()) if checkbox_speed_var.get() and entry_speed.get() else 1.0
    video = video.set_fps(fps)

    if checkbox_cut_scenes_var.get():
        part1_start = float(entry_part1_start.get())
        part1_end = float(entry_part1_end.get())
        part1 = video.subclip(part1_start, part1_end)

        part2_start = float(entry_part2_start.get())
        part2_end = float(entry_part2_end.get())
        part2 = video.subclip(part2_start, part2_end)
    else:
        midpoint = video.duration / 2
        part1 = video.subclip(0, midpoint)
        part2 = video.subclip(midpoint, video.duration)

    mute_video = checkbox_mute_video_var.get()
    if mute_video:
        part1 = part1.without_audio()
        part2 = part2.without_audio()

    num_workers = os.cpu_count()

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_list_part1 = [
            executor.submit(
                process_segment,
                part1.subclip(
                    i * int(part1.duration / num_workers),
                    min((i + 1) * int(part1.duration / num_workers), part1.duration),
                ),
                speed,
                fps,
            )
            for i in range(num_workers)
        ]

        future_list_part2 = [
            executor.submit(
                process_segment,
                part2.subclip(
                    j * int(part2.duration / num_workers),
                    min((j + 1) * int(part2.duration / num_workers), part2.duration),
                ),
                speed,
                fps,
            )
            for j in range(num_workers)
        ]

        segments_part1 = [future.result() for future in future_list_part1]
        segments_part2 = [future.result() for future in future_list_part2]
        
    final_video = concatenate_videoclips(segments_part1 + segments_part2)

    current_time = int(datetime.now().timestamp())
    output_file_name = f"{os.path.basename(input_file_path).split('.')[0]}_{current_time}.mp4"
    output_file_path = os.path.join(os.path.dirname(input_file_path), output_file_name)
    final_video.write_videofile(output_file_path, codec="libx265", audio_codec="aac")

    end_time = time.perf_counter()
    processing_time = f"Processing completed in {end_time - start_time:.2f} seconds"
    print(processing_time)
    processing_time_label.configure(text=processing_time)

    def open_output_file():
        os.startfile(output_file_path)

    def open_output_folder():
        os.startfile(os.path.dirname(output_file_path))

    ctk.CTkButton(app, text="Open Output File", command=open_output_file).pack(pady=(20, 10))
    ctk.CTkButton(app, text="Open Output Folder", command=open_output_folder).pack(pady=(0, 10))
    ctk.CTkButton(app, text="Process Another Video", command=reset_gui).pack(pady=(10, 10))

app = ctk.CTk()
app.geometry("500x800")
app.title("Video Processor")

# Input file path
frame_input = ctk.CTkFrame(app)
frame_input.pack(pady=(20, 10))
ctk.CTkLabel(frame_input, text="Input File:").pack(pady=(5, 5))
entry_file_path = ctk.CTkEntry(frame_input, width=400)
entry_file_path.pack(pady=(5, 5))
ctk.CTkButton(frame_input, text="Select File", command=select_file).pack(pady=(5, 10))

# FPS
frame_fps = ctk.CTkFrame(app)
frame_fps.pack(pady=(10, 10))
ctk.CTkLabel(frame_fps, text="FPS:").pack(pady=(5, 5))
entry_fps = ctk.CTkEntry(frame_fps, width=100)
entry_fps.pack(pady=(5, 5))

# Speed toggle
checkbox_speed_var = ctk.BooleanVar()
frame_speed_toggle = ctk.CTkFrame(app)
frame_speed_toggle.pack(pady=(10, 10))
ctk.CTkCheckBox(frame_speed_toggle, text="Adjust Speed", variable=checkbox_speed_var, command=toggle_speed).pack(pady=(5, 5))

# Speed
frame_speed = ctk.CTkFrame(app)
label_speed = ctk.CTkLabel(frame_speed, text="Speed:")
label_speed.pack(pady=(5, 5))
entry_speed = ctk.CTkEntry(frame_speed, width=100)
entry_speed.pack(pady=(5, 5))

# Cut scenes
checkbox_cut_scenes_var = ctk.BooleanVar()
frame_cut_scenes_toggle = ctk.CTkFrame(app)
frame_cut_scenes_toggle.pack(pady=(10, 10))
ctk.CTkCheckBox(frame_cut_scenes_toggle, text="Cut Scenes", variable=checkbox_cut_scenes_var, command=toggle_cut_scenes).pack(pady=(5, 5))

# Part 1 start and end
frame_cut_scenes = ctk.CTkFrame(app)
label_part1_start = ctk.CTkLabel(frame_cut_scenes, text="Part 1 Start (seconds):")
label_part1_start.pack(pady=(5, 5))
entry_part1_start = ctk.CTkEntry(frame_cut_scenes, width=100)
entry_part1_start.pack(pady=(5, 5))

label_part1_end = ctk.CTkLabel(frame_cut_scenes, text="Part 1 End (seconds):")
label_part1_end.pack(pady=(5, 5))
entry_part1_end = ctk.CTkEntry(frame_cut_scenes, width=100)
entry_part1_end.pack(pady=(5, 5))

# Part 2 start and end
label_part2_start = ctk.CTkLabel(frame_cut_scenes, text="Part 2 Start (seconds):")
label_part2_start.pack(pady=(5, 5))
entry_part2_start = ctk.CTkEntry(frame_cut_scenes, width=100)
entry_part2_start.pack(pady=(5, 5))

label_part2_end = ctk.CTkLabel(frame_cut_scenes, text="Part 2 End (seconds):")
label_part2_end.pack(pady=(5, 5))
entry_part2_end = ctk.CTkEntry(frame_cut_scenes, width=100)
entry_part2_end.pack(pady=(5, 5))

# Mute video
frame_mute_video = ctk.CTkFrame(app)
frame_mute_video.pack(pady=(10, 10))
checkbox_mute_video_var = ctk.BooleanVar()
checkbox_mute_video = ctk.CTkCheckBox(frame_mute_video, text="Mute Video", variable=checkbox_mute_video_var)
checkbox_mute_video.pack(pady=(5, 5))

# Processing time label
processing_time_label = ctk.CTkLabel(app, text="")
processing_time_label.pack(pady=(10, 10))

# Start processing
frame_start = ctk.CTkFrame(app)
frame_start.pack(pady=(10, 20))
ctk.CTkButton(frame_start, text="Start Processing", command=start_processing).pack(pady=(10, 10))

# Initially hide advanced options
frame_speed.pack_forget()
frame_cut_scenes.pack_forget()

app.mainloop()
