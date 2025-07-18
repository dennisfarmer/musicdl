import unittest

from musicdl.cli import MusicDownloader

class TestCli(unittest.TestCase):
    def test_track(self):
        """
        Simple example of a test case

        tests are defined as methods 
        starting with `test`
        """
        mdl = MusicDownloader()
        track = mdl.from_url("https://open.spotify.com/track/7AzlLxHn24DxjgQX73F9fU?si=0684264878094a00")
        self.assertEqual(track.name, "No Idea")
        self.assertEqual(track.artist_name, "Don Toliver")
    
    #def test_album(self):
        #pass

    #def test_playlist(self):
        #pass

    #def test_artist(self):
        #pass

    # ...

# python -m unittest --verbose tests
# python -m unittest --verbose tests.TestCli
# python -m unittest --verbose tests.TestCli.test_track

if __name__ == "__main__":
    unittest.main()
