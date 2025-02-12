import pysrt
from typing import Set
import sqlite3
import os
from datetime import datetime
from markdownify import markdownify as md
import re

def get_speakers_from_srt(subs: pysrt.SubRipFile) -> Set[int]:
    speakers = set()
    for sub in subs:
        line = sub.text
        parts = line.split(':', 1)
        speaker = parts[0]
        speakers.add(speaker)

    return speakers

# return speaker with the trailing ":"
def get_current_lineSpeaker(line: str) -> str:
    parts = line.split(':', 1)    
    speaker = parts[0] 
    return speaker

## Converts the subrip objects into text arrays that are hopefully better to finetune LLM, make embeddings, etc
## subs = pysrt object
## collapse = collapse contiguous lines from the same speaker
def process_srt(subs, collapse):
    
    processed_lines = []
    current_speaker = None
    current_text = []

    for sub in subs:
        if ':' in sub.text:
            speaker, text = sub.text.split(':', 1)
            if collapse and speaker == current_speaker:
                current_text.append(text.strip())
            else:
                if current_speaker is not None:
                    processed_lines.append(f"{current_speaker}: {' '.join(current_text)}")
                current_speaker = speaker
                current_text = [text.strip()]
        else:
            current_text.append(sub.text.strip())

    if current_speaker is not None:
        processed_lines.append(f"{current_speaker}: {' '.join(current_text)}")

    return processed_lines

def get_list_of_srts(srt_dir: str) -> list:

    srt_files = []
    for root, dirs, files in os.walk(srt_dir):
        for filename in sorted(files):
            if filename.endswith('.srt'):
                srt_files.append(os.path.join(root, filename))
    return srt_files

##
# collapse = collapse contiguous lines from the same speaker
def srtfile_to_text(subs_filepath: str, collapse: bool) -> str:
    
    subs = pysrt.open(subs_filepath)

    processed_lines = []
    current_speaker = None
    current_text = []

    for sub in subs:
        if ':' in sub.text:
            speaker, text = sub.text.split(':', 1)
            if collapse and speaker == current_speaker:
                current_text.append(text.strip())
            else:
                if current_speaker is not None:
                    processed_lines.append(f"{current_speaker}: {' '.join(current_text)}")
                current_speaker = speaker
                current_text = [text.strip()]
        else:
            current_text.append(sub.text.strip())

    if current_speaker is not None:
        processed_lines.append(f"{current_speaker}: {' '.join(current_text)}")

    return '\n'.join(processed_lines)



def remove_markdown_links(text):
    # This pattern matches markdown links: [text](url)
    pattern = r'\[([^\]]+)\]\([^)]+\)'
    # Replace with just the text inside square brackets
    return re.sub(pattern, r'\1', text)

def get_episode_info(db_path: str, showid: int) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get episode and show information
    episode_query = """
    SELECT e.title, e.pub_date, e.showid, s.title, e.body, e.id
    FROM podcast_episode e
    JOIN podcast_show s ON e.show_id = s.id
    WHERE e.showid = ?
    """
    
    cursor.execute(episode_query, (showid,))
    episode_data = cursor.fetchone()
    
    if not episode_data:
        conn.close()
        return "Episode not found"
    
    title, pub_date, ep_showid, show_title, body, episode_id = episode_data
    body = md(body)
    # Get things of the day
    things_query = """
    SELECT author, title, url
    FROM things_thing
    WHERE episode_id = ?
    ORDER BY id
    """
    
    cursor.execute(things_query, (episode_id,))
    things = cursor.fetchall()
    
    conn.close()
    
    # Format the output
    output = f"""Title: {title}
Date: {pub_date}
ID: {ep_showid}
Show type: {show_title}
Body: {body}
Things of the day:"""

    if things:
        for author, thing_title, url in things:
            output += f"\n{author}: [{thing_title}]({url})"
    
    return output