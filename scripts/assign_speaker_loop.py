import os
import pysrt
import time
# Define your directory paths
mp3_dir = '../mp3'
srt_dir = '../srt/labeled/new'
from ult import get_speakers_from_srt, get_current_lineSpeaker

default_speakers = ['Speaker 0', 'Speaker 1', 'Speaker 2', 'Speaker 3', 'Speaker 4', 'Speaker 5', 'Speaker 6', 'Speaker 7', 'Speaker 8']
skip_list = [
    '20061005.srt'
]
# Loop through all files in the srt directory
for root, dirs, files in os.walk(srt_dir):
    for filename in sorted(files):
        if filename.endswith('.srt'):
            if filename in skip_list:
                print (f'skipping {filename}')
                continue
            subtitles_file_path = os.path.join(root, filename)
            print (subtitles_file_path)
            subtitles = pysrt.open(subtitles_file_path)
            speakers = get_speakers_from_srt(subtitles)
            del subtitles
            has_default_speakers = speakers.intersection(default_speakers)
            if (has_default_speakers):
                print (f'{filename} has defualt speakers {speakers}, please assign speakers')
                basename = os.path.splitext(filename)[0]
                mp3_file = os.path.join(mp3_dir, basename + '.mp3')
                #os.system(f'python diarize_kero.py -a {os.path.join(args.directory, mp3_file)} --temp-dir="{temp_outputs}"')
                os.system(f'python assign_speaker_file.py --srt_file="{subtitles_file_path}" --mp3_file="{mp3_file}"')
                time.sleep(1)
                #break
