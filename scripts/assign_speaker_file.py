## Handles manually labeling the speakers in a file

import argparse
import pysrt
from pydub import AudioSegment
from pydub.playback import play
import sys
import readchar

import random

from typing import Set
from ult import get_speakers_from_srt, get_current_lineSpeaker

def parse_args():
    parser = argparse.ArgumentParser(description="Play SRT lines synced with an MP3 file.")
    parser.add_argument("--srt_file", help="The SRT file to use")
    parser.add_argument("--mp3_file", help="The MP3 file to play")
    parser.add_argument("--random", help="Random mode", action='store_true')
    return parser.parse_args()

def display_menu():
    print("1) Rym    |2) Scott    |3) Emily     |4) Guest   |5) Media     SP/p: Play Audio | q: exit | s:save | x:save+quit")



def replace_srt_speakers(subs: pysrt.SubRipFile, find: str, replace: str) -> pysrt.SubRipFile:
    for sub in subs:
        if sub.text.startswith(find):
            sub.text = sub.text.replace(find, replace)
    return subs

def skip_to_speaker(subs: pysrt.SubRipFile, speaker: str) -> int:
    lines = set()
    for index, sub in enumerate(subs):
        if sub.text.startswith(speaker):
            lines.add(index)
    return random.choice(list(lines))
    

def main():
    args = parse_args()
    current_index = 0
    selected_speaker_index = 0

    # Load SRT file
    subtitles = pysrt.open(args.srt_file)
    speakers = get_speakers_from_srt(subtitles)
    #print (speakers)

    # Load MP3 file
    print (f"loading mp3 {args.mp3_file} .. ")
    audio = AudioSegment.from_mp3(args.mp3_file)
    print ("done")


    print()
    print('-----------------------------------------------------')
    print("Current line:", subtitles[current_index].text)
    print()
    display_menu()
    print (f"Line #: {current_index}      Speakers: {speakers}")
    print('-----------------------------------------------------')



    try:
        while True:
            key = readchar.readkey()
            if key == readchar.key.LEFT:
                current_index = max(0, current_index - 1)
            elif key == readchar.key.RIGHT:
                current_index = min(len(subtitles) - 1, current_index + 1)
            elif key == readchar.key.UP:
                speakers_list = list(speakers)
                selected_speaker_index = max(0, selected_speaker_index - 1)
                current_index = skip_to_speaker(subtitles, speakers_list[selected_speaker_index])
                print (f'Switched to: {speakers_list[selected_speaker_index]}')             
            elif key == readchar.key.DOWN:
                speakers_list = list(speakers)
                selected_speaker_index = min(len(speakers_list) - 1, selected_speaker_index + 1)
                current_index = skip_to_speaker(subtitles, speakers_list[selected_speaker_index])
                print (f'Switched to: {speakers_list[selected_speaker_index]}')      
            elif key.lower() == '1':
                current_speaker = get_current_lineSpeaker(subtitles[current_index].text)
                subtitles = replace_srt_speakers(subtitles, current_speaker + ':', 'Rym:')
                speakers.remove(current_speaker)
                speakers.add('Rym')
                print ("Marked Rym")
            elif key.lower() == '2':
                current_speaker = get_current_lineSpeaker(subtitles[current_index].text)
                subtitles = replace_srt_speakers(subtitles, current_speaker + ':', 'Scott:')
                speakers.remove(current_speaker)
                speakers.add('Scott')                
                print ("Marked Scott")
            elif key.lower() == '3':
                current_speaker = get_current_lineSpeaker(subtitles[current_index].text) 
                subtitles = replace_srt_speakers(subtitles, current_speaker + ':', 'Emily:')
                speakers.remove(current_speaker)
                speakers.add('Emily')                     
                print ("Marked Emily")
            elif key.lower() == '4':
                current_speaker = get_current_lineSpeaker(subtitles[current_index].text)
                subtitles = replace_srt_speakers(subtitles, current_speaker + ':', 'Guest:')
                speakers.remove(current_speaker)
                speakers.add('Guest')                    
                print ("Marked Guest")
            elif key.lower() == '5':
                current_speaker = get_current_lineSpeaker(subtitles[current_index].text)
                subtitles = replace_srt_speakers(subtitles, current_speaker + ':', 'Media:')
                speakers.remove(current_speaker)
                speakers.add('Media')                    
                print ("Marked Media")                
            elif key.lower() == 'q':
                sys.exit()
            elif key.lower() == 's':
                subtitles.save()      
                print ("file saved")          
            elif key.lower() == 'x':
                subtitles.save()      
                print ("file saved")                  
                sys.exit()                
            elif key.lower() == 'p' or readchar.key.SPACE:
                start_time = subtitles[current_index].start.ordinal
                end_time = subtitles[current_index].end.ordinal + 500
                clip = audio[start_time:end_time]
                play(clip)
            else:
                continue
            
            print()
            print('-----------------------------------------------------')
            print("Current line:", subtitles[current_index].text)
            print()
            display_menu()
            print (f"Line #: {current_index}      Speakers: {speakers}")
            print('-----------------------------------------------------')

    except KeyboardInterrupt:
        print("Exiting program")
        sys.exit()

if __name__ == "__main__":
    main()
