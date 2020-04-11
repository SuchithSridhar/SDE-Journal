from PIL import Image
from PIL import ImageTk
import tkinter as tk

root = tk.Tk()
root.geometry("600x600")
canvas = tk.Canvas(root)
canvas.place(x=0, y=0, w=600, h=600)
image = Image.open()
image = ImageTk.PhotoImage(image)
canvas.create_image((0, 0), image=image, anchor="nw")
root.mainloop()
