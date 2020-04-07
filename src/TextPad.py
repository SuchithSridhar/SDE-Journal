import pickle
import os
import tkinter as tk
from . import constants as const
from . import Encryption as enc


class Textpad(tk.Text):

    def __init__(self, frame, code, *args, **kwargs):
        tk.Text.__init__(self, frame, *args, **kwargs)
        self.frame = frame
        self.code = code
        self.load_spells_file()

    def load_spells_file(self):
        try:
            with open(const.SPELL_CHECK_FILE, 'rb') as file:
                self.spells_dict = pickle.load(file)
        except FileNotFoundError:
            self.spells_dict = const.SPELLS_DICT.copy()

    def save_spells_file(self):
        with open(const.SPELL_CHECK_FILE, 'wb') as pickel_out:
            pickle.dump(self.spells_dict, pickel_out)

    def save_data(self, file_date):
        data = self.get('0.0', 'end')
        # Get the text that has been entered into the box

        data = data.rstrip()
        data = self.spell_check(data)

        if data.strip() == "":
            # Don't save an empty file
            return None

        if data.strip().lower() == "delete":
            try:
                os.remove(file_date + ".SDE")
            except FileNotFoundError:
                pass
            return None

        data = enc.encrypt(data, int(self.code))
        # Encrypt the data before saving as a file

        with open(file_date + ".SDE", 'w') as file:
            file.write(data)

    def load_file(self, file):
        if ".SDE" not in file:
            file += ".SDE"

        self.delete(1.0, 'end')
        try:
            with open(file) as f:
                data = enc.decrypt(f.read(), int(self.code))
            self.insert('end', data)
        except FileNotFoundError:
            self.focus()
            return False
        else:
            self.focus()
            return True

    def spell_check(self, text):
        exceptions = '<>?/\\{}()"\'!@#$%^&*_+=|`~:;.,'
        lines = text.split("\n")
        first_word_caps = True
        next_word_caps = False
        for i in range(len(lines)):
            lines[i] = lines[i].split(" ")
            # now lines is a list all lines where each line is a list of words
            line = lines[i]
            if line == [""]:
                # Make the next line letter caps
                first_word_caps = True
                continue

            for index, word in enumerate(line):
                if word == "":
                    continue

                if word.isupper():
                    upper = True

                else:
                    upper = False

                original_word = word
                for j in exceptions:
                    word = word.strip(j)
                word_start = original_word.index(word)
                if first_word_caps:
                    make_title = True
                    first_word_caps = False
                    next_word_caps = False
                elif next_word_caps:
                    make_title = True
                    next_word_caps = False
                elif word.istitle():
                    make_title = True
                else:
                    make_title = False
                word = word.lower()

                try:
                    if word[0] == "i" and word[1] == "'":
                        i_cat = True
                    else:
                        i_cat = False
                except IndexError:
                    i_cat = False

                if word in self.spells_dict:
                    before_part = original_word[:word_start]
                    after_part = original_word[word_start + len(word):]
                    for item in ".;!?":
                        if item in before_part:
                            make_title = True

                    replacement = self.spells_dict[word]
                    if make_title:
                        replacement = replacement.capitalize()
                    line[index] = before_part + replacement + after_part
                else:
                    if make_title:
                        line[index] = line[index].capitalize()
                    elif upper:
                        line[index] = line[index].upper()
                    elif i_cat:
                        line[index] = line[index].capitalize()
                    else:
                        line[index] = line[index].lower()

                if line[index][-1] in ".;":
                    next_word_caps = True

        for i in range(len(lines)):
            lines[i] = " ".join(lines[i])
        new_text = "\n".join(lines)

        return new_text
