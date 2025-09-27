import pandas as pd
import unittest
import musicdl
from musicdl.cli import MusicDownloader


class TestCli(unittest.TestCase):
    def test_download(self):
        """
        sanity check to make sure download pipeline works

        tests are defined as methods 
        starting with `test`
        """

        mdl = MusicDownloader()
        mdl.db.reset_database()
        track = mdl.download("https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU?si=0684264878094a00", verbose=False)
        self.assertEqual(track.name, "No Idea")
        self.assertEqual(track.artist_name, "Don Toliver")

    def test_export(self):
        # depends on test_download()
        mdl = MusicDownloader()
        file_path = mdl.to_csv()
        df = pd.read_csv(file_path)["audio_path"].iloc[0]
        # maybe the top video search result will change in the future
        # but this works for checking formatting for now
        self.assertEqual(df, "./mp3s/DonToliver_NoIdea__r-nPqWGG6c.mp3")
    

# python -m unittest --verbose tests

if __name__ == "__main__":
    unittest.main()
