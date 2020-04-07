import os
import tkinter as tk
from . import Encryption as enc
from . import foldermanager as fm
from . import constants as const
from . import sdeExceptions
from . import sde_utils


class User:
    def __init__(self):
        self.name_var = tk.StringVar()
        self.code_var = tk.StringVar()
        self.name = ''
        self.code = ''
        self.foldername = ''

    def update(self):
        self.name = self.name_var.get()
        self.code = self.code_var.get()
        self.foldername = self.make_folder_name()

    def make_folder_name(self):
        return self.name + "-SDE"

    def check_entered_code(self):
        password = int(self.code)
        with open('datfile.SDE') as file:
            data = file.read()
        data = enc.decrypt(data, password)

        return (data == const.EG_TEXT)

    def password_check(self):

        try:
            open("datfile.SDE")
        except FileNotFoundError:
            raise sdeExceptions.DatfileNotFound
        else:
            return self.check_entered_code()

    def check_user(self):
        return sde_utils.check_folder(self.foldername)

    def validate_values(self):

        enc.make_code(self.code)
        # Raises WeakCodeError or AlphaCodeError - digits only in code

        # folder name cant contain :
        # /\<>:*?"|
        invalid_chr = '/\\<>:*?"|'

        for i in invalid_chr:
            if i in self.name:
                raise sdeExceptions.InvalidChars
                return False

        if len(self.name) < 4:
            raise sdeExceptions.SmallUsername

        if len(self.name) > 25:
            raise sdeExceptions.LongUsername

    def login_init(self):
        if self.check_user():
            with fm.FolderManager(self.foldername):
                # --- Check if the password is right ---
                if not self.password_check():
                    raise sdeExceptions.WrongPassword
        else:
            raise sdeExceptions.UserNotFound

    def signin_init(self):
        os.makedirs(self.foldername)
        with fm.FolderManager(self.foldername):
            with open("datfile.SDE", 'w') as file:
                file.write(enc.encrypt(const.EG_TEXT, int(self.code)))
