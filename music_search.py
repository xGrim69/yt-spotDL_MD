from ytmusicapi import YTMusic
import requests
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QIcon

# Initialize YTMusic API
ytmusic = YTMusic()

# Initialization of global variables
music_screen = None
music_search_bar = None
music_results_list = None
timer = QTimer()
timer.setSingleShot(True)

# Function to launch music search window
def launch_music_search(qApplication, callback):
    global music_screen  # Persist the window instance

    # Check if window already exists, and reuse it
    if music_screen is None:
        screen_geometry = qApplication.primaryScreen().geometry()
        music_screen_x = int(screen_geometry.width() * 0.25)
        music_screen_y = int(screen_geometry.height() * 0.25)
        music_screen_width = int(screen_geometry.width() * 0.5)
        music_screen_height = int(screen_geometry.height() * 0.5)

        # Create and configure the music screen
        music_screen = QMainWindow()
        music_screen.setWindowTitle("Music Search")
        music_screen.setGeometry(music_screen_x, music_screen_y, music_screen_width, music_screen_height)

        central_widget = QWidget()

        music_screen.setCentralWidget(central_widget)

        global music_search_bar # Making the music search bar global for content modifications in the metadata results list
        music_search_bar = QLineEdit()

        timer.timeout.connect(fetch_results)
        music_search_bar.textChanged.connect(on_music_search_text_changed)

        music_search_label = QLabel("Song Title: ")

        music_search_layout = QHBoxLayout()
        music_search_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        music_search_layout.addWidget(music_search_label)
        music_search_layout.addSpacing(10)
        music_search_layout.addWidget(music_search_bar)

        global music_results_list # Making the music results list global for accessing information to the metadata search bar
        music_results_list = QListWidget()

        # Connect the item click event to fetch the selected track link
        music_results_list.itemClicked.connect(lambda item: on_music_item_clicked(item, callback))

        music_results_list.setUniformItemSizes(True)
        music_results_list.setIconSize(QSize(100, 100))

        music_screen_layout = QVBoxLayout()
        music_screen_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        music_screen_layout.addLayout(music_search_layout)
        music_screen_layout.addSpacing(30)
        music_screen_layout.addWidget(music_results_list)
        music_screen_layout.setContentsMargins(30, 30, 30, 30)

        central_widget.setLayout(music_screen_layout)
    
    # Show the window
    music_screen.show()

def on_music_search_text_changed(event):
    timer.start(1500)

def on_music_item_clicked(item, callback):
    song_url = item.data(Qt.ItemDataRole.UserRole) # Get Youtube Music link

    # Pass the track link back to the callback function in main_screen.py
    callback(song_url)
    
    # Close the music screen
    music_screen.close()

def fetch_results():
    song_query = music_search_bar.text()

    if not song_query:
        music_results_list.clear()
        return

    # Search for songs on YouTube Music using YTMusic API
    search_results = ytmusic.search(song_query, filter='songs')
    music_results_list.clear()  # Clear previous results

    # Adding the fetched items to the music results list
    for track in search_results[:10]:  # Slice the first 10 results
        song_title = track['title']
        artist_name = track['artists'][0]['name'] if 'artists' in track else 'Unknown Artist'
        video_id = track['videoId']
        
        # Create a YouTube Music link
        track_link = f'https://music.youtube.com/watch?v={video_id}'
        
        # Create a QListWidgetItem with the song title and artist name
        item_text = f"{song_title} - {artist_name}"
        item = QListWidgetItem(item_text)

        # Optionally, get album art (thumbnail)
        thumbnail_url = track['thumbnails'][0]['url'] if 'thumbnails' in track else None
        if thumbnail_url:
            image = fetch_album_image(thumbnail_url)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                item.setIcon(QIcon(pixmap))
        
        item.setData(Qt.ItemDataRole.UserRole, track_link) # Store the url as additional data to the item for fast url retrieval
        item.setSizeHint(QSize(110, 110))  # Set a larger size for each item
        music_results_list.addItem(item)

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