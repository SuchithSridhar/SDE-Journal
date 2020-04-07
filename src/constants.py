import os

BASE_COLOR = '#4d94ff'
TEXT_BASE_COLOR = BASE_COLOR
BASE_PATH = os.getcwd()
APPLICATION_NAME = "Journal SDE 1.5.0"
# Later used while saving the diary entries


# Fonts ---------
FONT = ("Verdana", 12)
FONT_BOLD = ("Verdana bold", 12)


DATE_FONT = ("Verdana", 17)

TEXT_BOX_FONT = FONT
OPTS_FONT = ("Verdana bold", 30)
OPTS_LABEL_FONT = ("Verdana bold", 14)

DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
MAIN_FOLDER = ".Diary_Entries-SDE"


# ----- Spell check dict ----

SPELL_CHECK_FILE = 'spellcheck.SDE'

SPELLS_DICT = {
    'i': 'I',
    "dont": "don't",
    "im": "I'm",
    "cant": "can't",
    'ill': "I'll",
    'ive': "I've"
}

UPPER_BG = '#0066ff'

EG_TEXT = '''potbnijeg8ufhvbivjsbdgof'''

INSTRUCTIONS_SAVE_TO_DRIVE = '''
1) The files in their encrypted version will be zipped
2) The folder in which the zip exists WILL BE OPENED
3) Google Drive Website will be opened
4) You have to upload the file MANUALLY to drive
'''

# Calendar Constants:
FONT = ("Verdana", 12)

CAL_BG = '#002966'
CAL_TEXT_COLOR = '#005ce6'
CAL_FONT = FONT
FIRST_WEEKDAY = "sunday"
