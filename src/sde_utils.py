from . import constants as const
from . import foldermanager as fm
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller
    To be able to get the images to work in One File mode"""

    try:
        # PyInstaller creates a temp folder
        # and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_icon_file():
    with fm.FolderManager(const.BASE_PATH):
        if os.name == "posix":
            x = resource_path("res/Diary_icon.png")
        else:
            x = resource_path("res/Diary_icon.ico")

    return x


def check_folder(folder):
    # Checks if the folder exists
    return os.path.isdir(folder)


def check_file(date):
    # Checks if the file exists
    try:
        open(date + ".SDE")
        return True
    except FileNotFoundError:
        return False


def cd_base_folder():
    if not check_folder(const.MAIN_FOLDER):
        os.makedirs(const.MAIN_FOLDER)

    os.chdir(const.MAIN_FOLDER)


def files_in_folder():
    things = os.listdir()
    files = []
    for file in things:
        if "-" in file and ".SDE" in file:
            file = file.replace(".SDE", "")
            files.append(file)

    files.sort()

    for i in range(len(files)):
        files[i] = files[i].split("-")
        # file.reverse() # This reverse Causes dd-mm-yyyy
    return files
