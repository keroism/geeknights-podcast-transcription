## tries to automatally label speakers based on commonly spoken lines

import os
import pysrt
from typing import List, Optional
from ult import get_speakers_from_srt, get_current_lineSpeaker



srt_dir = '../srt/labeled/new'
mp3_dir = '../mp3'


stuff_rym_says = ['GeekNights is not one, but four different shows',
                  'catch-alls for various rants and tomfoolery',
                  'and indiscriminate Thursdays'
                  'Creative Commons Attribution 4.0 International License',
                  'And the Patreon patrons for this episode of Geek Nights are'
                  ] 

stuff_scott_says = ['But unlike those other late shows',
                    'creative commons attribution non-commercial',
                    'distributed under a Creative Commons attribution 3.0 license',
                    'GeekNights is distributed under a creative commons attribution'
                    ]

default_speakers = ['Speaker 0', 'Speaker 1', 'Speaker 2', 'Speaker 3', 'Speaker 4', 'Speaker 5', 'Speaker 6', 'Speaker 7', 'Speaker 8']

def main():
    for root, dirs, files in os.walk(srt_dir):
        for filename in sorted(files):
            
            basename = os.path.splitext(filename)[0]
            mp3_file = os.path.join(mp3_dir, basename + '.mp3')
            if filename.endswith('.srt'):
                subtitles_file_path = os.path.join(root, filename)
                subtitles = pysrt.open(subtitles_file_path )
                speakers = get_speakers_from_srt(subtitles)
                
                has_default_speakers = speakers.intersection(default_speakers)
                if not has_default_speakers:
                    print(f"DEBUG: {filename} already good")
                    continue            

                # cowardly skip if not exactly 2 speakers
                if len (speakers) != 2:
                    print(f"DEBUG: {filename} num speakers != 2")
                    continue

                #Scott
                results = findTextList(subtitles, stuff_scott_says)
                if results:
                    #print(f'DEBUG: found {results.text}')
                    #continue
                    linespeaker = get_current_lineSpeaker(results.text)
                    findReplaceLineStart(subtitles, f'{linespeaker}:', 'Scott:')
                    subtitles.save(subtitles_file_path, encoding='utf-8')
                    print(f'DEBUG: processed {srt_dir}/{filename}')
                else:
                    print(f'DEBUG: {srt_dir}/{filename} {mp3_file} couldn\'t align text Scott')

                # Rym
                results = findTextList(subtitles, stuff_rym_says)
                if results:
                    #print(f'DEBUG: found {results.text}')
                    #continue
                    linespeaker = get_current_lineSpeaker(results.text)
                    findReplaceLineStart(subtitles, f'{linespeaker}:', 'Rym:')
                    subtitles.save(subtitles_file_path, encoding='utf-8')
                    print(f'DEBUG: processed {srt_dir}/{filename}')
                else:
                    print(f'DEBUG: {srt_dir}/{filename} {mp3_file} couldn\'t align text Rym')


                # free up resources??
                del subtitles

def findReplaceLineStart(subs: pysrt.SubRipFile, needle: str, replacement: str ):
    count = 0
    for sub in subs:
        if sub.text.startswith(needle):
            sub.text = sub.text.replace(needle, replacement)
            count += 1
    return count
    

def findTextList(subs: pysrt.SubRipFile,  search_terms: List[str]) -> Optional[pysrt.SubRipItem]:
    
    clean_search_terms = [term.lower().replace(',', '') for term in search_terms]

    for subtitle in subs:
        subtitle_text_clean = subtitle.text.lower().replace(',', '')
        if any(term.lower() in subtitle_text_clean for term in clean_search_terms):
            return subtitle
    return None

if __name__ == "__main__":
    main()
