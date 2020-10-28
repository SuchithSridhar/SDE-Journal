import webbrowser
import os
import subprocess
import sys
import time
import shutil


def zip_files(zip_file_name, folderPath):
    shutil.make_archive(zip_file_name, 'zip', folderPath)


def open_drive():
    url = r'https://drive.google.com/drive/my-drive'
    webbrowser.open_new(url)


def save_to_drive(pathToFolder):
    dirname = "ZipBackup"
    files = os.listdir(pathToFolder)
    zipping = []
    for file in files:
        if file[-4:] == ".SDE":
            zipping.append(file)

    try:
        os.makedirs(dirname)
    except Exception:
        pass

    try:
        zip_files(os.path.join(dirname, "SDE-Backup.zip"), zipping)
    except Exception as e:
        pass
        # print("Unable to zip files properly")
        # print(e)
    try:
        open_drive()
    except Exception as e:
        pass
        # print("Unable to open drive properly")
        # print(e)
    time.sleep(1)
    open_file(os.path.join(original_path, dirname))


def open_file(filename):
    try:
        os.startfile(filename)
    except Exception as e:
        # print("No folder in path 1 of opening")
        try:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])
        except Exception:
            pass
            # print("Not able to open folder using path 2!")
