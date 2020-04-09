from ScrollableFrame import ScrollableFrame
import tkinter as tk
from tkinter import ttk


root = tk.Tk()
frame = ScrollableFrame(root)
for i in range(50):
    ttk.Label(frame.scrollable_frame,
              text="Sample scrolling label").pack()
frame.place(x=0, y=0, w=500, h=500)
root.geometry("500x500")
root.mainloop()
