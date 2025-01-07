import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics

app = QApplication([])

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
    input_group_box = QGroupBox("Input Section")

    music_search_layout = QHBoxLayout()
    music_search_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    music_search_label = QLabel("FLAC Source [YT Music]")

    music_search_bar = QLineEdit()

    metadata_search_layout = QHBoxLayout()
    metadata_search_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    metadata_search_label = QLabel("Metadata Source [Spotify]")

    metadata_search_bar = QLineEdit()

    button_layout = QHBoxLayout()
    button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    download_button = QPushButton("Download")
    download_button.setFixedSize(100, 30)
    
    button_layout.addWidget(download_button)

    music_search_label_font_metrics = QFontMetrics(music_search_label.font())
    music_search_label_width = music_search_label_font_metrics.horizontalAdvance(music_search_label.text())

    metadata_search_label_font_metrics = QFontMetrics(metadata_search_label.font())
    metadata_search_label_width = metadata_search_label_font_metrics.horizontalAdvance(metadata_search_label.text())

    music_search_layout.addWidget(music_search_label)
    music_search_layout.addSpacing((metadata_search_label_width - music_search_label_width) + 10)
    music_search_layout.addWidget(music_search_bar)

    metadata_search_layout.addWidget(metadata_search_label)
    metadata_search_layout.addSpacing(10)
    metadata_search_layout.addWidget(metadata_search_bar)

    upper_input_section_layout = QVBoxLayout()
    upper_input_section_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    upper_input_section_layout.addLayout(music_search_layout)
    upper_input_section_layout.addSpacing(30)
    upper_input_section_layout.addLayout(metadata_search_layout)

    lower_input_section_layout = QVBoxLayout()
    lower_input_section_layout.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
    
    lower_input_section_layout.addLayout(button_layout)

    final_input_section_layout = QVBoxLayout()
    
    final_input_section_layout.addLayout(upper_input_section_layout)
    final_input_section_layout.addSpacing(20)
    final_input_section_layout.addLayout(lower_input_section_layout)

    input_group_box.setLayout(final_input_section_layout)

    final_layout = QVBoxLayout()
    final_layout.addWidget(input_group_box)
    
    return final_layout

def insert_recent_downloads():
    recents_group_box = QGroupBox("Recent Downloads")

    recent_downloads_area = QScrollArea()
    recent_downloads_area.setWidgetResizable(False)

    initialize_recents = QWidget()
    recent_downloads_area.setWidget(initialize_recents)

    recent_downloads_layout = QVBoxLayout()
    recent_downloads_layout.addWidget(recent_downloads_area)

    recents_group_box.setLayout(recent_downloads_layout)

    final_layout = QVBoxLayout()
    final_layout.addWidget(recents_group_box)

    return final_layout

def insert_queue_section():
    queue_group_box = QGroupBox("Queue Section")

    queue_section_area = QScrollArea()
    queue_section_area.setWidgetResizable(False)

    initialize_queue = QWidget()
    queue_section_area.setWidget(initialize_queue)

    queue_section_layout = QVBoxLayout()
    queue_section_layout.addWidget(queue_section_area)

    queue_group_box.setLayout(queue_section_layout)

    final_layout = QVBoxLayout()
    final_layout.addWidget(queue_group_box)

    return final_layout

if __name__ == "__main__":
    main_screen = create_main_screen()

    central_widget = QWidget()
    main_screen.setCentralWidget(central_widget)

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

    central_widget.setLayout(parent_layout)

    main_screen.show()

    sys.exit(app.exec())