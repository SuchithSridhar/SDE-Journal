import tkinter as tk
from tkinter import ttk

'''
A tkinter frame that comes with a scrollbar to
navigate the frame in the y direction

pack objects into the ScrollableFrame.scrollable_frame
and not into the object itself

pack,grid,place the frame object anywhere you like

to change things like bg color
change ScrollableFrame.canvas properties

example code:

root = tk.Tk()
frame = ScrollableFrame(root)
for i in range(50):
    ttk.Label(
        frame.scrollable_frame,
        text="Sample scrolling label"
    ).pack() # this has to be packed

frame.place(x=0, y=0, w=500, h=500)
root.geometry("500x500")
root.mainloop()


'''


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        self.canvas = canvas

        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=canvas.yview)
        self.scrollbar = scrollbar

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="center")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def update(self):
        self.scrollbar.destroy()
        self.canvas.destroy()
        self.scrollable_frame.destroy()

        canvas = tk.Canvas(self)
        self.canvas = canvas

        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=canvas.yview)
        self.scrollbar = scrollbar

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="center")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
