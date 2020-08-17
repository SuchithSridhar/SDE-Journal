
import os


class FolderManager:
    def __init__(self, folder):
        self.folder = folder

    def __enter__(self):
        self.main = os.getcwd()
        os.chdir(self.folder)

    def __exit__(self, exc_type, exc_val, traceback):
        os.chdir(self.main)
