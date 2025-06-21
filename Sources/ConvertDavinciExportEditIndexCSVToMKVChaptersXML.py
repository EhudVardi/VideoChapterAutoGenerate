# This script provides a way to convert the export of a Davinci Resolve's timeline's Edit Index Export into an xml chapter file that can be integrated into an mkv video file
# Export timeline edit index list 
#  -> Davinci resolve -> Edit tab -> Index view -> Edit Index tab -> three dots button-> Export Edit Index.. -> save as csv file
# Convert the edit index csv file into mkv xml chapters file 
#  -> run: python ConvertDavinciExportEditIndexCSVToMKVChaptersXML.py --fps [SOURCE_VIDEO_FILE_FPS] [SOURCE_VIDEO_FILE_NAME]

import csv
import os
import argparse
from datetime import timedelta

def timecode_to_seconds(timecode, fps=30.0):
    """Convert timecode (HH:MM:SS:FF) to seconds (frames considered)."""
    h, m, s, f = map(int, timecode.split(':'))
    return h * 3600 + m * 60 + s + f / fps

def seconds_to_mkv_timestamp(seconds):
    """Convert seconds to MKV timestamp format HH:MM:SS.mmm."""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    ms = int(round((seconds - total_seconds) * 1000))
    hh = total_seconds // 3600
    mm = (total_seconds % 3600) // 60
    ss = total_seconds % 60
    return f"{hh:02}:{mm:02}:{ss:02}.{ms:03}"

def process_edit_index(csv_path, fps):
    time_entries = []

    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            track = row.get('V', '').strip()
            record_in = row.get('Record In', '').strip()
            name = row.get('Name', '').strip()

            if track.startswith('V') and record_in:
                seconds = timecode_to_seconds(record_in, fps)
                time_entries.append((seconds, name))

    if not time_entries:
        return []

    # Auto-detect offset (smallest Record In time)
    min_time = min(t[0] for t in time_entries)
    adjusted_entries = []
    seen_times = set()

    for sec, name in time_entries:
        adj_sec = sec - min_time
        if adj_sec not in seen_times:
            seen_times.add(adj_sec)
            adjusted_entries.append((adj_sec, name if name else f"Chapter {len(adjusted_entries) + 1}"))

    # Sort adjusted times
    adjusted_entries.sort()
    return adjusted_entries

def generate_mkv_chapters(timestamps):
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<Chapters>',
           '  <EditionEntry>']

    for i, (sec, chapter_name) in enumerate(timestamps, start=1):
        ts = seconds_to_mkv_timestamp(sec)
        xml.extend([
            '    <ChapterAtom>',
            f'      <ChapterTimeStart>{ts}</ChapterTimeStart>',
            '      <ChapterDisplay>',
            f'        <ChapterString>{chapter_name}</ChapterString>',
            '        <ChapterLanguage>eng</ChapterLanguage>',
            '      </ChapterDisplay>',
            '    </ChapterAtom>'
        ])

    xml.append('  </EditionEntry>')
    xml.append('</Chapters>')
    return '\n'.join(xml)

def main(csv_file, fps=30.0):
    timestamps = process_edit_index(csv_file, fps)
    if not timestamps:
        print("No video cuts found in CSV.")
        return

    xml_content = generate_mkv_chapters(timestamps)

    base = os.path.splitext(os.path.basename(csv_file))[0]
    out_name = f"{base}_chapters.xml"
    with open(out_name, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"MKV chapters XML created: {out_name}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert DaVinci Resolve Edit Index CSV to MKV chapters XML (with offset detection and chapter names).")
    parser.add_argument('csv_file', help='Path to the Edit Index CSV file')
    parser.add_argument('--fps', type=float, default=23.976, help='Timeline FPS (default 23.976)')
    args = parser.parse_args()

    main(args.csv_file, args.fps)
