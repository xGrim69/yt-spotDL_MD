import os
import spotipy
import shutil
import json
import subprocess
import re
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from worker import DownloadWorker

client_id = '3cba3e9f179a4dd699883e7ac2888d6d'
client_secret = 'b6f564dffb6c4825b4b6fb128f966f2b'

credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=credentials)

song_queue = {}
queue_container = None
recent_container = None

# Add a flag to track if the queue is still being processed
is_downloading = False

def process_next_song():
    global is_downloading

    if song_queue:
        # Convert the dictionary to a list and pop the first item
        song_key, song = next(iter(song_queue.items()))  # Get the first item in the dictionary

        # Remove the first item from the queue
        del song_queue[song_key]
        
        flac_source = song['music_source']
        metadata_source = song['metadata_source']

        # Create the worker for downloading the song
        download_worker = DownloadWorker(get_music, flac_source, metadata_source)
        
        # Connect the finished signal to the next step (process next song)
        download_worker.finished.connect(lambda message: handle_download_finished(message, download_worker))
        
        # Start the worker thread
        download_worker.start()
    else:
        print("All downloads completed.")
        is_downloading = False

def handle_download_finished(message, worker):
    # Print the message when the download finishes (success or error)
    print(message)
    
    # Optionally, clean up the worker
    if worker:
        worker.quit()  # Stop the worker if it's finished
        worker.wait()  # Wait for the worker to finish cleanly

    # Process the next song in the queue
    process_next_song()

def download_audio(flac_source):
    # Load the metadata from the .spotdl file
    with open("./temp_resources/metadata.spotdl", "r") as file:
        metadata = json.load(file)

    # Assuming there is only one item in the metadata
    item = metadata[0]

    # Extract directory names first
    album_artist = item.get("album_artist", "").split(",") if item.get("album_artist") else ""
    album = item.get("album_name", "")
    title = item.get("name", "")

    # Sanitize variables to avoid filesystem issues
    sanitized_album_artist = ", ".join(album_artist).replace('/', '／')  # Join list and replace '/'
    sanitized_album = album.replace('/', '／')  # Replace '/' with a full-width slash for the folder name
    sanitized_title = title.replace('/', '／')  # Replace '/' with a full-width slash for the folder name

    # Download the music in flac format
    command = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "flac",  # Specify audio format as FLAC
        "-o", f"./Music/{sanitized_album_artist}/{sanitized_album}/{sanitized_title}.flac",  # Output template
        flac_source  # The URL to download from
    ]

    try:
        # Execute the command
        subprocess.run(command, check=True)
        
        # Return first artist, album, and title for directory naming
        return sanitized_album_artist, sanitized_album, sanitized_title
    except subprocess.CalledProcessError as e:
        print(f"{datetime.now().strftime("%H:%M:%S")}: An error occurred: {e}")

        return None, None, None  # Return None if there's an error

def extract_metadata(flac_source_link, metadata_source_link):
    # The spotdl command with arguments
    command = ["spotdl", "save", metadata_source_link, "--save-file", "./temp_resources/metadata.spotdl"]

    # Run the subprocess command
    try:
        if os.path.isdir("./temp_resources"):
            shutil.rmtree('./temp_resources')
        
        os.mkdir("./temp_resources")
        subprocess.run(command, check=True)
        
        # Load the metadata from the .spotdl file
        with open("./temp_resources/metadata.spotdl", "r") as file:
            metadata = json.load(file)

        # Assuming there is only one item in the metadata
        item = metadata[0]

        # Capitalize genre inline: Split by spaces, slashes, and hyphens, then capitalize each part
        # genre = '-'.join([word.capitalize() for word in item.get("genres", "")[0].split('-')])  # First genre or blank
        genre = item.get("genres")[0] if item.get("genres") else "" # Get the first genre if genre list is not empty, else, blank
        
        # Split by spaces and slashes, and capitalize
        parts = re.split(r'([ &/-])', genre)  # Split by space, slash, or hyphen but keep the delimiters
        capitalized_genre = ''.join([part.capitalize() if part not in [' ', '-', '/', '&'] else part for part in parts])

        # Extract fields with defaults for optional ones (blank if not available)
        extracted_data = {
            "TITLE": item.get("name", ""),
            "ARTIST": ", ".join(item.get("artists", "")),
            "ALBUM": item.get("album_name", ""),
            "ALBUMARTIST": item.get("album_artist", ""),
            "COMPOSER": item.get("composer", ""),  # Composer is optional
            "GENRE": capitalized_genre,  # First genre or blank
            "TRACKNUMBER": item.get("track_number", ""),
            "TRACKTOTAL": item.get("tracks_count", ""),
            "DISCNUMBER": item.get("disc_number", ""),
            "DISCTOTAL": item.get("disc_count", ""),  # Assume `disc_count` for total discs
            "DATE": item.get("date", ""),
            "YEAR": item.get("year", ""),
            "BPM": item.get("bpm", ""),  # BPM is optional
            "COMMENT": flac_source_link,
            "ENCODEDBY": item.get("publisher", "")
        }

        # Format the extracted data into the desired string format without extra blank lines
        formatted_data = "\n".join(f"{key}={value}" for key, value in extracted_data.items())

        # Save the formatted data to a text file
        output_file = "./temp_resources/tagfile.txt"
        with open(output_file, "w") as outfile:
            outfile.write(formatted_data + '\n')
        
        command = ["curl", "-s", "-o", "./temp_resources/cover.jpg", item.get("cover_url", "")]
        subprocess.run(command, check=True)

        print(f"Metadata source downloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

def embed_tag(flac_file):
    tagfile_path = './temp_resources/tagfile.txt' # File that will contain the extracted metadata
    cover_path = './temp_resources/cover.jpg' # File that will contain the album image of the song
    
    try:
        # Importing tags and album cover into FLAC file
        subprocess.run(['metaflac', '--remove-all-tags', flac_file], check=True)  # Optional: Remove existing tags
        subprocess.run(['metaflac', '--import-tags-from=' + tagfile_path, flac_file], check=True) # Embed the metadata to the flac file
        subprocess.run(['metaflac', '--import-picture-from=' + cover_path, flac_file], check=True) # Embed the album image to the flac file

        print(f"\n{datetime.now().strftime("%H:%M:%S")}: Metadata and album cover embedded successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"{datetime.now().strftime("%H:%M:%S")}: An error occurred: {e}")

def get_music(flac_source_link, metadata_source_link):
    extract_metadata(flac_source_link, metadata_source_link) # Extracts metadata and save it to a txt file 
    album_artist, album, title = download_audio(flac_source_link) # Get artist, album, and title value from the flac file

    # Specify FLAC file and file
    flac_file = f'./Music/{album_artist}/{album}/{title}.flac'  # Predefined location of the flac file

    embed_tag(flac_file) # Do the embedding process itself

    queue_item = queue_container.takeItem(0) # Get the recently downloaded item from the queue container referenced to queue_section_area of main screen
    recent_item = queue_item.clone() # Clone the item to be inserted in recent container referenced to recent_downloads_area
    recent_container.insertItem(0, recent_item) # Insert the cloned item to the first place

    del queue_item # Delete the item downloaded to the queue item

    # Cleaning the directory
    try:
        shutil.rmtree('./temp_resources')
    except OSError as e:
        print(f'Error: {e.error}')

# # Use this function if the music is not available in spotify and comment out line 185 to 189 before running the python file.
# get_music([youtube music url without query line (?si=)], [spotify url without query line (?si=)])