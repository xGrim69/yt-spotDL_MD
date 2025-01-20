import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QListWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFontMetrics
from metadata_search import launch_metadata_search
from music_search import launch_music_search
import download_song
import metadata_search

app = QApplication([]) # Initializing the application

# Initialization of global variables
music_search_bar = None
metadata_search_bar = None
queue_section_area = None
recent_downloads_area = None

def on_metadata_search_clicked(event):
    # Automatically inserts the link of the selected item in the metadata search scren
    def update_metadata_search_bar(track_link):
        metadata_search_bar.setText(track_link)  # Set the text in the metadata search bar
    
    # Calling the function itself
    launch_metadata_search(app, update_metadata_search_bar)
    event.accept()

def on_music_search_clicked(event):
    # Automatically inserts the link of the selected item in the metadata search scren
    def update_music_search_bar(track_link):
        music_search_bar.setText(track_link)  # Set the text in the music search bar
    
    # Calling the function itself
    launch_music_search(app, update_music_search_bar)
    event.accept()

def on_download_button_clicked():
    # global is_downloading
    
    if download_song.is_downloading:
        print("Already downloading, please wait.")
        return

    download_song.is_downloading = True

    download_song.queue_container = queue_section_area
    download_song.recent_container = recent_downloads_area

    # Start processing the songs in the queue
    download_song.process_next_song()

def on_add_button_clicked():
    if music_search_bar.text().strip() != "" and metadata_search_bar.text().strip() != "":
        download_song.song_queue[len(download_song.song_queue) + 1] = {'music_source': music_search_bar.text(), 'metadata_source': metadata_search_bar.text()}
        music_search_bar.clear()
        metadata_search_bar.clear()

        metadata_search.temp_queued_song.setSizeHint(QSize(70, 70))
        metadata_search.queued_songs[len(metadata_search.queued_songs) + 1] = metadata_search.temp_queued_song

        queue_section_area.addItem(metadata_search.queued_songs[len(metadata_search.queued_songs)])

def create_main_screen():
    screen_geometry = app.primaryScreen().geometry()
    main_screen_x = int(screen_geometry.width() * 0.2)
    main_screen_y = int(screen_geometry.height() * 0.2)
    main_screen_width = int(screen_geometry.width() * 0.6)
    main_screen_height = int(screen_geometry.height() * 0.6)

    # Create the main window
    main_screen = QMainWindow()
    main_screen.setWindowTitle("yt-dlp X spotDL Music Downloader")
    main_screen.setGeometry(main_screen_x, main_screen_y, main_screen_width, main_screen_height)

    return main_screen

def insert_input_section():
    input_group_box = QGroupBox("Input Section") # Initializing the group box of input section

    music_search_layout = QHBoxLayout() # Container for inputs
    music_search_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    music_search_label = QLabel("FLAC Source [YT Music]")

    global music_search_bar # Making the music search bar global for content modifications
    music_search_bar = QLineEdit()
    music_search_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)

    # Connect the click event of the music search bar to launch the music screen
    music_search_bar.mousePressEvent = on_music_search_clicked

    metadata_search_layout = QHBoxLayout()
    metadata_search_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    metadata_search_label = QLabel("Metadata Source [Spotify]")

    global metadata_search_bar # Making the metadata search bar for content modifications
    metadata_search_bar = QLineEdit()
    metadata_search_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)

    # Connect the click event of the metadata search bar to launch the metadata screen
    metadata_search_bar.mousePressEvent = on_metadata_search_clicked

    button_layout = QHBoxLayout()
    button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    download_button = QPushButton("Download")
    download_button.clicked.connect(on_download_button_clicked) # Connecting the operation function to the download button
    download_button.setFixedSize(100, 30)

    add_button = QPushButton("Add")
    add_button.clicked.connect(on_add_button_clicked) # Connecting the operation function to the download button
    add_button.setFixedSize(100, 30)
    
    button_layout.addWidget(add_button)
    button_layout.addSpacing(5)
    button_layout.addWidget(download_button)

    music_search_label_font_metrics = QFontMetrics(music_search_label.font()) # Fetching the information about the music search label
    music_search_label_width = music_search_label_font_metrics.horizontalAdvance(music_search_label.text()) # Extracting the width out of it

    metadata_search_label_font_metrics = QFontMetrics(metadata_search_label.font()) # Fetching the information about the metadata search label
    metadata_search_label_width = metadata_search_label_font_metrics.horizontalAdvance(metadata_search_label.text()) # Extracting the width out of it

    music_search_layout.addWidget(music_search_label)
    music_search_layout.addSpacing((metadata_search_label_width - music_search_label_width) + 10)
    music_search_layout.addWidget(music_search_bar)

    metadata_search_layout.addWidget(metadata_search_label)
    metadata_search_layout.addSpacing(10)
    metadata_search_layout.addWidget(metadata_search_bar)

    upper_input_section_layout = QVBoxLayout()
    upper_input_section_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    upper_input_section_layout.addLayout(metadata_search_layout)
    upper_input_section_layout.addSpacing(30)
    upper_input_section_layout.addLayout(music_search_layout)

    lower_input_section_layout = QVBoxLayout()
    lower_input_section_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
    
    lower_input_section_layout.addLayout(button_layout)

    final_input_section_layout = QVBoxLayout()
    
    final_input_section_layout.addLayout(upper_input_section_layout)
    final_input_section_layout.addSpacing(20)
    final_input_section_layout.addLayout(lower_input_section_layout)

    input_group_box.setLayout(final_input_section_layout) # Setting the final input section layout as the default layout for input group box

    final_layout = QVBoxLayout()
    final_layout.addWidget(input_group_box) # Inserting the final input section layout to the input group box
    
    return final_layout

def insert_recent_downloads():
    recents_group_box = QGroupBox("Recent Downloads") # Initializing the group box for recent downloads

    global recent_downloads_area
    recent_downloads_area = QListWidget() # Initializing the container for recent downloads
    recent_downloads_area.setSpacing(5)
    recent_downloads_area.setUniformItemSizes(True)
    recent_downloads_area.setIconSize(QSize(60, 60))

    recent_downloads_layout = QVBoxLayout()
    recent_downloads_layout.addWidget(recent_downloads_area)

    recents_group_box.setLayout(recent_downloads_layout) # Setting the recent downloads layout as the default layout for recent downloads group box

    final_layout = QVBoxLayout()
    final_layout.addWidget(recents_group_box)

    return final_layout

def insert_queue_section():
    queue_group_box = QGroupBox("Queue Section") # Initializing the group box for queue section

    global queue_section_area
    queue_section_area = QListWidget() # Initializing the container for queue section
    queue_section_area.setSpacing(5)
    queue_section_area.setUniformItemSizes(True)
    queue_section_area.setIconSize(QSize(60, 60))

    queue_section_layout = QVBoxLayout()
    queue_section_layout.addWidget(queue_section_area)

    queue_group_box.setLayout(queue_section_layout) # Setting the queue section layout as the default layout for queue group box

    final_layout = QVBoxLayout()
    final_layout.addWidget(queue_group_box)

    return final_layout

if __name__ == "__main__":
    main_screen = create_main_screen()

    central_widget = QWidget()
    main_screen.setCentralWidget(central_widget) # Initializing the central widget of the main screen

    input_section = insert_input_section()

    recents_downloads = insert_recent_downloads()

    queue_section = insert_queue_section()

    upper_layout = QHBoxLayout()
    upper_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    upper_layout.addLayout(input_section)
    upper_layout.addSpacing(20)
    upper_layout.addLayout(recents_downloads)

    parent_layout = QVBoxLayout()
    parent_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

    parent_layout.addLayout(upper_layout)
    parent_layout.addSpacing(15)
    parent_layout.addLayout(queue_section)

    parent_layout.setContentsMargins(30, 30, 30, 30)

    central_widget.setLayout(parent_layout) # Setting the parent layout as the layout of the central widget

    main_screen.show() # Show the main screen

    sys.exit(app.exec()) # Executes the application