import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QIcon

# Spotify authentication
client_id = '3cba3e9f179a4dd699883e7ac2888d6d'
client_secret = 'b6f564dffb6c4825b4b6fb128f966f2b'

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Global variable to persist the metadata window
metadata_screen = None

metadata_search_bar = None
metadata_results_list = None
timer = QTimer()
timer.setSingleShot(True)

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

        global metadata_search_bar
        metadata_search_bar = QLineEdit()

        timer.timeout.connect(fetch_results)
        metadata_search_bar.textChanged.connect(on_metadata_search_text_changed)

        metadata_search_label = QLabel("Song Title: ")

        metadata_search_layout = QHBoxLayout()
        metadata_search_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        metadata_search_layout.addWidget(metadata_search_label)
        metadata_search_layout.addSpacing(10)
        metadata_search_layout.addWidget(metadata_search_bar)

        global metadata_results_list
        metadata_results_list = QListWidget()

        # Connect the item click event to fetch the selected track link
        metadata_results_list.itemClicked.connect(lambda item: on_metadata_item_clicked(item, callback))

        metadata_results_list.setUniformItemSizes(True)
        metadata_results_list.setIconSize(QSize(100, 100))

        metadata_screen_layout = QVBoxLayout()
        metadata_screen_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        metadata_screen_layout.addLayout(metadata_search_layout)
        metadata_screen_layout.addSpacing(30)
        metadata_screen_layout.addWidget(metadata_results_list)
        metadata_screen_layout.setContentsMargins(30, 30, 30, 30)

        central_widget.setLayout(metadata_screen_layout)
    
    # Show the window
    metadata_screen.show()

def on_metadata_search_text_changed(event):
    timer.start(1500)

def on_metadata_item_clicked(item, callback):
    # Extract the song query (track name and artist)
    selected_text = item.text()
    
    # Search for the selected track to get its link
    query = selected_text.split(" - ")[0]  # Get the song title
    results = sp.search(q=query, type='track', limit=1)
    track_link = results['tracks']['items'][0]['external_urls']['spotify']  # Get Spotify link
    
    # Pass the track link back to the callback function in main_screen.py
    callback(track_link)
    
    # Close the metadata screen
    metadata_screen.close()

def fetch_results():
    song_query = metadata_search_bar.text()

    if not song_query:
        metadata_results_list.clear()
        return

    results = sp.search(q=song_query, type='track', limit=10)  # Limit results to 10 tracks
    tracks = results['tracks']['items']
    metadata_results_list.clear()  # Clear previous results

    for track in tracks:
        song_title = track['name']
        artist_name = ', '.join(artist['name'] for artist in track['artists'])
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