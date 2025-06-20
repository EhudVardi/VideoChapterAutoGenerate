import subprocess
import re
import sys
import os

# Set your ffmpeg.exe full path here
ffmpeg_path = r'E:\Programs\ffmpeg\bin\ffmpeg'
mkvmerge_path = r'C:\Program Files\MKVToolNix\mkvmerge'

def run_ffmpeg_scene_detection(video_file, scene_changes_file, scene_detection_threshold):
    """Runs ffmpeg to detect scene changes and stores them in 'scene_changes.txt'"""
    ffmpeg_command = [
        ffmpeg_path,
        '-i', video_file,
        '-vf', f'select=gt(scene\\,{scene_detection_threshold}),showinfo',
        '-f', 'null', '-'
    ]

    try:
        # Run ffmpeg and capture output
        result = subprocess.run(ffmpeg_command, capture_output=True, text=True, check=True)

        # Filter stderr for lines containing 'showinfo'
        with open(scene_changes_file, 'w') as f:
            for line in result.stderr.splitlines():
                if 'showinfo' in line:
                    f.write(line + '\n')

        print(f"Scene changes detected and saved to {scene_changes_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        cleanup([scene_changes_file])
        exit_program(1)

def extract_timestamps(scene_changes_file):
    """Extract timestamps from ffmpeg scene detection output"""
    timestamps = []
    time_pattern = re.compile(r'pts_time:(\d+\.\d+)')

    with open(scene_changes_file, 'r') as file:
        for line in file:
            match = time_pattern.search(line)
            if match:
                timestamps.append(float(match.group(1)))

    return timestamps

def format_time(seconds):
    """Formats the time in HH:MM:SS.ms for the XML file"""
    ms = int((seconds % 1) * 1000)
    seconds = int(seconds)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f'{hours:02}:{mins:02}:{secs:02}.{ms:03}'

def generate_chapter_xml(timestamps, xml_file='chapters.xml'):
    """Generates an MKVToolNix compatible XML chapter file"""
    with open(xml_file, 'w') as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<Chapters>\n')
        f.write('  <EditionEntry>\n')

        for i, timestamp in enumerate(timestamps):
            f.write('    <ChapterAtom>\n')
            f.write(f'      <ChapterTimeStart>{format_time(timestamp)}</ChapterTimeStart>\n')
            f.write('      <ChapterDisplay>\n')
            f.write(f'        <ChapterString>Chapter {i + 1}</ChapterString>\n')
            f.write('        <ChapterLanguage>eng</ChapterLanguage>\n')
            f.write('      </ChapterDisplay>\n')
            f.write('    </ChapterAtom>\n')

        f.write('  </EditionEntry>\n')
        f.write('</Chapters>\n')

    print(f"Chapter XML file created: {xml_file}")
    return xml_file

def create_mkv_with_chapters(input_video, chapters_xml, output_video):
    """Uses MKVToolNix to create a new MKV file with chapters"""
    mkv_command = [
        mkvmerge_path,
        '-o', output_video,
        '--chapters', chapters_xml,
        input_video
    ]

    try:
        subprocess.run(mkv_command, check=True)
        print(f"New MKV file created with chapters: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error running mkvmerge: {e}")
        cleanup([chapters_xml])
        exit_program(1)

def cleanup(files_to_remove):
    """Deletes temporary files if they exist"""
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Deleted temporary file: {file}")
            except OSError as e:
                print(f"Error deleting {file}: {e}")

def exit_program(status=0):
    """Custom exit to pause before quitting"""
    input(f'Program ended with status {status}\nPress Enter to exit...')
    sys.exit(status)

def main(video_file, scene_detection_threshold):
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.")
        exit_program(1)

    scene_changes_file = "scene_changes.txt"
    video_file_no_ext = os.path.splitext(video_file)[0]
    chapters_xml_filename = video_file_no_ext + ".xml"

    try:
        if os.path.exists(chapters_xml_filename):
            print(f"Chapters XML file '{chapters_xml_filename}' already exists. Skipping scene detection.")
        else:
            print("Running scene detection..")
            run_ffmpeg_scene_detection(video_file, scene_changes_file, scene_detection_threshold)

            print("Extracting timestamps..")
            timestamps = extract_timestamps(scene_changes_file)

            if not timestamps:
                print("No scene changes detected.")
                cleanup([scene_changes_file])
                exit_program(1)

            print("Generating chapters XML file..")
            generate_chapter_xml(timestamps, chapters_xml_filename)

        print("Embedding chapters into a new MKV video file..")
        output_video = video_file_no_ext + "_with_chapters.mkv"
        create_mkv_with_chapters(video_file, chapters_xml_filename, output_video)

    finally:
        print("Cleaning up..")
        cleanup([scene_changes_file])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python DetectChaptersAndGenerateMkv.py <video_file> (optional)<scene_detection_threshold>")
        exit_program(1)

    video_file = sys.argv[1]

    try:
        scene_detection_threshold = float(sys.argv[2]) if len(sys.argv) >= 3 else 0.3
    except ValueError:
        print("Scene detection threshold must be a number.")
        exit_program(1)

    print(f"Executing on input file '{video_file}' with threshold {scene_detection_threshold}.")
    main(video_file, scene_detection_threshold)

    exit_program(0)
