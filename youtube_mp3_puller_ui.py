"""Graphical frontend for the SpotDL YouTube MP3 Puller."""

from youtube_mp3_puller._ui import SpotdlDownloaderUI

__all__ = ["SpotdlDownloaderUI"]

if __name__ == "__main__":
    app = SpotdlDownloaderUI()
    app.mainloop()
