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