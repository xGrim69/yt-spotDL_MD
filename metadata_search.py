import time
import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QIcon
from requests.exceptions import ReadTimeout
from worker import MetadataSearchWorker

# Spotify authentication
client_id = '3cba3e9f179a4dd699883e7ac2888d6d'
client_secret = 'b6f564dffb6c4825b4b6fb128f966f2b'

# Initializing the connection to spotify database
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Initialization of global variables
metadata_screen = None
metadata_search_bar = None
metadata_results_list = None
search_timer = None
queued_songs = {}
temp_queued_song = None

def on_metadata_search_text_changed(event):
    global search_timer

    song_query = metadata_search_bar.text().strip()  # Get the search query from the search bar

    # Stop the previous timer if it's running
    if search_timer is not None:
        search_timer.stop()

    # Clears the content of metadata results list
    if not song_query:
        metadata_results_list.clear()
        return
    
    if song_query:  # Only trigger search if the input is not empty
        # Create the timer to wait for 1.5 seconds before executing the search function
        search_timer = QTimer()
        search_timer.setSingleShot(True)  # Ensures it triggers only once after the delay
        search_timer.timeout.connect(lambda: start_metadata_search(song_query))
        search_timer.start(1500)  # Wait for 1.5 seconds before calling the search function

def start_metadata_search(song_query):
    # Create the MetadataSearchWorker with the search function and song query
    search_worker = MetadataSearchWorker(fetch_results_with_retry, song_query)
    
    # Connect the finished signal to handle the results and pass the album_id = track['album']['id']  # Get the album IDworker instance
    search_worker.finished.connect(lambda results: handle_metadata_search_finished(results, search_worker))
    
    # Start the worker thread
    search_worker.start()

def handle_metadata_search_finished(results, worker):
    if isinstance(results, str):  # If there's an error message
        print(f"Metadata search failed: {results}")
    else:
        # Handle the search results (e.g., display them in the UI)
        metadata_results_list.clear()
        fetch_results()
    
    # Optionally, clean up the worker
    if worker:
        worker.quit()  # Stop the worker if it's finished
        worker.wait()  # Wait for the worker to finish cleanly

# Function to launch metadata search window
def launch_metadata_search(qApplication, callback):
    global metadata_screen  # Persist the window instance

    # Check if window already exists, and reuse it
    if metadata_screen is None:
        screen_geometry = qApplication.primaryScreen().geometry()
        metadata_screen_x = int(screen_geometry.width() * 0.25)
        metadata_screen_y = int(screen_geometry.height() * 0.25)
        metadata_screen_width = int(screen_geometry.width() * 0.5)
        metadata_screen_height = int(screen_geometry.height() * 0.5)

        # Create and configure the metadata screen
        metadata_screen = QMainWindow()
        metadata_screen.setWindowTitle("Metadata Search")
        metadata_screen.setGeometry(metadata_screen_x, metadata_screen_y, metadata_screen_width, metadata_screen_height)

        central_widget = QWidget()

        metadata_screen.setCentralWidget(central_widget)

        global metadata_search_bar # Making the metadata search bar global for content modifications in the metadata results list
        metadata_search_bar = QLineEdit()

        metadata_search_bar.textChanged.connect(on_metadata_search_text_changed)

        metadata_search_label = QLabel("Song Title: ")

        metadata_search_layout = QHBoxLayout()
        metadata_search_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        metadata_search_layout.addWidget(metadata_search_label)
        metadata_search_layout.addSpacing(10)
        metadata_search_layout.addWidget(metadata_search_bar)

        global metadata_results_list # Making the metadata results list global for accessing information to the metadata search bar
        metadata_results_list = QListWidget()

        # Connect the item click event to fetch the selected track link
        metadata_results_list.itemClicked.connect(lambda item: on_metadata_item_clicked(item, callback))

        metadata_results_list.setUniformItemSizes(True)
        metadata_results_list.setIconSize(QSize(60, 60))

        metadata_screen_layout = QVBoxLayout()
        metadata_screen_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        metadata_screen_layout.addLayout(metadata_search_layout)
        metadata_screen_layout.addSpacing(30)
        metadata_screen_layout.addWidget(metadata_results_list)
        metadata_screen_layout.setContentsMargins(30, 30, 30, 30)

        central_widget.setLayout(metadata_screen_layout)
    
    # Show the window
    metadata_screen.show()

# def on_metadata_search_text_changed(event):
#     timer.start(1500)

def on_metadata_item_clicked(item, callback):
    track_link = item.data(Qt.ItemDataRole.UserRole) # Get Spotify link
    
    # Pass the track link back to the callback function in main_screen.py
    callback(track_link)

    global temp_queued_song
    temp_queued_song = item.clone() # Saving info of a queued song, including album art and track link

    metadata_search_bar.clear()
    metadata_search_bar.setFocus()
    metadata_results_list.clear()
    
    # Close the metadata screen
    metadata_screen.close()

# Function to handle Spotify search with retry logic
def fetch_results_with_retry(song_query, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            # Try to fetch results from Spotify API
            metadata_results = sp.search(q=song_query, type='track', limit=10)  # Limit results to 10 tracks
            return metadata_results
        except ReadTimeout as e:
            # If a timeout occurs, retry the request
            retries += 1
            print(f"Timeout error, retrying... {retries}/{max_retries}")
            time.sleep(2)  # Wait for 2 seconds before retrying
        except Exception as e:
            # Log other exceptions and stop retrying
            print(f"Error occurred: {e}")
            break
    print("Max retries reached, returning empty results.")
    return None  # Return None if max retries are reached without success

def fetch_results():
    song_query = metadata_search_bar.text()

    # Clears the content of metadata results list
    if not song_query:
        metadata_results_list.clear()
        return

    # Call the retry-enabled search function
    metadata_results = fetch_results_with_retry(song_query)

    if metadata_results:
        tracks = metadata_results['tracks']['items']  # Fetching the results based on the song query
        metadata_results_list.clear()  # Clear previous results

    # Adding the fetched items to the metadata results list
    for track in tracks:
        song_title = track['name']
        artist_name = ', '.join(artist['name'] for artist in track['artists'])
        track_url = track['external_urls']['spotify']
        album_id = track['album']['id']  # Get the album ID
        
        # Fetch album details using the album ID
        album_details = sp.album(album_id)
        album_image_url = album_details['images'][0]['url'] if album_details['images'] else None
        
        # Create a QListWidgetItem with the song title and artist name
        item_text = f"{song_title} - {artist_name}"
        item = QListWidgetItem(item_text)

        if album_image_url:
            image = fetch_album_image(album_image_url)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                item.setIcon(QIcon(pixmap))
        
        item.setData(Qt.ItemDataRole.UserRole, track_url) # Store the url as additional data to the item for fast url retrieval
        item.setSizeHint(QSize(110, 110))  # Set a larger size hint for each item (width x height)
        metadata_results_list.addItem(item)

def fetch_album_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        
        image = QImage()
        if not image.loadFromData(response.content):  # Load image from response content
            print(f"Failed to load image from {url}: Invalid image data")
            return QImage()  # Return an invalid QImage
        
        return image  # Return the QImage

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Log HTTP errors
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")  # Log other errors
    
    return QImage()  # Return an invalid QImage if there's an error