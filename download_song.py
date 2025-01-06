import os
import shutil
import subprocess
import ffmpeg
from datetime import datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

def get_directory_names(metadata_source):
    try:
        # Use ffprobe to get metadata
        probe = ffmpeg.probe(metadata_source)

        artist = probe['format']['tags'].get('artist', 'Unknown Artist')
        album = probe['format']['tags'].get('album', 'Unknown Album')
        title = probe['format']['tags'].get('title', 'Unknown Title')
        
        return artist, album, title
    except subprocess.CalledProcessError as e:
        print(f"{datetime.now().strftime("%H:%M:%S")}: An error occurred: {e}")

def download_audio(flac_source, metadata_source):
    # Extract metadata first
    artist, album, title = get_directory_names(metadata_source)

    # Define the yt-dlp command with the specified options
    command = [
        "yt-dlp",
        "-q",
        "-x",  # Extract audio
        "--audio-format", "flac",  # Specify audio format as FLAC
        "-o", f"./Music/{artist.split('/')[0].strip()}/{album}/{title}.%(ext)s",  # Output template
        flac_source  # The URL to download from
    ]

    try:
        # Execute the command
        subprocess.run(command, check=True)
        
        # Return first artist, album, and title for further use
        return artist, album, title
    except subprocess.CalledProcessError as e:
        print(f"{datetime.now().strftime("%H:%M:%S")}: An error occurred: {e}")
        return None, None, None  # Return None if there's an error

def get_metadata_source(url):
    command = [
        "spotdl",
        "--log-level",
        "CRITICAL",
        url,
        "--format",
        "mp3",
        "--output",
        f"./temp_resources"
    ]

    try:
        # Execute the command
        subprocess.run(command, check=True)
        print(f"{datetime.now().strftime("%H:%M:%S")}: Metadata source downloaded successfully.")

        for temp_file in os.listdir('./temp_resources'):
            if temp_file.endswith('.mp3'):
                return temp_file
        
        return None
    except subprocess.CalledProcessError as e:
        print(f"{datetime.now().strftime("%H:%M:%S")}: An error occurred: {e}")
        return None

def extract_metadata(mp3_file):
    # Extract metadata from an MP3 file.
    audio = MP3(mp3_file, ID3=ID3)
    
    tags = {
        'TITLE': str(audio.get('TIT2', '')),
        'ARTIST': str(audio.get('TPE1', '')).replace('/', ', '),  # Replace '/' with ', '
        'ALBUM': str(audio.get('TALB', '')),
        'ALBUMARTIST': str(audio.get('TPE2', '')).replace('/', ', '),  # Replace '/' with ', '
        'COMPOSER': str(audio.get('TCOM', '')),
        'GENRE': str(audio.get('TCON', '')),
        'TRACKNUMBER': str(audio.get('TRCK', '')).split('/')[0] if 'TRCK' in audio else '',
        'TRACKTOTAL': str(audio.get('TRCK', '')).split('/')[1] if 'TRCK' in audio and '/' in str(audio['TRCK']) else '',
        'DISCNUMBER': str(audio.get('TPOS', '')).split('/')[0] if 'TPOS' in audio else '',
        'DISCTOTAL': str(audio.get('TPOS', '')).split('/')[1] if 'TPOS' in audio and '/' in str(audio['TPOS']) else '',
        'DATE': str(audio.get('TDRC', '')),
        'YEAR': str(audio.get('TDRC', '')).split('-')[0],
        'BPM': str(audio.get('TBPM', '')),
        'COMMENT': str(audio.get('COMM::XXX', '')),
        'ENCODEDBY': str(audio.get('TENC', ''))
    }

    return tags

def embed_tag(mp3_file, flac_file):
    tagfile_path = './temp_resources/tagfile.txt'
    cover_path = './temp_resources/cover.jpg'
    
    try:
        # Extract metadata from the MP3 file
        tags = extract_metadata(mp3_file)

        # Create a tagfile.txt to store extracted tags
        with open(tagfile_path, 'w') as tagfile:
            for tag_name, tag_value in tags.items():
                tagfile.write(f"{tag_name}={tag_value}\n")
        
        if not os.path.exists(cover_path):
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-hide_banner', '-i', mp3_file, '-an', '-frames:v', '1', '-c:v', 'copy', cover_path], check=True)

        # Importing tags and album cover into FLAC file
        subprocess.run(['metaflac', '--remove-all-tags', flac_file], check=True)  # Optional: Remove existing tags
        subprocess.run(['metaflac', '--import-tags-from=' + tagfile_path, flac_file], check=True)
        subprocess.run(['metaflac', '--import-picture-from=' + cover_path, flac_file], check=True)

        print(f"{datetime.now().strftime("%H:%M:%S")}: Metadata and album cover embedded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"{datetime.now().strftime("%H:%M:%S")}: An error occurred: {e}")

if __name__ == "__main__":
    # Get sources of the music and metadata
    flac_source_link = input("FLAC source link [YOUTUBE]: ")
    metadata_source_link = input("Metadata source link [SPOTIFY]: ")

    metadata_source = get_metadata_source(metadata_source_link)
    artist, album, title = download_audio(flac_source_link, f'./temp_resources/{metadata_source}')

    # Specify your FLAC file and JSON metadata file
    flac_file = f'./Music/{artist.split('/')[0].strip()}/{album}/{title}.flac'  # Change to your FLAC file path
    mp3_file = f'./temp_resources/{artist.replace('/', ', ')} - {title}.mp3'

    embed_tag(mp3_file, flac_file)

    # Cleaning the directory
    try:
        shutil.rmtree('./temp_resources')
    except OSError as e:
        print(f'Error: {e.error}')