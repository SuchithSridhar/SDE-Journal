import os
import time
import pickle
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tk_filedialog
from . import constants as const
from . import foldermanager as fm
from . import Encryption as enc
from . import SDE_Logger as logger
from . import ConvergeEntries, Change_pass_user, Open_drive, calendarClass
from . import TextPad, userClass, sde_utils, sdeExceptions, PicturesPage


class FakeEvent:
    def __init__(self, w, h):
        self.width = w
        self.height = h


class SDE_Window:
    ''' This class is not to create objects but
    only to be inherited. It defines functions common
    to Root windows and Toplevel windows'''

    def set_window(self):
        self.configure(bg=const.BASE_COLOR)
        self.center()

        try:
            self.iconbitmap(sde_utils.get_icon_file())
        except tk.TclError:
            self.tk.call(
                'wm',
                'iconphoto',
                self._w,
                tk.PhotoImage(file=sde_utils.get_icon_file())
            )

        self.title(const.APPLICATION_NAME)
        self.focus()

    def center(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def pop_up(self, button_text, label=""):
        popup_window = SDE_TopLevel(self)

        label = tk.Label(popup_window, text=label)
        label.config(bg=const.BASE_COLOR, font=const.FONT, fg='white')
        label.pack()
        button = ttk.Button(popup_window, text=button_text,
                            command=lambda: popup_window.destroy())
        button.pack()
        button.focus()

        return popup_window


class SDE_Root(SDE_Window, tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)


class SDE_TopLevel(SDE_Window, tk.Toplevel):

    def __init__(self, root, *args, **kwargs):
        tk.Toplevel.__init__(self, root, *args, **kwargs)


class MainApp(SDE_Root):

    def __init__(self, pages, *args, **kwargs):

        SDE_Root.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self)
        main_frame.pack(side="top", fill="both", expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        # 0 --> minimum size
        # weight =1 --> priority thing
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.bind('<Configure>', self.on_resize)

        self.current_frame = None
        self.frames = {}

        # pages is a list of pages
        for F in pages:
            frame = F(main_frame, self)
            # Here self is just the parent/ root
            self.frames[F] = frame
            frame.configure(bg=const.BASE_COLOR)
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(pages[0])
        logger.log("Created Pages, raised Intropage")

    def show_frame(self, page):

        self.frames[page].tkraise()

        if page == MainPage and self.frames[page].first_raise:
            logger.log("Raising MainFrame first time")
            self.resizable(True, True)
            self.frames[page].first_raise = False
            self.frames[page].on_first_raise()

        self.current_frame = page
        width = self.winfo_width()
        height = self.winfo_height()

        # this is being done since if we were on a different
        # page the the elements of the other pages wouldn't be
        # resized to decrease lag
        self.on_resize(FakeEvent(w=width, h=height))

    def on_resize(self, event):
        w = event.width
        h = event.height

        if w < 300 or h < 300:
            # for some reason the width and height kept
            # becoming very low numbers even though the
            # actual window size remained big
            return None

        try:
            self.frames[self.current_frame].resize_widgets(w, h)
        except KeyError:
            pass


class IntroPage(tk.Frame):

    page_name = "IntroPage"

    def __init__(self, main_frame, root):
        tk.Frame.__init__(self, main_frame)

        self.root = root
        self.main_frame = main_frame

        root.geometry("300x150")
        root.resizable(True, True)
        root.set_window()

        root.style = ttk.Style()
        # app.style.theme_use("clam") --> can set theme
        root.style.configure('TButton', background=const.UPPER_BG)
        root.style.configure('TButton', foreground='black')
        root.style.configure('new.TFrame', background=const.BASE_COLOR)

        # --- Check or make the main directory and cd to it ---
        sde_utils.cd_base_folder()
        # ----

        user = userClass.User()
        self.root.user = user

        label = tk.Label(self, text="User:")
        label.config(bg=const.BASE_COLOR, font=const.FONT, fg='white')
        label.place(x=15, y=25)
        user_box = tk.Entry(self, textvariable=user.name_var)
        user_box.place(x=50 + 15, y=25, width=200, height=25)
        user_box.focus()

        label = tk.Label(self, text="Code:")
        label.config(bg=const.BASE_COLOR, font=const.FONT, fg='white')
        label.place(x=14, y=75)
        code_box = tk.Entry(self, textvariable=user.code_var, show="*")
        code_box.place(x=50 + 15, y=75, width=200, height=25)

        log_in_b = ttk.Button(
            self, text="Log In",
            command=self.log_in
        )
        log_in_b.place(x=25, y=115, w=100)

        sign_up_b = ttk.Button(
            self, text="Sign up",
            command=self.sign_up
        )
        sign_up_b.place(x=300 - 25 - 100, y=115, w=100)

    def log_in(self):
        user = self.root.user
        user.update()
        exception_flag = True
        try:
            user.validate_values()
        except sdeExceptions.InvalidChars:
            self.root.pop_up("Close", "Invalid Characters")
        except sdeExceptions.LongUsername:
            self.root.pop_up("Close", "Username too long (24 max)")
        except sdeExceptions.SmallUsername:
            self.root.pop_up("Close", "Username too short (4 min)")
        except sdeExceptions.AlphaCodeError:
            self.root.pop_up("Close", "Password in numeric form only")
        else:
            exception_flag = False

        if exception_flag:
            # If there was an exception then dont proceed
            return None

        try:
            user.login_init()
            # If User exists and the password is right,
            # does not raise any exceptions
        except sdeExceptions.UserNotFound:
            self.root.pop_up("Close", "User Does not Exist")
        except sdeExceptions.WrongPassword:
            self.root.pop_up("Close", "Incorrect Password")
        except sdeExceptions.DatfileNotFound:
            self.root.pop_up("Close", "Unable to check password.")
        else:
            self.root.show_frame(MainPage)
            self.root.code = self.root.user.code
            logger.log("User Successful login")

    def sign_up(self):
        user = self.root.user
        user.update()
        exception_flag = True
        try:
            user.validate_values()
        except sdeExceptions.InvalidChars:
            self.root.pop_up("Close", "Invalid Characters")
        except sdeExceptions.LongUsername:
            self.root.pop_up("Close", "Username too long (24 max)")
        except sdeExceptions.SmallUsername:
            self.root.pop_up("Close", "Username too short (4 min)")
        except sdeExceptions.AlphaCodeError:
            self.root.pop_up("Close", "Password in numeric form only")
        else:
            exception_flag = False

        if exception_flag:
            # If there was an exception then dont proceed
            return None

        if user.check_user():
            self.root.pop_up("Close", "User already exists")
            return None

        else:
            user.signin_init()
            # Creates the folder and sets the password

            self.root.pop_up("Close", "User successfully created")
            time.sleep(2)
            self.root.show_frame(MainPage)
            logger.log("User signup successful")

    def resize_widgets(self, w, h):
        pass


class MainPage(tk.Frame):

    page_name = "MainPage"

    def __init__(self, main_frame, root):
        tk.Frame.__init__(self, main_frame)

        self.main_frame = main_frame
        self.root = root
        self.widgets = {}
        self.first_raise = True
        # Changed to false once raised the first time

    def switch_folder(self):
        user = self.root.user
        foldername = user.foldername
        try:
            os.chdir(foldername)
            logger.log("Switched to the User's folder")
        except FileNotFoundError:
            raise sdeExceptions.FolderMissing

    def on_first_raise(self):
        self.switch_folder()
        self.set_right_frame()
        self.set_left_frame()

        # Configure Pictures:
        self.widgets["PICTURES"].configure(cal_var=self.cal.var)

        self.root.geometry(f"{const.DEFAULT_WIDTH}x{const.DEFAULT_HEIGHT}")
        self.root.center()

    def set_right_frame(self):

        text_frame = tk.Frame(self, bg=const.BASE_COLOR)
        pics_frame = tk.Frame(self, bg=const.BASE_COLOR)
        pictures = PicturesPage.Pictures(pics_frame, self.root.user.code)

        s = tk.Scrollbar(text_frame, orient=tk.VERTICAL)

        text_frame.config(bg=const.BASE_COLOR)
        text = TextPad.Textpad(text_frame,
                               code=self.root.user.code,
                               wrap=tk.WORD,
                               yscrollcommand=s.set)

        text.config(font=const.TEXT_BOX_FONT)
        s.config(command=text.yview)

        pics_frame.place()
        text_frame.place()
        text.place()
        s.place()

        text.focus()
        self.root.text_box = text

        self.widgets["PICSFRAME"] = pics_frame
        self.widgets["TEXTFRAME"] = text_frame
        self.widgets["PICTURES"] = pictures
        self.widgets["TEXT"] = text
        self.widgets["SCROLL"] = s

    def set_left_frame(self):

        def change_day(*args, **kwargs):

            logger.log(f"Saving the file: {self.file_date}")

            set_notepad()
            self.day_var.set(self.cal.get_selected_formatted())
            self.widgets["PICTURES"].update()

            logger.log(f"Changed to file: {self.file_date}")

        def notes_func():
            file = "notes"
            if self.file_date == file:
                # When notes is already open
                return None

            text_box = self.root.text_box
            text_box.save_data(self.file_date)
            self.file_date = file

            if not text_box.load_file(file):
                # The file did not exist
                with open(file + ".SDE", 'w') as f:
                    f.write(enc.encrypt(
                        "--- ADD NOTES HERE ---\n\n",
                        int(self.root.user.code)
                    ))

                text_box.load_file(file)

            logger.log("Loaded the notes file")

        def options_page():
            set_notepad()
            logger.log(f"Saved to file: {self.file_date}")
            self.root.show_frame(OptionsPage)

        def next_page():
            files = sde_utils.files_in_folder()
            for i in range(len(files)):
                files[i] = "/".join(files[i])

            cur = ("/".join(self.file_date.split("-")))

            for file in range(len(files)):
                if files[file] > cur:
                    set_date = files[file].split("/")

                    set_date = set_date[1] + "/" + \
                        set_date[2] + "/" + set_date[0]

                    self.cal.var.set(set_date)
                    self.cal.var.set(set_date)
                    logger.log("Next file button triggered")
                    return None
            else:
                return None

        def prev_page():

            files = sde_utils.files_in_folder()
            for i in range(len(files)):
                files[i] = "/".join(files[i])

            cur = ("/".join(self.file_date.split("-")))

            for file in range(len(files) - 1, -1, -1):
                if files[file] < cur:
                    set_date = files[file].split("/")

                    set_date = set_date[1] + "/" + \
                        set_date[2] + "/" + set_date[0]

                    self.cal.var.set(set_date)
                    self.cal.var.set(set_date)
                    logger.log("Previous file button triggered")
                    return None
            else:
                return None

        def cal_set():
            # Calender widget
            # today = (today_date_num('m') + "/" +
            #          today_date_num('d') + "/" +
            #          today_date_num('y'))

            cal = calendarClass.Calendar(self)
            cal.place(x=10, y=150, w=380, h=300)

            self.cal = cal
            self.widgets["CAL"] = cal
            logger.log("Calendar set up")

        def set_notepad():
            text_box = self.root.text_box
            text_box.save_data(self.file_date)

            self.file_date = self.cal.get_file_date()
            self.cal.add_markings()
            text_box.load_file(self.file_date)

        def pics_button_frunction():
            text_button_frame.tkraise()
            self.widgets["PICSFRAME"].tkraise()

        def text_button_function():
            pics_button_frame.tkraise()
            self.widgets["TEXTFRAME"].tkraise()

        def last_func():
            # The function performed just before closing the window
            try:
                text_box = self.root.text_box
                text_box.save_data(self.file_date)
                text_box.save_spells_file()
            except Exception as e:

                error_msg = ("Error before closing\nwindow\nplease report:\n" +
                             str(e))
                pop_up = self.root.pop_up("Close", error_msg)
                pop_up.geometry('600x600')
                pop_up.update()

                file = "ErrorMSG--Journal.txt"

                with open(file, 'w') as f:
                    f.write(error_msg + "\n")
                    traceback_str = ''.join(
                        traceback.format_tb(e.__traceback__))
                    f.write(traceback_str)

                time.sleep(2)
            finally:
                self.root.destroy()

        cal_set()
        self.cal.make_today()
        # Label var
        self.day_var = tk.StringVar()
        self.day_var.set(self.cal.get_selected_formatted())

        # File date var
        self.file_date = ''
        self.file_date = self.cal.get_file_date()

        self.root.protocol('WM_DELETE_WINDOW', last_func)

        self.cal.var.trace('w', change_day)

        refresh_but = ttk.Button(self, text="Refresh")
        refresh_but.config(command=change_day)
        refresh_but.place()
        self.widgets["REF"] = refresh_but

        notes_but = ttk.Button(self, text="Notes")
        notes_but.config(command=notes_func)
        notes_but.place()
        self.widgets["NOTE"] = notes_but

        pics_button_frame = tk.Frame(self)
        pics_button_frame.place()

        text_button_frame = tk.Frame(self)
        text_button_frame.place()

        pics_button = ttk.Button(pics_button_frame, text="Pictures")
        pics_button.config(command=pics_button_frunction)
        pics_button.pack(fill=tk.BOTH, expand=True)
        self.widgets["PICSBUTTONFRAME"] = pics_button_frame

        text_button = ttk.Button(text_button_frame, text="Entry")
        text_button.config(command=text_button_function)
        text_button.pack(fill=tk.BOTH, expand=True)
        self.widgets["TEXTBUTTONFRAME"] = text_button_frame

        options_button = ttk.Button(self, text="Options")
        options_button.config(command=options_page)
        options_button.place()
        self.widgets["OPTS"] = options_button

        next_button = ttk.Button(self, text="Next")
        next_button.config(command=next_page)
        next_button.place()
        self.widgets["NEXT"] = next_button

        prev_button = ttk.Button(self, text="Prev")
        prev_button.config(command=prev_page)
        prev_button.place()
        self.widgets["PREV"] = prev_button

        today_button = ttk.Button(self, text="Today")
        today_button.config(command=self.cal.make_today)
        today_button.place()
        self.widgets["TDAY"] = today_button

        # This is the Dark purple bar that is created of design purposes
        frame = tk.Frame(self, bg=const.UPPER_BG)
        frame.place(x=0, y=0, w=const.DEFAULT_WIDTH // 2, h=100)
        self.widgets["UBG"] = frame

        label = tk.Label(frame, textvariable=self.day_var, wraplength=250)
        # comics----------------------------------------------------------
        label.config(bg=const.UPPER_BG, font=const.DATE_FONT, fg='white')
        label.place(x=10, y=40)
        self.widgets["DATE"] = label

        text_button_function()
        set_notepad()

    def resize_widgets(self, w, h):
        # Right-side
        wrap = w * 0.4

        x_percentage = 45
        x1r = x_percentage/100
        x2r = 1 - x1r

        y1r = 0.2
        y2r = 0.6
        y3r = 0.2

        th = 0.04  # today button ratio
        tw = 0.1

        self.widgets["TEXTFRAME"].place(
            x=w * x1r, y=0,
            w=int(w * x2r),
            h=int(h)
        )
        self.widgets["PICSFRAME"].place(
            x=w * x1r, y=0,
            w=int(w * x2r),
            h=int(h)
        )

        self.widgets["PICTURES"].resize(w=int(w * x2r), h=int(h))

        # with respect to frame
        self.widgets["TEXT"].place(
            x=0, y=0,
            w=int(w * x2r) - 15,
            h=int(h)
        )
        self.widgets["SCROLL"].place(x=int(w * x2r) - 15, y=0, h=h)

        # Left-side
        self.widgets["UBG"].place(x=0, y=0,
                                  w=int(w * x1r),
                                  h=int(h * y1r))
        df = const.DATE_FONT
        self.widgets["DATE"].config(
            fg="white",
            wraplength=wrap,
            font=(df[0],
                  int(df[1] * (w + h) / 2 * 0.0015) + 2)
        )

        self.widgets["DATE"].place(x=0, y=0,
                                   w=int(w * x1r),
                                   h=int(h * y1r))

        self.widgets["TDAY"].place(x=(w * x1r) - (w * tw) - (10),
                                   y=(h * 0.2) + (2),
                                   w=int(w * tw),
                                   h=int(h * th))
        buf = 10
        self.widgets["CAL"].place(x=buf / 2, y=(h * (y1r + th + 0.01)),
                                  w=int(w * x1r) - buf,
                                  h=int(h * (y2r - (th + 0.01))))

        width_buttons = int((((w * x1r) / 3)*0.9))
        height_buttons = int(h * (y3r / 2) - 10)

        math = ((w * x1r) / 2) - ((w * x1r) * 0.9 / 2) - (buf / 2)
        self.widgets["REF"].place(
            x=math, y=(h * (y2r + y1r)) + (buf / 2),
            w=width_buttons,
            h=height_buttons
        )

        math = math + width_buttons + (buf/2)
        self.widgets["NOTE"].place(
            x=math, y=(h * (y2r + y1r)) + (buf / 2),
            w=width_buttons,
            h=height_buttons
        )

        math = math + width_buttons + (buf/2)
        self.widgets["PICSBUTTONFRAME"].place(
            x=math, y=(h * (y2r + y1r)) + (buf/2),
            w=width_buttons,
            h=height_buttons
        )
        self.widgets["TEXTBUTTONFRAME"].place(
            x=math, y=(h * (y2r + y1r)) + (buf/2),
            w=width_buttons,
            h=height_buttons
        )

        math = ((w * x1r) / 2) - (w * x1r * 0.5) / 2
        self.widgets["OPTS"].place(x=math,
                                   y=(h * (y2r + y1r) +
                                      (h * (y3r / 2) - 10)) + (buf),
                                   w=int(w * x1r * 0.5),
                                   h=int(h * (y3r / 2) - 10))
        self.widgets["PREV"].place(x=math - buf/2 - (w * x1r * 0.15),
                                   y=(h * (y2r + y1r) +
                                      (h * (y3r / 2) - 10)) + (buf),
                                   w=int(w * x1r * 0.15),
                                   h=int(h * (y3r / 2) - 10))
        self.widgets["NEXT"].place(x=math + buf/2 + (w * x1r * 0.5),
                                   y=(h * (y2r + y1r) +
                                      (h * (y3r / 2) - 10)) + (buf),
                                   w=int(w * x1r * 0.15),
                                   h=int(h * (y3r / 2) - 10))


class OptionsPage(tk.Frame):

    page_name = "OptionsPage"

    def __init__(self, main_frame, root):
        tk.Frame.__init__(self, main_frame)
        button = ttk.Button(
            self,
            text="Back",
            command=lambda: root.show_frame(MainPage)
        )
        button.place(x=400 - 100, y=600 - 75, h=50, w=200)

        self.root = root
        self.widgets = {}
        self.widgets["OPTS_BACK"] = button

        self.set_options_page()

    def make_options(self):

        def save_drive():
            def button_func():
                window.destroy()
                logger.log("Open to drive triggered")
                Open_drive.save_to_drive()

            window = SDE_TopLevel(self)

            for line in const.INSTRUCTIONS_SAVE_TO_DRIVE.split("\n"):
                instr = tk.Label(window, text=line)
                instr.config(font=const.FONT_BOLD, bg=const.BASE_COLOR,
                             fg='white', anchor="w")
                instr.pack(fill=tk.X)
            ttk.Button(window, text='  OK  ',
                       command=button_func).pack(pady=5)

            window.set_window()

        def export():

            folder = tk_filedialog.askdirectory()
            if folder != '' and file != ():
                logger.log(f"Writing to folder: {folder}")
                if os.path.exists(folder):
                    try:
                        logger.log("Starting the converge entries")
                        ConvergeEntries.write_new_file(
                            ConvergeEntries.SDE_files(),
                            function=enc.decrypt,
                            folder=folder,
                            code=self.root.user.code
                        )
                    except Exception as e:
                        traceback.print_exc()
                        self.root.pop_up("Close", str(e))
                    self.root.pop_up("DONE")

        def spell_check_opts():

            spells_dict = self.root.text_box.spells_dict

            def insert_spells():
                logger.log("Inserting spells")
                string = ''
                key_value = list(spells_dict.items())
                key_value.sort()
                for word, correction in key_value:
                    string += word + " ---> " + correction + "\n"

                spells_box.insert("end", string)

            def update_spells():
                logger.log("Update spells")

                data = spells_box.get('0.0', 'end')
                data = data.strip()

                # ["cant ---> can't\ndont ---> <don't>\n<i> ---> <I>\n
                # <ill> ---> <I'll>\n<im> ---> <I'm>\n<ive> ---> <I've>"]

                try:
                    data = data.split("\n")
                    spells_new_dict = {}

                    for spell_corrects in data:
                        if spell_corrects.count("--->") != 1:
                            raise Exception

                        spell_corrects = spell_corrects.split("--->")
                        spells_new_dict[spell_corrects[0].strip()
                                        ] = spell_corrects[1].strip()

                    self.root.text_box.spells_dict = spells_new_dict

                except Exception as e:
                    self.root.pop_up("Close", 'Wrong Format')

                spells_window.destroy()

            # Create the file here if not existing
            # Dont need to make a file if not necessary
            if not os.path.isfile(const.SPELL_CHECK_FILE):
                with open(const.SPELL_CHECK_FILE, 'wb') as f:
                    pickle.dump(spells_dict, f)

            spells_window = SDE_TopLevel(self)
            spells_window.geometry('350x450')
            spells_window.resizable(False, False)
            spells_window.set_window()

            s = tk.Scrollbar(spells_window, orient=tk.VERTICAL)
            # Setting a scroll bar in case needed
            spells_box = tk.Text(
                spells_window, wrap=tk.WORD, yscrollcommand=s.set)
            # The height and width is based on the font-size and not pixels
            # It has word wrap functionality added onto it.
            spells_box.config(font=const.TEXT_BOX_FONT)
            spells_box.place(x=5, y=5, w=350 - 30, h=400 - 10)
            spells_box.focus()
            s.config(command=spells_box.yview)
            # Setting what the scroll bar scrolls
            # The scroll bar is pointless if not set
            s.place(x=5 + 350 - 30, y=5, height=400 - 10)

            button = ttk.Button(spells_window, text='SAVE',
                                command=update_spells)
            button.place(x=5, y=405, w=340, h=40)

            insert_spells()
            spells_window.mainloop()

        def all_entries():
            logger.log("Listing all entries")

            def button_func():
                window.destroy()

            window = SDE_TopLevel(self)
            window.geometry('250x400')
            window.set_window()

            listbox = tk.Listbox(window)
            listbox.config(font=const.FONT_BOLD,
                           bg=const.BASE_COLOR,
                           fg='white')

            files = sde_utils.files_in_folder()
            for i in range(len(files)):
                files[i] = "#".join(files[i])

            files.sort()

            for i in range(len(files)):
                files[i] = " - ".join(reversed(files[i].split("#")))

            for i, file in enumerate(files):
                listbox.insert(i, file)

            listbox.place(x=10, y=10, w=230, h=350)

            ttk.Button(window, text='close', command=button_func).place(
                x=10, y=365, w=230)

            window.center()

        def change_username():
            new_user = userClass.User()

            def button_func():
                new_username_str = str(new_user.name_var.get())
                new_user.code_var.set("1978")
                new_user.update()
                # the code does not matter, just has to be valid
                if new_user.validate_values():
                    cur_path = os.getcwd()
                    os.chdir("../")
                    if not sde_utils.check_folder(new_user.foldername):
                        os.chdir(cur_path)
                        Change_pass_user.change_username(
                            new_user.foldername,
                            self.root.user.name
                        )
                        logger.log("Changed the user name")

                        self.root.user.name_var = new_user.name_var.get()
                        self.root.user.update()

                        win_pop.destroy()
                        self.root.pop_up("Done", label="")
                    else:
                        os.chdir(cur_path)
                        self.root.pop_up("Close", "User Already Exist")

            win_pop = SDE_TopLevel(self)
            win_pop.geometry('400x100')
            win_pop.set_window()

            tk.Label(win_pop, text="New Username :", font=const.FONT_BOLD,
                     bg=const.BASE_COLOR, fg='white').place(x=5, y=18)

            ent = tk.Entry(win_pop, textvariable=new_user.name_var)
            ent.place(x=160, y=20, w=225, h=25)

            ttk.Button(win_pop, text="Change",
                       command=button_func).place(x=90, y=60, w=225, h=30)

        def change_password():
            new_user = userClass.User()
            old_user = userClass.User()

            def r_u_sure():
                # Before confirming, check if old password is
                # correct and new one is valid

                cont = False
                new_user.name_var.set("TestUser")
                old_user.name_var.set("TestUser")
                new_user.update()
                old_user.update()
                if old_user.validate_values():
                    # The Username does'nt matter its just
                    # to validate the password
                    if old_user.password_check():
                        if new_user.validate_values():
                            cont = True

                if cont:
                    pop_up = SDE_TopLevel(window_pop)
                    pop_up.geometry('200x100')

                    confirm_but = ttk.Button(pop_up, text="Confirm",
                                             command=lambda:
                                             change_pass_ok(pop_up,
                                                            confirm_but,
                                                            new_user.code,
                                                            old_user.code))
                    confirm_but.pack()
                    pop_up.center()
                    pop_up.mainloop()

            def change_pass_ok(pop_up, confirm_but, new_code, old_code):
                confirm_but.destroy()
                label_var = tk.StringVar()
                label_var.set("Processing... Don't close")
                tk.Label(pop_up, textvariable=label_var).pack()
                mess_1 = []  # Could not copy
                mess_2 = []  # Copied but could not change

                for file_completed_number, file_name in (
                        Change_pass_user.change_password(new_code, old_code)):
                    if file_completed_number == -1:
                        mess_1.append(file_name)
                    if file_completed_number == -2:
                        mess_2.append(file_name)

                logger.log("Password changed for user")
                self.root.user.code_var.set(str(new_code))
                window_pop.destroy()
                self.root.pop_up("Done", label="Successfully Changed")

            window_pop = SDE_TopLevel(self)
            window_pop.geometry('400x150')
            window_pop.set_window()

            tk.Label(window_pop, text="Old Password :", font=const.FONT_BOLD,
                     bg=const.BASE_COLOR, fg='white').place(x=5, y=18)

            ent = tk.Entry(window_pop,
                           textvariable=old_user.code_var,
                           show="*")
            ent.place(x=160, y=20, w=225, h=25)

            tk.Label(window_pop, text="New Password :", font=const.FONT_BOLD,
                     bg=const.BASE_COLOR, fg='white').place(x=5, y=48 + 10)

            ent = tk.Entry(
                window_pop, textvariable=new_user.code_var, show="*")

            ent.place(x=160, y=50 + 10, w=225, h=25)

            ttk.Button(window_pop, text="Change", command=r_u_sure).place(
                x=90, y=100, w=225, h=30)

            window_pop.mainloop()

        buttons = [
            'Save to Drive',
            'Export',
            'Spell Check',
            'Show All Entries',
            'Change UserName',
            'Change Password'
        ]
        texts = [
            'Save files to drive as zip',
            'Export entries as text file',
            'Add/Remove to words to spell check',
            'Show all DATES with entries',
            'Change UserName of current user',
            'Change Password of current user',
        ]
        commands = [
            save_drive,
            export,
            spell_check_opts,
            all_entries,
            change_username,
            change_password
        ]

        self.widgets["OPTS_BUTS"] = []
        self.widgets["OPTS_TEXTS"] = []

        for i, button in enumerate(buttons):
            t_button = ttk.Button(self, text=button, command=commands[i])
            y = 100 + (i * 70)
            t_button.place(x=50, y=y, w=200, h=50)
            t_text = tk.Label(self, text=texts[i])
            t_text.config(bg=const.UPPER_BG,
                          font=const.OPTS_LABEL_FONT,
                          fg='white')
            t_text.place(x=275, y=y, w=500, h=50)
            self.widgets["OPTS_BUTS"].append(t_button)
            self.widgets["OPTS_TEXTS"].append(t_text)

    def set_options_page(self):

        label = tk.Label(self, text="Options Page",
                         bg=const.UPPER_BG, font=const.OPTS_FONT,
                         fg='white')
        label.place(x=245, y=10)
        self.widgets["OPTS_LABEL"] = label

        buttons = self.make_options()
        logger.log("Set options page")

    def resize_widgets(self, w, h):
        self.widgets["OPTS_LABEL"].place(x=0,
                                         y=0,
                                         w=w,
                                         h=h * 0.12)

        a = len(self.widgets["OPTS_BUTS"])
        for i in range(a):
            button = self.widgets["OPTS_BUTS"][i]
            label = self.widgets["OPTS_TEXTS"][i]
            y = ((1+i) * h // 8.5) + 10
            f1 = (
                const.OPTS_LABEL_FONT[0],
                int(const.OPTS_LABEL_FONT[1] *
                    (w + h) / 2 * 0.0015 - w // 1000) - 1
            )
            button.place(x=w * 0.05, y=y, w=w // 4, h=h // 12)
            label.config(bg=const.UPPER_BG, font=f1, fg='white')
            label.place(x=(w * 0.05) + (w // 4) + (15),
                        y=y, w=w // 1.6, h=h // 12)

        y = 100 + ((i + 1) * h // 8.5)
        self.widgets["OPTS_BACK"].place(
            x=w // 2 - (w // 3) // 2,
            y=y,
            w=w // 3,
            h=h // 12)


def main():
    logger.log("Starting Application")
    pages = [IntroPage, MainPage, OptionsPage]
    app = MainApp(pages=pages)
    app.mainloop()
