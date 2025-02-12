## Converts the subrip files into text files that are hopefully better to finetune LLM, make embeddings, etc

import argparse
import pysrt

def parse_args():
    parser = argparse.ArgumentParser(description="Convert SRT files to plain text using pysrt")
    parser.add_argument("--srt_file", type=str, help="Path to the SRT file")
    parser.add_argument("--output_file", type=str, help="Path to the output text file")
    parser.add_argument("--collapse", action="store_true", help="Collapse contiguous lines from the same speaker")
    return parser.parse_args()

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

    return '\n\n'.join(processed_lines)

def main():
    args = parse_args()
    subs = pysrt.open(args.srt_file)
    processed_content = process_srt(subs, args.collapse)

    with open(args.output_file, 'w', encoding='utf-8') as file:
        file.write(processed_content)

if __name__ == "__main__":
    main()
