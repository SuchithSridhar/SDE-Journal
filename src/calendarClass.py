import tkcalendar
import tkinter as tk
from . import constants as const
from . import sde_utils
import datetime


class Calendar(tkcalendar.Calendar):
    def __init__(self, frame):
        self.var = tk.StringVar()

        kwargs_dict = {
            'font': const.CAL_FONT,
            'selectmode': 'day',
            'textvariable': self.var,
            'firstweekday': const.FIRST_WEEKDAY,
            'showweeknumbers': False,
            'background': const.CAL_BG,
            'headersbackground': const.CAL_TEXT_COLOR,
            'weekendforeground': 'black',
            'showothermonthdays': False,
            'othermonthforeground': '#bfbfbf',
            'othermonthbackground': '#d9d9d9',
            'othermonthweforeground': '#bfbfbf',
            'othermonthwebackground': '#d9d9d9'
        }

        tkcalendar.Calendar.__init__(self, frame, **kwargs_dict)

    def get_selected(self):
        # Returns the date selected on the calender widget
        var = self.selection_get()
        if var is None:
            raise Exception
        else:
            return var

    def get_selected_formatted(self):
        return self.get_selected().strftime("%d %B %Y, %A")

    def caldates(self):
        # x = datetime.datetime(2020, 5, 17)
        files = sde_utils.files_in_folder()

        dates = []
        for file in files:
            try:
                day = datetime.datetime(int(file[0]),
                                        int(file[1]),
                                        int(file[2]))
                dates.append(day)
            except Exception:
                continue

        return dates

    def add_markings(self):
        dates = self.caldates()
        self.calevent_remove("all")
        for date in dates:
            self.calevent_create(date, 'completed', 'done')

        self.tag_config('done', background='#58afd0', foreground='black')

    def today_date_num(self, option):
        # Get today's date in single number form
        today = datetime.date.today()
        if option == "m":
            num = today.strftime("%m")
        elif option == 'd':
            num = today.strftime("%d")
        elif option == 'y':
            num = today.strftime("%Y")
        else:
            raise TypeError

        return num

    def today_date(self):
        # Today's date in proper format
        today = datetime.date.today()
        d1 = today.strftime("%d %B %Y            %A")
        return d1

    def make_today(self):
        today = (self.today_date_num('m') + "/" +
                 self.today_date_num('d') + "/" +
                 self.today_date_num('y'))

        # Doing it 2x cause of some bug
        self.var.set(today)
        self.var.set(today)

    def get_file_date(self):
        var = self.var.get()
        var = var.split("/")
        # mm/dd/yy
        if len(var[2]) == 2:
            var[2] = "20"+var[2]

        if len(var[0]) == 1:
            var[0] = "0"+var[0]
        if len(var[1]) == 1:
            var[1] = "0"+var[1]

        var = f"{var[2]}-{var[0]}-{var[1]}"
        return var
