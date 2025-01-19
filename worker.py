from PyQt6.QtCore import QThread, pyqtSignal

class DownloadWorker(QThread):
    # Signal to notify when a song download is complete
    finished = pyqtSignal(str)

    def __init__(self, get_music, flac_source_link, metadata_source_link):
        super().__init__()
        self.get_music = get_music
        self.flac_source_link = flac_source_link
        self.metadata_source_link = metadata_source_link

    def run(self):
        try:
            # Call the get_music function to download the song
            self.get_music(self.flac_source_link, self.metadata_source_link)
            self.finished.emit("Download Complete")
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

class MetadataSearchWorker(QThread):
    # Signal to notify when metadata search is complete
    finished = pyqtSignal(list)  # We will emit the list of search results

    def __init__(self, start_metadata_search, song_query):
        super().__init__()
        self.start_metadata_search = start_metadata_search  # Accept the search function
        self.song_query = song_query

    def run(self):
        try:
            # Execute the function passed during instantiation
            results = self.start_metadata_search(self.song_query)

            if results:
                tracks = results['tracks']['items']  # Assuming you want to pass the tracks data
                self.finished.emit(tracks)  # Emit the results when the search is complete
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")  # Emit an error message if something goes wrong

class MusicSearchWorker(QThread):
    # Signal to notify when the music search is complete
    finished = pyqtSignal(list)

    def __init__(self, start_music_search, song_query):
        super().__init__()
        self.start_music_search = start_music_search
        self.song_query = song_query

    def run(self):
        try:
            # Call the fetch_results_function to search for music
            results = self.start_music_search(self.song_query)
            self.finished.emit(results)
        except Exception as e:
            self.finished.emit(str(e))  # Emit error if something goes wrong