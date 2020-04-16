import io
import tkinter as tk
from . import foldermanager as fm
from . import SDEImageCipher


class Canvas:
    def __init__(self, root, folder, code):
        self.code = code
        self.frame = tk.Frame(root)
        self.canvas = tk.Canvas(self.frame)
        self.folder = folder
        self.size = (0, 0)

    def place(self, x=0, y=0, w=0, h=0):
        self.size = (w, h)
        self.frame.place(x=x, y=y, w=w, h=h)
        self.canvas.place(x=x, y=10, w=w, h=h-10)

    def raiseframe(self):
        self.frame.tkraise()

    def load(self, file):
        with fm.FolderManager(self.folder):
            with open(file, 'rb') as f:
                data = f.read()

        data = SDEImageCipher.decrypt(data, self.code)
        image = io.BytesIO(data)
        image = Image.open(image)
        image = image.resize(self.size, Image.ANTIALIAS)
        image = ImageTK.PhotoImage(image)
        self.image = image
        self.canvas.create_image((0, 0), image=self.image, anchor="nw")

    def clear(self):
        self.canvas.delete("all")


# with fm.FolderManager(self.folder):
#                 with open("2020-04-09--Test copy.png", 'rb') as f:
#                     image = Image.open(f)
#                     image = image.resize(self.canvas.sde_size, Image.ANTIALIAS)
#                     image = ImageTk.PhotoImage(image)
#             self.canvas.image = image
#             self.canvas.create_image(
#                 (0, 0), image=self.canvas.image, anchor="nw")
