import unittest
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
import gui as myGui
import rip as rip
import utils as utils
from downloadItem import DownloadItem

class TestRipper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
        
        cls.test_dir = Path.home() / "RipperTestDownloads"
        try:
            cls.test_dir.mkdir(exist_ok=True)
            test_file = cls.test_dir / "test_write.tmp"
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError) as e:
            raise unittest.SkipTest(f"Could not create or write to test directory: {e}")
        
        cls.ripper = rip.Ripper(None)
        cls.ripper.setPath(cls.test_dir)
        
        cls.window = myGui.MainWindow(cls.ripper)
        cls.ripper.window = cls.window

    def setUp(self):
        try:
            for file in self.test_dir.glob("*"):
                if file.is_file():
                    file.unlink()
        except (PermissionError, OSError) as e:
            self.fail(f"Failed to clean test directory: {e}")

    def test_ripper_initialization(self):
        """Test if Ripper initializes correctly"""
        self.assertIsNotNone(self.ripper)
        self.assertIsNotNone(self.ripper.ripQueue)
        self.assertIsNotNone(self.ripper.updateQueue)

    def test_add_to_queue(self):
        """Test adding items to the download queue"""
        test_url = "https://www.youtube.com/watch?v=yykFKAZuU_g"
        item = DownloadItem()
        item.setUrl(test_url)
        item.setDownloadDir(self.ripper.getPath())
        
        self.ripper.addToQueue(item)
        self.assertEqual(len(list(self.ripper.ripQueue.queue)), 1)

    def test_path_management(self):
        """Test path setting and getting functionality"""
        new_path = self.test_dir / "subdir"
        try:
            new_path.mkdir(exist_ok=True)
            self.ripper.setPath(new_path)
            self.assertEqual(self.ripper.getPath(), "subdir")
            self.assertEqual(self.ripper.getFullPath(), new_path)
        except (PermissionError, OSError) as e:
            self.skipTest(f"Could not create test subdirectory: {e}")

    def test_download_item_creation(self):
        """Test DownloadItem creation and properties"""
        item = DownloadItem()
        test_url = "https://www.youtube.com/watch?v=yykFKAZuU_g"
        item.setUrl(test_url)
        
        self.assertEqual(item.getUrl(), test_url)
        self.assertEqual(item.getUrlType(), 0)  # Single video type

    def test_playlist_detection(self):
        """Test playlist URL detection"""
        playlist_url = "https://www.youtube.com/playlist?list=PLQMmC9DAcgQCskmnA04APtCJLOgT9p0X3"
        item = DownloadItem()
        item.setUrl(playlist_url)
        
        self.assertEqual(item.getUrlType(), 1)  # Playlist type

    @classmethod
    def tearDownClass(cls):
        try:
            for file in cls.test_dir.glob("*"):
                if file.is_file():
                    file.unlink()
            cls.test_dir.rmdir()
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not clean up test directory: {e}")
        
        cls.app.quit()

if __name__ == '__main__':
    unittest.main()


