import os
import tkinter as tk
from tkinter import ttk
from . import constants as const
from . import foldermanager as fm
from . import ScrollableFrame


class Pictures:
    def __init__(self, frame):
        self.frame = frame
        self.folder = "Assets"
        self.mainlabel = tk.Label(self.frame, text="Pictures on this day:")
        self.mainlabel.configure(bg=const.UPPER_BG,
                                 font=const.PICS_OPTIONS_FONT,
                                 fg="white")

        self.but_frame_holder = ScrollableFrame.ScrollableFrame(
            self.frame, style="new.TFrame"
        )
        self.buttons_frame = self.but_frame_holder.scrollable_frame
        self.buttons_frame.configure(style="new.TFrame")
        self.but_frame_holder.canvas.configure(bg=const.BASE_COLOR)

        def load():
            print(self.var.get())

        def delete():
            pass

        def picture():
            pass

        def draw():
            pass

        self.load_but = ttk.Button(
            self.frame, text="Load", command=load)
        self.delete_but = ttk.Button(
            self.frame, text="Delete", command=delete)
        self.picture_but = ttk.Button(
            self.frame, text="Add", command=picture)
        self.draw_but = ttk.Button(
            self.frame, text="Draw", command=draw)

        self.buttons = []
        self.labels = []

        self.w = 0
        self.h = 0

        self.mainlabel.place()

    def resize(self, w, h):
        self.w = w
        self.h = h
        self.mainlabel.place(x=2, y=2, w=w-4, h=0.1*h)

        x_buff = 10
        y_buff = 5

        internal_padx = 50
        internal_pady = 5

        start_x = x_buff
        start_y = (0.1*h)+10

        self.but_frame_holder.place(
            x=start_x, y=start_y, w=w-(x_buff*2), h=h*0.69
        )

        for button in self.buttons:
            # button.place(x=start_x, y=start_y,
            #              h=button_height, w=w-(x_buff*2)-15)
            button.pack(fill=tk.X, pady=y_buff, padx=x_buff/2,
                        ipadx=internal_padx, ipady=internal_pady,
                        expand=True, anchor=tk.CENTER)

        button_height = h*0.2/2.5
        button_width = w/2.5

        x_math = w/2 - button_width - x_buff
        y_math = start_y + h*0.69 + y_buff
        self.load_but.place(x=x_math, y=y_math,
                            w=button_width, h=button_height)

        x_math = w/2 - button_width - x_buff
        y_math = y_math = start_y + h*0.69 + y_buff + y_buff+button_height
        self.delete_but.place(x=x_math, y=y_math,
                              w=button_width, h=button_height)

        x_math = w/2 + x_buff
        y_math = y_math = start_y + h*0.69 + y_buff
        self.picture_but.place(x=x_math, y=y_math,
                               w=button_width, h=button_height)

        x_math = w/2 + x_buff
        y_math = y_math = start_y + h*0.69 + y_buff + y_buff + button_height
        self.draw_but.place(x=x_math, y=y_math,
                            w=button_width, h=button_height)

    def update(self):
        for button in self.buttons:
            button.destroy()

        self.buttons = []
        self.but_frame_holder.update()
        self.buttons_frame = self.but_frame_holder.scrollable_frame
        self.buttons_frame.configure(style="new.TFrame")
        self.but_frame_holder.canvas.configure(bg=const.BASE_COLOR)

        self.set_radio_buttons()
        self.resize(self.w, self.h)

    def set_radio_buttons(self):
        files = self.getfiles_today()
        self.var = tk.StringVar(self.frame)
        self.var.set("None")

        for name, file in files.items():
            button = tk.Radiobutton(self.buttons_frame, text=name,
                                    variable=self.var,
                                    value=file, indicator=0,
                                    bg=const.UPPER_BG)

            self.buttons.append(button)

    def configure(self, cal_var):
        self.cal_var = cal_var
        self.set_radio_buttons()

    def get_date(self):
        var = self.cal_var.get()
        var = var.split("/")

        if len(var[2]) == 2:
            var[2] = "20" + var[2]
        if len(var[1]) == 1:
            var[1] = "0" + var[1]
        if len(var[0]) == 1:
            var[0] = "0" + var[0]

        var = f"{var[2]}-{var[0]}-{var[1]}"
        return var

    def getfiles_today(self):
        files = self.getfiles()
        files_today = {}
        date = self.get_date()

        for file in files:
            if date in file:
                i = file.index("--")+2
                name = file[i:-7]
                files_today[name] = file

        return files_today

    def getfiles(self):
        # Files Names = 2019-02-15--my-picture's-name.SDEJPG
        # Files Names = 2019-02-15--my-picture's-name.SDEPNG
        try:
            with fm.FolderManager(self.folder):
                files = os.listdir()
        except FileNotFoundError:
            os.mkdir("Assets")
            files = []

        files.sort()
        for i in range(len(files)-1, -1, -1):
            if ".SDEJPG" not in files[i] and ".SDEPNG" not in files[i]:
                files.pop(i)

        return files
